from flask import jsonify, request
from flask_jwt_extended import jwt_required

from db_instance import db
from models.camion_model import CamionModel

from controllers.administrador_controller import AdministradorController

from src.Camion import Camion


class CamionController:

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

        matricula = datos.get("matricula")
        marca = datos.get("marca")
        modelo = datos.get("modelo")
        capacidad_carga = datos.get("capacidad_carga")
        estado = datos.get("estado")
        nroTanque = datos.get("nroTanque")

        camion_clase = Camion(
            None,
            matricula,
            marca,
            modelo,
            capacidad_carga,
            estado,
            nroTanque,
        )

        if not admin.registrar_camion(camion_clase):
            return jsonify({"mensaje": "Faltan datos obligatorios o hay datos invalidos"}), 400

        camion_existente = CamionModel.query.filter_by(matricula=matricula).first()

        if camion_existente:
            return jsonify({"mensaje": "Ya existe un camion con esa matricula"}), 400

        nuevo_camion = CamionModel(
            matricula=matricula,
            marca=marca,
            modelo=modelo,
            capacidad_carga=capacidad_carga,
            estado=estado,
            nroTanque=nroTanque,
        )

        db.session.add(nuevo_camion)
        db.session.commit()

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

        matricula = datos.get("matricula")
        marca = datos.get("marca")
        modelo = datos.get("modelo")
        capacidad_carga = datos.get("capacidad_carga")
        estado = datos.get("estado")
        nroTanque = datos.get("nroTanque")

        camion_clase = Camion(
            camion_db.id_camion,
            matricula,
            marca,
            modelo,
            capacidad_carga,
            estado,
            nroTanque,
        )

        if not admin.modificar_camion(camion_clase):
            return jsonify({"mensaje": "Faltan datos obligatorios o hay datos invalidos"}), 400

        camion_existente = CamionModel.query.filter_by(matricula=matricula).first()

        if camion_existente and camion_existente.id_camion != id_camion:
            return jsonify({"mensaje": "Ya existe otro camion con esa matricula"}), 400

        camion_db.matricula = camion_clase.matricula
        camion_db.marca = camion_clase.marca
        camion_db.modelo = camion_clase.modelo
        camion_db.capacidad_carga = camion_clase.capacidad_carga
        camion_db.estado = camion_clase.estado
        camion_db.nroTanque = camion_clase.nroTanque

        db.session.commit()

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

        camion_clase = Camion(
            camion_db.id_camion,
            camion_db.matricula,
            camion_db.marca,
            camion_db.modelo,
            camion_db.capacidad_carga,
            camion_db.estado,
            camion_db.nroTanque,
        )

        if not admin.cambiar_estado_camion(camion_clase, nuevo_estado):
            return jsonify({"mensaje": "Estado invalido"}), 400

        camion_db.estado = camion_clase.estado

        db.session.commit()

        return jsonify({
            "mensaje": "Estado del camion modificado correctamente",
            "camion": camion_db.to_dict(),
        }), 200