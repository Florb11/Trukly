from flask import Blueprint
from controllers.auth_controller import AuthController

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/api/auth/registro", methods=["POST"])
def ruta_registrar_chofer():
    return AuthController.registrar_chofer()


@auth_routes.route("/api/auth/registro-firebase", methods=["POST"])
def ruta_registrar_chofer_firebase():
    return AuthController.registrar_chofer_firebase()


@auth_routes.route("/api/auth/login", methods=["POST"])
def ruta_login():
    return AuthController.login()


@auth_routes.route("/api/auth/firebase-login", methods=["POST"])
def ruta_login_firebase():
    return AuthController.login_firebase()
