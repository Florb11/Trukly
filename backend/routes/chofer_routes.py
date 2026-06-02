from flask import Blueprint
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