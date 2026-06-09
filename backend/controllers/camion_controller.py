from flask import jsonify, request
from flask_jwt_extended import jwt_required

from db_instance import db
from models.camion_model import CamionModel

from controllers.administrador_controller import AdministradorController

from src.Camion import Camion


class CamionController:

    @staticmethod
    def _crear_camion_clase(
        datos,
        id_camion=None,
        camion_db=None
    ):
        return Camion(
            id_camion,
            datos.get(
                "matricula",
                camion_db.matricula if camion_db else None
            ),
            datos.get(
                "marca",
                camion_db.marca if camion_db else None
            ),
            datos.get(
                "modelo",
                camion_db.modelo if camion_db else None
            ),
            datos.get(
                "capacidad_carga",
                camion_db.capacidad_carga if camion_db else None
            ),
            datos.get(
                "estado",
                camion_db.estado if camion_db else None
            ),
            datos.get(
                "nroTanque",
                camion_db.nroTanque if camion_db else None
            ),
        )

    @staticmethod
    def _aplicar_datos_camion(camion_db, camion_clase):
        camion_db.matricula = camion_clase.matricula
        camion_db.marca = camion_clase.marca
        camion_db.modelo = camion_clase.modelo
        camion_db.capacidad_carga = camion_clase.capacidad_carga
        camion_db.estado = camion_clase.estado
        camion_db.nroTanque = camion_clase.nroTanque

    @staticmethod
    @jwt_required()
    def listar_camiones():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camiones = CamionModel.query.all()

        return jsonify({
            "camiones": [camion.to_dict() for camion in camiones]
        }), 200

    @staticmethod
    @jwt_required()
    def obtener_camion(id_camion):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camion = CamionModel.query.get(id_camion)

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        return jsonify({
            "camion": camion.to_dict()
        }), 200

    @staticmethod
    @jwt_required()
    def crear_camion():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        datos = request.get_json(silent=True) or {}

        camion_clase = CamionController._crear_camion_clase(datos)

        if not admin.registrar_camion(camion_clase):
            return jsonify({"mensaje": "Faltan datos obligatorios o hay datos invalidos"}), 400

        camion_existente = CamionModel.query.filter_by(
            matricula=camion_clase.matricula
        ).first()

        if camion_existente:
            return jsonify({"mensaje": "Ya existe un camion con esa matricula"}), 400

        nuevo_camion = CamionModel(
            matricula=camion_clase.matricula,
            marca=camion_clase.marca,
            modelo=camion_clase.modelo,
            capacidad_carga=camion_clase.capacidad_carga,
            estado=camion_clase.estado,
            nroTanque=camion_clase.nroTanque,
        )

        try:
            db.session.add(nuevo_camion)
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo crear el camion"
            }), 500

        return jsonify({
            "mensaje": "Camion creado correctamente",
            "camion": nuevo_camion.to_dict(),
        }), 201

    @staticmethod
    @jwt_required()
    def modificar_camion(id_camion):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = request.get_json(silent=True) or {}

        camion_clase = CamionController._crear_camion_clase(
            datos,
            camion_db.id_camion
        )

        if not admin.modificar_camion(camion_clase):
            return jsonify({"mensaje": "Faltan datos obligatorios o hay datos invalidos"}), 400

        camion_existente = CamionModel.query.filter_by(
            matricula=camion_clase.matricula
        ).first()

        if camion_existente and camion_existente.id_camion != id_camion:
            return jsonify({"mensaje": "Ya existe otro camion con esa matricula"}), 400

        CamionController._aplicar_datos_camion(
            camion_db,
            camion_clase
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo modificar el camion"
            }), 500

        return jsonify({
            "mensaje": "Camion modificado correctamente",
            "camion": camion_db.to_dict(),
        }), 200

    @staticmethod
    @jwt_required()
    def cambiar_estado_camion(id_camion):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = request.get_json(silent=True) or {}
        nuevo_estado = datos.get("estado")

        camion_clase = CamionController._crear_camion_clase(
            {},
            camion_db.id_camion,
            camion_db
        )

        if not admin.cambiar_estado_camion(camion_clase, nuevo_estado):
            return jsonify({"mensaje": "Estado invalido"}), 400

        camion_db.estado = camion_clase.estado

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo modificar el estado del camion"
            }), 500

        return jsonify({
            "mensaje": "Estado del camion modificado correctamente",
            "camion": camion_db.to_dict(),
        }), 200