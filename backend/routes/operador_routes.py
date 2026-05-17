from flask import Blueprint
from controllers.operador_controller import (
    listar_operadores,
    obtener_operador,
    crear_operador,
)

operador_routes = Blueprint("operador_routes", __name__)


@operador_routes.route("/api/operador", methods=["GET"])
def ruta_listar_operadores():

    return listar_operadores()


@operador_routes.route("/api/operador/<int:id_usuario>", methods=["GET"])
def ruta_obtener_operador(id_usuario):

    return obtener_operador(id_usuario)


@operador_routes.route("/api/operador", methods=["POST"])
def ruta_crear_operador():

    return crear_operador()
