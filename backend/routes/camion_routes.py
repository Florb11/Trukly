from flask import Blueprint
from controllers.camion_controller import CamionController

camion_routes = Blueprint("camion_routes", __name__)


@camion_routes.route("/api/admin/camiones", methods=["GET"])
def ruta_listar_camiones():
    return CamionController.listar_camiones()


@camion_routes.route("/api/admin/camiones/<int:id_camion>", methods=["GET"])
def ruta_obtener_camion(id_camion):
    return CamionController.obtener_camion(id_camion)


@camion_routes.route("/api/admin/camiones", methods=["POST"])
def ruta_crear_camion():
    return CamionController.crear_camion()


@camion_routes.route("/api/admin/camiones/<int:id_camion>", methods=["PUT"])
def ruta_modificar_camion(id_camion):
    return CamionController.modificar_camion(id_camion)


@camion_routes.route("/api/admin/camiones/<int:id_camion>/estado", methods=["PUT"])
def ruta_cambiar_estado_camion(id_camion):
    return CamionController.cambiar_estado_camion(id_camion)