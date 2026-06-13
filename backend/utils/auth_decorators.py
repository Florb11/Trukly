from functools import wraps #wrapper es la funcion intermedia que se ejecuta antes del controller

from flask import g, jsonify
from flask_jwt_extended import jwt_required

from services.auth_service import AuthService


def roles_required(*roles_permitidos):
    # Decorador general para permitir uno o varios roles
    def decorador(funcion):

        @wraps(funcion)
        @jwt_required()
        def wrapper(*args, **kwargs):
            # Busca el usuario actual usando el token
            usuario = AuthService.obtener_usuario_model_actual()

            # Si no existe o no esta activo, no permite entrar
            if usuario is None:
                return (
                    jsonify({"mensaje": "No tenes permiso para realizar esta accion"}),
                    403,
                )

            # Lee el rol que viene guardado en el token
            rol_token = AuthService.obtener_rol_actual()

            # Valida tres cosas:
            # 1. Que el rol del token este permitido
            # 2. Que el rol de la BD este permitido
            # 3. Que el rol del token y el de la BD coincidan
            if (
                rol_token not in roles_permitidos
                or usuario.rol not in roles_permitidos
                or rol_token != usuario.rol
            ):
                return (
                    jsonify({"mensaje": "No tenes permiso para realizar esta accion"}),
                    403,
                )

            # Guarda el usuario en g para usarlo durante esta request
            g.usuario_actual = usuario

            # Si paso todas las validaciones, ejecuta la funcion original
            return funcion(*args, **kwargs)

        return wrapper

    return decorador


def obtener_admin_actual_desde_token():
    # Pide al AuthService el admin actual armado como objeto 
    return AuthService.obtener_admin_actual_desde_token()


def admin_required(funcion):
    # Decorador especifico para endpoints de admin

    @wraps(funcion)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Valida token, usuario activo, rol admin y datos de Administrador
        admin = obtener_admin_actual_desde_token()

        # Si no es admin valido, corta la request
        if admin is None:
            return (
                jsonify({"mensaje": "No tenes permiso para realizar esta accion"}),
                403,
            )

        # Guarda el admin en g para usarlo en el controller
        g.admin_actual = admin

        # Ejecuta la funcion original protegida
        return funcion(*args, **kwargs)

    return wrapper


def obtener_mecanico_actual_desde_token():
    # Pide al AuthService el mecanico actual armado como objeto 
    return AuthService.obtener_mecanico_actual_desde_token()


def mecanico_required(funcion):
    # Decorador especifico para endpoints de mecanico

    @wraps(funcion)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Valida token, usuario activo, rol mecanico y datos de Mecanico
        mecanico = obtener_mecanico_actual_desde_token()

        # Si no es mecanico valido, corta la request
        if mecanico is None:
            return (
                jsonify({"mensaje": "No tenes permiso para realizar esta accion"}),
                403,
            )

        # Guarda el mecanico en g para usarlo en el controller
        g.mecanico_actual = mecanico

        # Ejecuta la funcion original protegida
        return funcion(*args, **kwargs)

    return wrapper


def usuario_required(funcion):
    # Decorador para cualquier usuario logueado y activo

    @wraps(funcion)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Busca el usuario actual usando el token
        usuario = AuthService.obtener_usuario_model_actual()

        # Si el usuario no existe o no esta activo, corta
        if usuario is None:
            return (
                jsonify({"mensaje": "La sesion no corresponde a un usuario activo"}),
                401,
            )

        # Guarda el usuario en g para usarlo en el controller
        g.usuario_actual = usuario

        # Ejecuta la funcion original protegida
        return funcion(*args, **kwargs)
       
    return wrapper


def obtener_chofer_actual_desde_token():

        return AuthService.obtener_chofer_actual_desde_token()
    
def chofer_required(funcion):

        @wraps(funcion)
        @jwt_required()
        def wrapper(*args, **kwargs):
  
           chofer = obtener_chofer_actual_desde_token()

           if chofer is None:
            return (
                jsonify({"mensaje": "No tenés permiso para realizar esta acción"}),
                403,
            )
    
           g.chofer_actual = chofer

           return funcion(*args, **kwargs)

        return wrapper

      