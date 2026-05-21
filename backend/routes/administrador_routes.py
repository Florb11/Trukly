from flask import Blueprint
from controllers.administrador_controller import (
    listar_administradores,
    obtener_administrador,
    crear_administrador,
    listar_usuarios_pendientes,
    activar_usuario,
    listar_usuarios,
    desactivar_usuario,
)

administrador_routes = Blueprint("administrador_routes", __name__)


# ruta listar administradores
@administrador_routes.route("/api/administrador", methods=["GET"])
def ruta_listar_administradores():
    return listar_administradores()


# ruta obtener administrador por id
@administrador_routes.route("/api/administrador/<int:id_usuario>", methods=["GET"])
def ruta_obtener_administrador(id_usuario):
    return obtener_administrador(id_usuario)


# ruta crear administrador
@administrador_routes.route("/api/administrador", methods=["POST"])
def ruta_crear_administrador():
    return crear_administrador()


# ruta listar usuarios pendientes
@administrador_routes.route("/api/admin/usuarios-pendientes", methods=["GET"])
def ruta_listar_usuarios_pendientes():
    return listar_usuarios_pendientes()


# ruta activar usuario
@administrador_routes.route("/api/admin/usuarios/<int:id_usuario>/activar", methods=["PUT"])
def ruta_activar_usuario(id_usuario):
    return activar_usuario(id_usuario)

#ruta listar usuarios todos 
@administrador_routes.route("/api/admin/usuarios", methods=["GET"])
def ruta_listar_usuarios():
    return listar_usuarios()
#ruta desactivar usuario
@administrador_routes.route("/api/admin/usuarios/<int:id_usuario>/desactivar", methods=["PUT"])
def ruta_desactivar_usuario(id_usuario):
    return desactivar_usuario(id_usuario)