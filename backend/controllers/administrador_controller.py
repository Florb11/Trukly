from flask import jsonify, request

from db_instance import db

from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel

from src.Usuario import Usuario
from services.auth_service import AuthService
from utils.auth_decorators import admin_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer


logger = get_app_logger()


class AdministradorController:

    @staticmethod
    @admin_required
    def listar_administradores():
        administradores = AdministradorModel.query.all()

        return jsonify([
            administrador.to_dict()
            for administrador in administradores
        ]), 200

    @staticmethod
    @admin_required
    def obtener_administrador(id_usuario):
        administrador = AdministradorModel.query.get(id_usuario)

        if administrador is None:
            return jsonify({
                "mensaje": "Administrador no encontrado"
            }), 404

        return jsonify(administrador.to_dict()), 200

    @staticmethod
    @admin_required
    def crear_administrador():
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["legajo"],
            campos_enteros=["Usuario_idUsuario"],
        )

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

        id_usuario = datos["Usuario_idUsuario"]

        if id_usuario is None:
            return jsonify({
                "mensaje": "Usuario_idUsuario no valido"
            }), 400

        legajo = datos["legajo"]

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
            logger.exception("No se pudo crear el administrador")

            return jsonify({
                "mensaje": "No se pudo crear el administrador"
            }), 500

        return jsonify({
            "mensaje": "Administrador creado correctamente",
            "administrador": nuevo_administrador.to_dict()
        }), 201

    @staticmethod
    def obtener_admin_actual():
        return AuthService.obtener_admin_actual_desde_token()
        