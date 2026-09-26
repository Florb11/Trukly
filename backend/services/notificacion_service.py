from datetime import datetime

from db_instance import db
from models.notificacion_model import NotificacionModel
from src.Notificacion import Notificacion


class NotificacionService:

    @staticmethod
    def crear(id_usuario, titulo, mensaje, tipo=None, fecha_hora=None):
        titulo = str(titulo or "").strip()[:100]
        mensaje = str(mensaje or "").strip()[:255]
        tipo = str(tipo).strip()[:45] if tipo is not None else None
        notificacion = Notificacion.crear_desde_datos({
            "id_usuario": id_usuario,
            "titulo": titulo,
            "mensaje": mensaje,
            "leida": False,
            "fecha_hora": fecha_hora or datetime.now(),
            "tipo": tipo,
        })

        if notificacion is None or not notificacion.validar_datos():
            raise ValueError("Los datos de la notificacion no son validos")

        return NotificacionService.agregar_a_sesion(notificacion)

    @staticmethod
    def crear_para_usuarios(ids_usuario, titulo, mensaje, tipo=None):
        return [
            NotificacionService.crear(id_usuario, titulo, mensaje, tipo)
            for id_usuario in dict.fromkeys(ids_usuario)
        ]

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
