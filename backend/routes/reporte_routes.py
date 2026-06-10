from flask import Blueprint
from controllers.reporte_controller import ReporteController

reporte_routes = Blueprint("reporte_routes", __name__)


@reporte_routes.route("/api/reportes", methods=["GET"])
def ruta_listar_reportes():
    return ReporteController.listar_reportes()


@reporte_routes.route("/api/reportes/<int:id_reporte>", methods=["GET"])
def ruta_obtener_reporte(id_reporte):
    return ReporteController.obtener_reporte(id_reporte)


@reporte_routes.route("/api/reportes", methods=["POST"])
def ruta_crear_reporte():
    return ReporteController.crear_reporte()


@reporte_routes.route("/api/reportes/<int:id_reporte>/estado", methods=["PUT"])
def ruta_cambiar_estado_reporte(id_reporte):
    return ReporteController.cambiar_estado_reporte(id_reporte)


@reporte_routes.route("/api/reportes/<int:id_reporte>/asignar-mecanico", methods=["PUT"])
def ruta_asignar_mecanico(id_reporte):
    return ReporteController.asignar_mecanico(id_reporte)