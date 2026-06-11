from flask import Blueprint
from controllers.registro_ingreso_salida_controller import (
    RegistroIngresoSalidaController
)

registro_ingreso_salida_routes = Blueprint(
    "registro_ingreso_salida_routes",
    __name__
)


@registro_ingreso_salida_routes.route(
    "/api/registros-ingreso-salida",
    methods=["GET"]
)
def ruta_listar_registros_ingreso_salida():

    return RegistroIngresoSalidaController.listar_registros()


@registro_ingreso_salida_routes.route(
    "/api/registros-ingreso-salida/<int:id_registro>",
    methods=["GET"]
)
def ruta_obtener_registro_ingreso_salida(id_registro):

    return RegistroIngresoSalidaController.obtener_registro(id_registro)


@registro_ingreso_salida_routes.route(
    "/api/registros-ingreso-salida",
    methods=["POST"]
)
def ruta_crear_registro_ingreso_salida():

    return RegistroIngresoSalidaController.crear_registro()