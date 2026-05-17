from flask import Blueprint
from controllers.administrador_controller import (
    listar_administradores, obtener_administrador, crear_administrador)
administrador_routes = Blueprint("administrador_routes", __name__)

# ruta listar administradores
@administrador_routes.route("/api/administrador", methods=["GET"])
def ruta_listar_administradores():

    return listar_administradores()

# ruta obtener administrador por id
@administrador_routes.route("/api/administrador/<int:id_usuario>", methods=["GET"])
def ruta_obtener_administrador(id_usuario):

    return obtener_administrador(id_usuario)


@administrador_routes.route("/api/administrador", methods=["POST"])
def ruta_crear_administrador():
# llamo al controller para crear un administrador nuevo
    return crear_administrador()
