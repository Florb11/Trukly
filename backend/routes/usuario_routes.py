from flask import Blueprint

from controllers.usuario_controller import UsuarioController


usuario_routes = Blueprint("usuario_routes", __name__)


@usuario_routes.route("/api/usuarios", methods=["GET"])
def ruta_listar_usuarios():
    return UsuarioController.listar_usuarios()


@usuario_routes.route("/api/usuarios/<int:id_usuario>", methods=["GET"])
def ruta_obtener_usuario(id_usuario):
    return UsuarioController.obtener_usuario(id_usuario)