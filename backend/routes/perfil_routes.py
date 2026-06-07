from flask import Blueprint, send_from_directory

from controllers.perfil_controller import PerfilController


perfil_routes = Blueprint("perfil_routes", __name__)


# ruta para obtener los datos del perfil del usuario logueado
@perfil_routes.route("/api/perfil", methods=["GET"])
def ruta_obtener_perfil():
    return PerfilController.obtener_perfil()


# ruta para modificar nombre, apellido y email
@perfil_routes.route("/api/perfil", methods=["PUT"])
def ruta_modificar_perfil():
    return PerfilController.modificar_perfil()


# ruta para cambiar la contrasena
@perfil_routes.route("/api/perfil/password", methods=["PUT"])
def ruta_cambiar_password():
    return PerfilController.cambiar_password()


# ruta para subir o cambiar la foto de perfil
@perfil_routes.route("/api/perfil/foto", methods=["POST"])
def ruta_subir_foto():
    return PerfilController.subir_foto()


# ruta para mostrar las fotos guardadas en el backend
@perfil_routes.route(
    "/uploads/perfiles/<path:nombre_archivo>",
    methods=["GET"]
)
def ruta_obtener_foto(nombre_archivo):
    return send_from_directory(
        PerfilController.CARPETA_PERFILES,
        nombre_archivo
    )