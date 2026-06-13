from flask import Blueprint
from controllers.operador_controller import OperadorController

operador_routes = Blueprint("operador_routes", __name__)


@operador_routes.route("/api/operador", methods=["GET"])
def ruta_listar_operadores():
    return OperadorController.listar_operadores()


@operador_routes.route("/api/operador/<int:id_usuario>", methods=["GET"])
def ruta_obtener_operador(id_usuario):
    return OperadorController.obtener_operador(id_usuario)


@operador_routes.route("/api/operador", methods=["POST"])
def ruta_crear_operador():
    return OperadorController.crear_operador()


@operador_routes.route("/api/operador/viajes", methods=["GET"])
def ruta_listar_viajes():
    return OperadorController.listar_viajes()


@operador_routes.route("/api/operador/viajes", methods=["POST"])
def ruta_crear_viaje():
    return OperadorController.crear_viaje()


@operador_routes.route("/api/operador/viajes/<int:id_viaje>/cancelar", methods=["PUT"])
def ruta_cancelar_viaje(id_viaje):
    return OperadorController.cancelar_viaje(id_viaje)