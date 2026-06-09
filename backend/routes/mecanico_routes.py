from flask import Blueprint
from controllers.mecanico_controller import MecanicoController

mecanico_routes = Blueprint("mecanico_routes", __name__)


@mecanico_routes.route("/api/mecanico/reportes", methods=["GET"])
def ruta_listar_reportes_asignados():
    return MecanicoController.listar_reportes_asignados()


@mecanico_routes.route("/api/mecanico/reportes/<int:id_reporte>/resolver", methods=["PUT"])
def ruta_resolver_reporte(id_reporte):
    return MecanicoController.resolver_reporte(id_reporte)


@mecanico_routes.route(
    "/api/mecanico/camiones/<int:id_camion>/mantenimiento",
    methods=["GET"]
)
def ruta_obtener_mantenimiento_camion(id_camion):
    return MecanicoController.obtener_mantenimiento_camion(id_camion)


@mecanico_routes.route("/api/mecanico/camiones-mantenimiento", methods=["GET"])
def ruta_listar_camiones_mantenimiento():
    return MecanicoController.listar_camiones_mantenimiento()
