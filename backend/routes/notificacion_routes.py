from flask import Blueprint
from controllers.notificacion_controller import NotificacionController
from controllers.push_controller import PushController

notificacion_routes = Blueprint("notificacion_routes", __name__)


@notificacion_routes.route("/api/notificaciones/dispositivo", methods=["POST", "DELETE"])
def ruta_dispositivo_push():
    return PushController.dispositivo()


@notificacion_routes.route("/api/notificaciones", methods=["GET"])
def ruta_listar_mis_notificaciones():
    return NotificacionController.listar_mis_notificaciones()


@notificacion_routes.route("/api/notificaciones/<int:id_notificacion>/leida", methods=["PUT"])
def ruta_marcar_como_leida(id_notificacion):
    return NotificacionController.marcar_como_leida(id_notificacion)
