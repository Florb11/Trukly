from flask import Blueprint
from controllers.auth_controller import AuthController

auth_routes = Blueprint("auth_routes", __name__)


# Ahora las rutas llaman a metodos de AuthController.
# Esto se cambio porque el controller paso de tener funciones sueltas a estar organizado como clase.
# Las rutas siguen solo conectando cada endpoint con la accion que corresponde.

@auth_routes.route("/api/auth/registro", methods=["POST"])
def ruta_registrar_chofer():
    return AuthController.registrar_chofer()


@auth_routes.route("/api/auth/login", methods=["POST"])
def ruta_login():
    return AuthController.login()