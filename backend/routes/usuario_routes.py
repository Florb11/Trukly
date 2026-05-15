from flask import Blueprint
from controllers.usuario_controller import (
    listar_usuarios,
    obtener_usuario,
    crear_usuario
)

usuario_routes = Blueprint("usuario_routes", __name__)


@usuario_routes.route("/api/usuarios", methods=["GET"]) #GET /api/usuarios
def ruta_listar_usuarios():
    # llamo al controller para listar todos los usuarios
    return listar_usuarios()


@usuario_routes.route("/api/usuarios/<int:id_usuario>", methods=["GET"]) #GET /api/usuarios/1
def ruta_obtener_usuario(id_usuario):
    # llamo al controller para buscar un usuario por id
    return obtener_usuario(id_usuario)


@usuario_routes.route("/api/usuarios", methods=["POST"]) #POST /api/usuarios
def ruta_crear_usuario():
    # llamo al controller para crear un usuario nuevo
    return crear_usuario()