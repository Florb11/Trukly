from datetime import datetime

from db_instance import db
from src.observer.EventListener import EventListener
from models.notificacion_model import NotificacionModel


class NotificacionReporteListener(EventListener):

    # se ejecuta cuando el EventManager avisa que ocurrio un evento
    def actualizar(self, datos):
        id_usuario = datos.get("id_usuario")
        titulo = datos.get("titulo")
        mensaje = datos.get("mensaje")
        tipo = datos.get("tipo")

        if not id_usuario or not titulo or not mensaje:
            return

        nueva_notificacion = NotificacionModel(
            Usuario_idUsuario=id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            leida=False,
            fecha_hora=datetime.now(),
            tipo=tipo,
        )

        db.session.add(nueva_notificacion)