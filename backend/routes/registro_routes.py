from flask import Blueprint
from controllers.registro_controller import (
    listar_registros,
    obtener_registro,
    crear_registro,
)

registro_routes = Blueprint("registro_routes", __name__)


@registro_routes.route("/api/registro", methods=["GET"])
def ruta_listar_registros():

    return listar_registros()


@registro_routes.route("/api/registro/<int:id_registro>", methods=["GET"])
def ruta_obtener_registro(id_registro):

    return obtener_registro(id_registro)


@registro_routes.route("/api/registro", methods=["POST"])
def ruta_crear_registro():

    return crear_registro()