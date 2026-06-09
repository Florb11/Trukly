from datetime import datetime

from db_instance import db
from src.observer.EventListener import EventListener
from models.notificacion_model import NotificacionModel
from src.Notificacion import Notificacion


class NotificacionReporteListener(EventListener):

    # se ejecuta cuando el EventManager avisa que ocurrio un evento
    def actualizar(self, datos):
        id_usuario = datos.get("id_usuario")
        titulo = datos.get("titulo")
        mensaje = datos.get("mensaje")
        tipo = datos.get("tipo")

        notificacion = Notificacion(
            id_notificacion=None,
            Usuario_idUsuario=id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            leida=False,
            fecha_hora=datetime.now(),
            tipo=tipo,
        )

        if not notificacion.validar_datos():
            return

        nueva_notificacion = NotificacionModel(
            Usuario_idUsuario=notificacion.Usuario_idUsuario,
            titulo=notificacion.titulo,
            mensaje=notificacion.mensaje,
            leida=notificacion.leida,
            fecha_hora=notificacion.fecha_hora,
            tipo=notificacion.tipo,
        )

        db.session.add(nueva_notificacion)