from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import jwt_required

from services.auth_service import AuthService


def roles_required(*roles_permitidos):
    def decorador(funcion):
        @wraps(funcion)
        @jwt_required()
        def wrapper(*args, **kwargs):
            rol = AuthService.obtener_rol_actual()

            if rol not in roles_permitidos:
                return jsonify({
                    "mensaje": "No tenes permiso para realizar esta accion"
                }), 403

            return funcion(*args, **kwargs)

        return wrapper

    return decorador


def obtener_admin_actual_desde_token():
    return AuthService.obtener_admin_actual_desde_token()


def admin_required(funcion):
    @wraps(funcion)
    @jwt_required()
    def wrapper(*args, **kwargs):
        admin = obtener_admin_actual_desde_token()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        g.admin_actual = admin

        return funcion(*args, **kwargs)

    return wrapper


def obtener_mecanico_actual_desde_token():
    return AuthService.obtener_mecanico_actual_desde_token()


def mecanico_required(funcion):
    @wraps(funcion)
    @jwt_required()
    def wrapper(*args, **kwargs):
        mecanico = obtener_mecanico_actual_desde_token()

        if mecanico is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        g.mecanico_actual = mecanico

        return funcion(*args, **kwargs)

    return wrapper


def usuario_required(funcion):
    @wraps(funcion)
    @jwt_required()
    def wrapper(*args, **kwargs):
        usuario = AuthService.obtener_usuario_model_actual()

        if usuario is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        g.usuario_actual = usuario

        return funcion(*args, **kwargs)

    return wrapper
