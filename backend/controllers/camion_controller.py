from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from db_instance import db
from models.camion_model import CamionModel
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel

from src.Administrador import Administrador
from src.Camion import Camion


class CamionController:

    @staticmethod
    def obtener_admin_actual():
        id_usuario = get_jwt_identity()
        datos_token = get_jwt()

        if datos_token.get("rol") != "admin":
            return None

        usuario = UsuarioModel.query.get(id_usuario)

        if usuario is None:
            return None

        admin_db = AdministradorModel.query.filter_by(
            Usuario_idUsuario=id_usuario
        ).first()

        if admin_db is None:
            return None

        admin = Administrador(
            usuario.id_usuario,
            usuario.username,
            usuario.email,
            usuario.password,
            usuario.nombre,
            usuario.apellido,
            usuario.estado,
            usuario.rol,
            admin_db.legajo,
        )

        return admin

    @staticmethod
    @jwt_required()
    def listar_camiones():
        admin = CamionController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camiones = CamionModel.query.all()

        return jsonify({
            "camiones": [camion.to_dict() for camion in camiones]
        }), 200

    @staticmethod
    @jwt_required()
    def obtener_camion(id_camion):
        admin = CamionController.obtener_admin_actual()

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
        admin = CamionController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        datos = request.get_json()

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
        admin = CamionController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = request.get_json()

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
        admin = CamionController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = request.get_json()
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