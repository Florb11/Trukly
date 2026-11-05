from html import unescape

from db_instance import db
from models.usuario_model import UsuarioModel
from services.notificacion_service import NotificacionService


def notificar_cancelacion_chofer(viaje, motivo):
    NotificacionService.crear(
        viaje.Chofer_Usuario_idUsuario,
        "Viaje cancelado",
        f"El viaje #{viaje.id_viaje} fue cancelado. Motivo: {unescape(motivo)}",
        "viaje_cancelado",
    )


def notificar_aceptacion_operador(viaje):
    chofer = db.session.get(UsuarioModel, viaje.Chofer_Usuario_idUsuario)
    nombre = (f"{chofer.nombre} {chofer.apellido}".strip() if chofer else "El chofer asignado")
    NotificacionService.crear(
        viaje.OperadorLogistico_Usuario_idUsuario,
        "Viaje aceptado",
        f"{unescape(nombre)} aceptó el viaje #{viaje.id_viaje}. Está pendiente de salida por QR.",
        "viaje_aceptado",
    )
