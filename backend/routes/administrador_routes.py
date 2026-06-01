from flask import Blueprint
from controllers.administrador_controller import AdministradorController

administrador_routes = Blueprint("administrador_routes", __name__)

# Antes las rutas llamaban directamente a funciones sueltas del controller.
# Como ahora el controlador esta organizado como una clase, cada ruta llama al metodo correspondiente de AdministradorController.
# La ruta solo define el endpoint y delega la accion al controller.

# ruta listar administradores
@administrador_routes.route("/api/administrador", methods=["GET"])
def ruta_listar_administradores():
    return AdministradorController.listar_administradores()


# ruta obtener administrador por id
@administrador_routes.route("/api/administrador/<int:id_usuario>", methods=["GET"])
def ruta_obtener_administrador(id_usuario):
    return AdministradorController.obtener_administrador(id_usuario)


# ruta crear administrador
@administrador_routes.route("/api/administrador", methods=["POST"])
def ruta_crear_administrador():
    return AdministradorController.crear_administrador()


# ruta listar usuarios pendientes
@administrador_routes.route("/api/admin/usuarios-pendientes", methods=["GET"])
def ruta_listar_usuarios_pendientes():
    return AdministradorController.listar_usuarios_pendientes()


# ruta activar usuario
@administrador_routes.route("/api/admin/usuarios/<int:id_usuario>/activar", methods=["PUT"])
def ruta_activar_usuario(id_usuario):
    return AdministradorController.activar_usuario(id_usuario)


# ruta listar todos los usuarios
@administrador_routes.route("/api/admin/usuarios", methods=["GET"])
def ruta_listar_usuarios():
    return AdministradorController.listar_usuarios()


# ruta desactivar usuario
@administrador_routes.route("/api/admin/usuarios/<int:id_usuario>/desactivar", methods=["PUT"])
def ruta_desactivar_usuario(id_usuario):
    return AdministradorController.desactivar_usuario(id_usuario)

# ruta modificar usuario
@administrador_routes.route("/api/admin/usuarios/<int:id_usuario>", methods=["PUT"])
def ruta_modificar_usuario(id_usuario):
    return AdministradorController.modificar_usuario(id_usuario)

# ruta registrar usuario desde admin
@administrador_routes.route("/api/admin/usuarios", methods=["POST"])
def ruta_registrar_usuario():
    return AdministradorController.registrar_usuario()

#ruta para el resumen del dashboard de admin
@administrador_routes.route("/api/admin/dashboard/resumen", methods=["GET"])
def ruta_obtener_resumen_dashboard():
    return AdministradorController.obtener_resumen_dashboard()