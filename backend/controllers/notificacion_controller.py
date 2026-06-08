from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from db_instance import db
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel


class NotificacionController:

    @staticmethod
    def convertir_notificacion(notificacion):
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

        if rol == "admin":
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

        notificacion = NotificacionModel.query.get(id_notificacion)

        if notificacion is None:
            return jsonify({"mensaje": "Notificación no encontrada"}), 404

        if rol != "admin" and str(notificacion.Usuario_idUsuario) != str(id_usuario):
            return jsonify({
                "mensaje": "No tenés permisos para modificar esta notificación"
            }), 403

        notificacion.leida = True
        db.session.commit()

        return jsonify({
            "mensaje": "Notificación marcada como leída",
            "notificacion": NotificacionController.convertir_notificacion(notificacion)
        }), 200