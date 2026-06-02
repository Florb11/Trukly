from flask import Blueprint
from controllers.chofer_controller import ChoferController

chofer_routes = Blueprint("chofer_routes", __name__)


@chofer_routes.route("/api/choferes", methods=["GET"])
def ruta_listar_choferes():
# Llamo al método estático listar_choferes de la clase ChoferController
    return ChoferController.listar_choferes()


@chofer_routes.route("/api/choferes/<int:id_usuario>", methods=["GET"])
def ruta_obtener_chofer(id_usuario):
# Llamo al método estático obtener_chofer pasando el ID
    return ChoferController.obtener_chofer(id_usuario)


@chofer_routes.route("/api/choferes", methods=["POST"]) 
def ruta_crear_chofer():
# Llamo al controller para crear un chofer nuevo
    return ChoferController.crear_chofer()