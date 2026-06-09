from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from db_instance import db
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel

from src.Notificacion import Notificacion
from src.Usuario import Usuario


class NotificacionController:

    @staticmethod
    def crear_objeto_notificacion(notificacion_model):
        return Notificacion(
            id_notificacion=notificacion_model.id_notificacion,
            Usuario_idUsuario=notificacion_model.Usuario_idUsuario,
            titulo=notificacion_model.titulo,
            mensaje=notificacion_model.mensaje,
            leida=notificacion_model.leida,
            fecha_hora=notificacion_model.fecha_hora,
            tipo=notificacion_model.tipo,
        )

    @staticmethod
    def actualizar_modelo_notificacion(
        notificacion_model,
        notificacion_clase
    ):
        notificacion_model.leida = notificacion_clase.leida

    @staticmethod
    def convertir_notificacion(notificacion_model):
        notificacion = (
            NotificacionController.crear_objeto_notificacion(
                notificacion_model
            )
        )

        usuario = UsuarioModel.query.get(notificacion.Usuario_idUsuario)

        datos = notificacion.to_dict()
        datos["usuario_destino"] = None

        if usuario is not None:
            datos["usuario_destino"] = {
                "id_usuario": usuario.id_usuario,
                "username": usuario.username,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "rol": usuario.rol,
            }

        return datos

    @staticmethod
    @jwt_required()
    def listar_mis_notificaciones():
        id_usuario = get_jwt_identity()
        datos_token = get_jwt()
        rol = datos_token.get("rol")

        if rol == Usuario.ROL_ADMIN:
            notificaciones = NotificacionModel.query.order_by(
                NotificacionModel.fecha_hora.desc()
            ).all()
        else:
            notificaciones = NotificacionModel.query.filter_by(
                Usuario_idUsuario=id_usuario
            ).order_by(NotificacionModel.fecha_hora.desc()).all()

        return jsonify({
            "notificaciones": [
                NotificacionController.convertir_notificacion(notificacion)
                for notificacion in notificaciones
            ]
        }), 200

    @staticmethod
    @jwt_required()
    def marcar_como_leida(id_notificacion):
        id_usuario = get_jwt_identity()
        datos_token = get_jwt()
        rol = datos_token.get("rol")

        notificacion_model = NotificacionModel.query.get(id_notificacion)

        if notificacion_model is None:
            return jsonify({
                "mensaje": "Notificacion no encontrada"
            }), 404

        notificacion = (
            NotificacionController.crear_objeto_notificacion(
                notificacion_model
            )
        )

        if not notificacion.marcar_como_leida(id_usuario, rol):
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

            return jsonify({
                "mensaje": "No se pudo marcar la notificacion como leida"
            }), 500

        return jsonify({
            "mensaje": "Notificacion marcada como leida",
            "notificacion": NotificacionController.convertir_notificacion(
                notificacion_model
            )
        }), 200