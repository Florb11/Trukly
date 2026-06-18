from flask import Blueprint
from utils.auth_decorators import chofer_required
from controllers.chofer_controller import ChoferController

chofer_routes = Blueprint("chofer_routes", __name__)

@chofer_routes.route("/api/choferes", methods=["GET"])
def ruta_listar_choferes():
    return ChoferController.listar_choferes()

@chofer_routes.route("/api/choferes/<int:id_usuario>", methods=["GET"])
def ruta_obtener_chofer(id_usuario):
    return ChoferController.obtener_chofer(id_usuario)

@chofer_routes.route("/api/choferes", methods=["POST"]) 
def ruta_crear_chofer():
    return ChoferController.crear_chofer()

@chofer_routes.route("/api/choferes/mis-reportes", methods=["GET"])
def ruta_listar_reportes_propios():
    return ChoferController.listar_reportes_propios()

@chofer_routes.route("/api/choferes/mis-viajes", methods=["GET"])
def ruta_listar_viajes_propios():
    return ChoferController.listar_viajes_propios()

@chofer_routes.route("/api/choferes/estadisticas", methods=["GET"])
def ruta_estadisticas():
    return ChoferController.obtener_estadisticas()

@chofer_routes.route("/api/choferes/camiones", methods=["GET"])
@chofer_required
def ruta_listar_camiones_chofer():
    return ChoferController.listar_camiones()
@chofer_routes.route("/api/choferes/viajes/<int:id_viaje>/iniciar", methods=["PUT"])
def ruta_iniciar_viaje(id_viaje):
    return ChoferController.iniciar_viaje(id_viaje)

@chofer_routes.route("/api/choferes/viajes/<int:id_viaje>/finalizar", methods=["PUT"])
def ruta_finalizar_viaje(id_viaje):
    return ChoferController.finalizar_viaje(id_viaje)