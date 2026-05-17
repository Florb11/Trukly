from flask import Blueprint
from controllers.mecanico_controller import (
    listar_mecanicos,
    obtener_mecanico,
    crear_mecanico,
)

mecanico_routes = Blueprint("mecanico_routes", __name__)


@mecanico_routes.route("/api/mecanico", methods=["GET"])
def ruta_listar_mecanicos():

    return listar_mecanicos()


@mecanico_routes.route("/api/mecanico/<int:id_usuario>", methods=["GET"])
def ruta_obtener_mecanico(id_usuario):

    return obtener_mecanico(id_usuario)


@mecanico_routes.route("/api/mecanico", methods=["POST"])
def ruta_crear_mecanico():
    
    return crear_mecanico()
