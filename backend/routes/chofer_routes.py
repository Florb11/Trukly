from flask import Blueprint
from controllers.chofer_controller import (
    listar_choferes,
    obtener_chofer,
    crear_chofer
)

chofer_routes = Blueprint("chofer_routes", __name__)


@chofer_routes.route("/api/choferes", methods=["GET"])
def ruta_listar_choferes():

    return listar_choferes()


@chofer_routes.route("/api/choferes/<int:id_usuario>", methods=["GET"])
def ruta_obtener_chofer(id_usuario):

    return obtener_chofer(id_usuario)


@chofer_routes.route("/api/choferes", methods=["POST"]) 
def ruta_crear_chofer():
    # llamo al controller para crear un chofer nuevo
    return crear_chofer()