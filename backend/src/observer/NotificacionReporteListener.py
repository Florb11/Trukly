from datetime import datetime

from src.observer.EventListener import EventListener
from src.Notificacion import Notificacion


class NotificacionReporteListener(EventListener):

    def __init__(self, guardar_notificacion=None):
        self.guardar_notificacion = guardar_notificacion

    # se ejecuta cuando el EventManager avisa que ocurrio un evento
    def actualizar(self, datos):
        id_usuario = datos.get("id_usuario")
        titulo = datos.get("titulo")
        mensaje = datos.get("mensaje")
        tipo = datos.get("tipo")

        notificacion = Notificacion.crear_desde_datos(
            {
                "id_usuario": id_usuario,
                "titulo": titulo,
                "mensaje": mensaje,
                "leida": False,
                "fecha_hora": datetime.now(),
                "tipo": tipo,
            }
        )

        if not notificacion.validar_datos():
            return

        if self.guardar_notificacion is not None:
            self.guardar_notificacion(notificacion)