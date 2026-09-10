from flask import Blueprint

from controllers.contacto_controller import ContactoController


contacto_routes = Blueprint("contacto_routes", __name__)


@contacto_routes.route("/api/contacto", methods=["POST"])
def ruta_enviar_consulta():
    return ContactoController.enviar_consulta()
