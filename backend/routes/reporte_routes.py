from flask import Blueprint
from controllers.reporte_controller import (
    listar_reportes,
    obtener_reporte,
    crear_reporte,
)

reporte_routes = Blueprint("reporte_routes", __name__)


@reporte_routes.route("/api/reporte", methods=["GET"])
def ruta_listar_reportes():

    return listar_reportes()


@reporte_routes.route("/api/reporte/<int:id_reporte>", methods=["GET"])
def ruta_obtener_reporte(id_reporte):

    return obtener_reporte(id_reporte)


@reporte_routes.route("/api/reporte", methods=["POST"])
def ruta_crear_reporte():

    return crear_reporte()