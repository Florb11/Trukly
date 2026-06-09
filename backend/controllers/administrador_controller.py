from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required

from db_instance import db

from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel

from src.Administrador import Administrador
from src.Usuario import Usuario


class AdministradorController:

    @staticmethod
    @jwt_required()
    def listar_administradores():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        administradores = AdministradorModel.query.all()

        return jsonify([
            administrador.to_dict()
            for administrador in administradores
        ]), 200

    @staticmethod
    @jwt_required()
    def obtener_administrador(id_usuario):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        administrador = AdministradorModel.query.get(id_usuario)

        if administrador is None:
            return jsonify({
                "mensaje": "Administrador no encontrado"
            }), 404

        return jsonify(administrador.to_dict()), 200

    @staticmethod
    @jwt_required()
    def crear_administrador():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        datos = request.get_json(silent=True) or {}

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        if not datos.get("Usuario_idUsuario"):
            return jsonify({
                "mensaje": "Falta el campo Usuario_idUsuario"
            }), 400

        if not datos.get("legajo") or str(datos["legajo"]).strip() == "":
            return jsonify({
                "mensaje": "Falta el campo legajo"
            }), 400

        try:
            id_usuario = int(datos["Usuario_idUsuario"])
        except (TypeError, ValueError):
            return jsonify({
                "mensaje": "Usuario_idUsuario no valido"
            }), 400

        legajo = str(datos["legajo"]).strip()

        usuario = UsuarioModel.query.get(id_usuario)

        if usuario is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        if usuario.rol != Usuario.ROL_ADMIN:
            return jsonify({
                "mensaje": "El usuario no tiene rol admin"
            }), 400

        administrador_existente = AdministradorModel.query.get(
            id_usuario
        )

        if administrador_existente:
            return jsonify({
                "mensaje": "Este usuario ya tiene datos de administrador"
            }), 409

        nuevo_administrador = AdministradorModel(
            Usuario_idUsuario=id_usuario,
            legajo=legajo
        )

        try:
            db.session.add(nuevo_administrador)
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo crear el administrador"
            }), 500

        return jsonify({
            "mensaje": "Administrador creado correctamente",
            "administrador": nuevo_administrador.to_dict()
        }), 201

    @staticmethod
    def obtener_admin_actual():
        id_usuario = get_jwt_identity()
        datos_token = get_jwt()

        if not id_usuario:
            return None

        if datos_token.get("rol") != Usuario.ROL_ADMIN:
            return None

        try:
            id_usuario = int(id_usuario)
        except (TypeError, ValueError):
            return None

        usuario = UsuarioModel.query.get(id_usuario)

        if usuario is None:
            return None

        administrador = AdministradorModel.query.get(
            usuario.id_usuario
        )

        if administrador is None:
            return None

        return Administrador(
            usuario.id_usuario,
            usuario.username,
            usuario.email,
            usuario.password,
            usuario.nombre,
            usuario.apellido,
            usuario.estado,
            usuario.rol,
            administrador.legajo,
        )
        