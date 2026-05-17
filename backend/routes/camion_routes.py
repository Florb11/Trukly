from flask import Blueprint
from controllers.camion_controller import (
    listar_camiones,
    obtener_camion,
    crear_camion
)

camion_routes = Blueprint("camion_routes", __name__)


@camion_routes.route("/api/camiones", methods=["GET"])
def ruta_listar_camiones():

    return listar_camiones()


@camion_routes.route("/api/camiones/<int:id_camion>", methods=["GET"])
def ruta_obtener_camion(id_camion):

    return obtener_camion(id_camion)

@camion_routes.route("/api/camiones", methods=["POST"])
def ruta_crear_camion():

    return crear_camion()