from flask import Blueprint
from controllers.viaje_controller import (
    listar_viajes,
    obtener_viaje,
    crear_viaje,
)

viaje_routes = Blueprint("viaje_routes", __name__)

@viaje_routes.route("/api/viaje", methods=["GET"])
def ruta_listar_viajes():
    return listar_viajes()

@viaje_routes.route("/api/viaje/<int:id_viaje>")
def ruta_obtener_viaje(id_viaje):
    return obtener_viaje(id_viaje)

@viaje_routes.route("/api/viaje", methods=["POST"])
def ruta_crear_viaje():
    return crear_viaje()