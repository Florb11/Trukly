from flask import Blueprint
from controllers.auth_controller import AuthController

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/api/auth/registro", methods=["POST"])
def ruta_registrar_chofer():
    return AuthController.registrar_chofer()


@auth_routes.route("/api/auth/login", methods=["POST"])
def ruta_login():
    return AuthController.login()