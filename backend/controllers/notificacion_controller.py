from flask import g, jsonify

from db_instance import db
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel

from src.Notificacion import Notificacion
from src.Usuario import Usuario
from utils.auth_decorators import usuario_required
from utils.app_logger import get_app_logger


logger = get_app_logger()


class NotificacionController:

    @staticmethod
    def crear_objeto_usuario(usuario_model):
        if usuario_model is None:
            return None

        datos_usuario = usuario_model.to_dict()
        datos_usuario["password"] = usuario_model.password

        return Usuario.crear_desde_datos(datos_usuario)

    @staticmethod
    def crear_objeto_notificacion(notificacion_model, usuario=None):
        if notificacion_model is None:
            return None

        return Notificacion.crear_desde_datos(
            {
                "id_notificacion": notificacion_model.id_notificacion,
                "id_usuario": notificacion_model.Usuario_idUsuario,
                "titulo": notificacion_model.titulo,
                "mensaje": notificacion_model.mensaje,
                "leida": notificacion_model.leida,
                "fecha_hora": notificacion_model.fecha_hora,
                "tipo": notificacion_model.tipo,
            },
            usuario=usuario,
        )

    @staticmethod
    def actualizar_modelo_notificacion(
        notificacion_model,
        notificacion_clase
    ):
        # copia cambios del dominio al modelo
        notificacion_model.leida = notificacion_clase.leida

    @staticmethod
    def convertir_notificacion(notificacion_model):
        # arma la respuesta de una notificacion
        usuario_model = UsuarioModel.query.get(
            notificacion_model.Usuario_idUsuario
        )

        usuario = NotificacionController.crear_objeto_usuario(usuario_model)

        notificacion = (
            NotificacionController.crear_objeto_notificacion(
                notificacion_model,
                usuario
            )
        )

        datos = notificacion.to_dict()
        datos["Usuario_idUsuario"] = datos.pop("id_usuario")
        datos["usuario_destino"] = None

        if usuario_model is not None:
            datos["usuario_destino"] = {
                "id_usuario": usuario_model.id_usuario,
                "username": usuario_model.username,
                "nombre": usuario_model.nombre,
                "apellido": usuario_model.apellido,
                "rol": usuario_model.rol,
            }

        return datos

    @staticmethod
    @usuario_required
    def listar_mis_notificaciones():
        # lista notificaciones del usuario logueado
        usuario_actual = g.usuario_actual
        id_usuario = usuario_actual.id_usuario
        rol = usuario_actual.rol

        if rol == Usuario.ROL_ADMIN:
            notificaciones = NotificacionModel.query.order_by(
                NotificacionModel.fecha_hora.desc()
            ).all()
        else:
            notificaciones = (
                NotificacionModel.query
                .filter_by(Usuario_idUsuario=id_usuario)
                .order_by(NotificacionModel.fecha_hora.desc())
                .all()
            )

        return jsonify({
            "notificaciones": [
                NotificacionController.convertir_notificacion(notificacion)
                for notificacion in notificaciones
            ]
        }), 200

    @staticmethod
    @usuario_required
    def marcar_como_leida(id_notificacion):
        # marca una notificacion como leida
        usuario_actual = NotificacionController.crear_objeto_usuario(
            g.usuario_actual
        )

        notificacion_model = NotificacionModel.query.get(id_notificacion)

        if notificacion_model is None:
            return jsonify({
                "mensaje": "Notificacion no encontrada"
            }), 404

        notificacion = (
            NotificacionController.crear_objeto_notificacion(
                notificacion_model,
                usuario_actual
            )
        )

        if notificacion is None:
            return jsonify({
                "mensaje": "No se pudo leer la notificacion"
            }), 400

        # la regla de permiso esta en Notificacion
        if not notificacion.marcar_como_leida_por(usuario_actual):
            return jsonify({
                "mensaje": "No tenes permisos para modificar esta notificacion"
            }), 403

        NotificacionController.actualizar_modelo_notificacion(
            notificacion_model,
            notificacion
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo marcar la notificacion como leida")

            return jsonify({
                "mensaje": "No se pudo marcar la notificacion como leida"
            }), 500

        return jsonify({
            "mensaje": "Notificacion marcada como leida",
            "notificacion": NotificacionController.convertir_notificacion(
                notificacion_model
            )
        }), 200