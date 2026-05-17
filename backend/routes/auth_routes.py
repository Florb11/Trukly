from flask import Blueprint
from controllers.auth_controller import registrar_chofer

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/api/auth/registro", methods=["POST"])
def ruta_registrar_chofer():
    # llamo al controller para registrar un chofer pendiente
    return registrar_chofer()