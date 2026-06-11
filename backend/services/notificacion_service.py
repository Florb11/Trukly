from db_instance import db
from models.notificacion_model import NotificacionModel


class NotificacionService:

    @staticmethod
    def agregar_a_sesion(notificacion):
        nueva_notificacion = NotificacionModel(
            Usuario_idUsuario=notificacion.id_usuario,
            titulo=notificacion.titulo,
            mensaje=notificacion.mensaje,
            leida=notificacion.leida,
            fecha_hora=notificacion.fecha_hora,
            tipo=notificacion.tipo,
        )

        db.session.add(nueva_notificacion)
        return nueva_notificacion