from flask import Blueprint
from controllers.viaje_controller import ViajeController

viaje_routes = Blueprint("viaje_routes", __name__)

# RUTAS GENERALES PROTEGIDAS

@viaje_routes.route("/api/viaje", methods=["GET"])
def ruta_listar_viajes():
    return ViajeController.listar_viajes()


@viaje_routes.route("/api/viaje/<int:id_viaje>", methods=["GET"])
def ruta_obtener_viaje(id_viaje):
    return ViajeController.obtener_viaje(id_viaje)


@viaje_routes.route("/api/viaje", methods=["POST"])
def ruta_crear_viaje():
    return ViajeController.crear_viaje()


# RUTAS ADMIN

@viaje_routes.route("/api/admin/viajes", methods=["GET"])
def ruta_listar_viajes_admin():
    return ViajeController.listar_viajes_admin()


@viaje_routes.route("/api/admin/viajes/<int:id_viaje>", methods=["GET"])
def ruta_obtener_viaje_admin(id_viaje):
    return ViajeController.obtener_viaje_admin(id_viaje)


@viaje_routes.route("/api/admin/viajes/<int:id_viaje>/cancelar", methods=["PUT"])
def ruta_cancelar_viaje_admin(id_viaje):
    return ViajeController.cancelar_viaje_admin(id_viaje)

