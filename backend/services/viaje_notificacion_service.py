from html import unescape

from services.notificacion_service import NotificacionService


def notificar_cancelacion_chofer(viaje, motivo):
    NotificacionService.crear(
        viaje.Chofer_Usuario_idUsuario,
        "Viaje cancelado",
        f"El viaje #{viaje.id_viaje} fue cancelado. Motivo: {unescape(motivo)}",
        "viaje_cancelado",
    )
