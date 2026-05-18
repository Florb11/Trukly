from flask import Blueprint
from controllers.auth_controller import registrar_chofer, login


auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/api/auth/registro", methods=["POST"])
def ruta_registrar_chofer():
    # llamo al controller para registrar un chofer pendiente
    return registrar_chofer()

@auth_routes.route("/api/auth/login", methods=["POST"])
def ruta_login():
    # llamo al controller para iniciar sesion
    return login()