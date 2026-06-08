from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.observer.EventManager import EventManager
from src.observer.NotificacionReporteListener import NotificacionReporteListener

from db_instance import db

from models.usuario_model import UsuarioModel
from models.mecanico_model import MecanicoModel
from models.reporte_model import ReporteModel

from src.Mecanico import Mecanico


class MecanicoController:

    @staticmethod
    def crear_objeto_mecanico(usuario_model, mecanico_model):
        return Mecanico(
            id_usuario=usuario_model.id_usuario,
            username=usuario_model.username,
            email=usuario_model.email,
            password=usuario_model.password,
            nombre=usuario_model.nombre,
            apellido=usuario_model.apellido,
            estado=usuario_model.estado,
            rol=usuario_model.rol,
            legajo=mecanico_model.legajo,
            especialidad=mecanico_model.especialidad,
            foto_perfil=usuario_model.foto_perfil,
        )

    @staticmethod
    def obtener_mecanico_actual():
        id_usuario = get_jwt_identity()
        datos_token = get_jwt()

        if datos_token.get("rol") != "mecanico":
            return None

        usuario_model = UsuarioModel.query.get(id_usuario)
        mecanico_model = MecanicoModel.query.get(id_usuario)

        if usuario_model is None or mecanico_model is None:
            return None

        return MecanicoController.crear_objeto_mecanico(
            usuario_model,
            mecanico_model
        )

    @staticmethod
    def listar_mecanicos():
        mecanicos = MecanicoModel.query.all()

        return jsonify([mecanico.to_dict() for mecanico in mecanicos]), 200

    @staticmethod
    def obtener_mecanico(id_usuario):
        mecanico = MecanicoModel.query.get(id_usuario)

        if mecanico is None:
            return jsonify({"mensaje": "Mecánico no encontrado"}), 404

        return jsonify(mecanico.to_dict()), 200

    @staticmethod
    def crear_mecanico():
        datos = request.get_json()

        nuevo_mecanico = MecanicoModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["Legajo"],
            especialidad=datos["Especialidad"],
        )

        db.session.add(nuevo_mecanico)
        db.session.commit()

        return jsonify(
            {
                "mensaje": "Mecánico creado correctamente",
                "mecanico": nuevo_mecanico.to_dict(),
            }
        ), 201

    @staticmethod
    @jwt_required()
    def listar_reportes_asignados():
        mecanico = MecanicoController.obtener_mecanico_actual()

        if mecanico is None:
            return jsonify({"mensaje": "No tenés permisos para ver estos reportes"}), 403

        reportes = ReporteModel.query.filter_by(
            Mecanico_Usuario_idUsuario=mecanico.id_usuario
        ).all()

        return jsonify(
            {
                "reportes": [reporte.to_dict() for reporte in reportes]
            }
        ), 200

    @staticmethod
    @jwt_required()
    def resolver_reporte(id_reporte):
        mecanico = MecanicoController.obtener_mecanico_actual()

        if mecanico is None:
            return jsonify({"mensaje": "No tenés permisos para resolver reportes"}), 403

        datos = request.get_json()
        nota_reparacion = datos.get("nota_reparacion")

        reporte = ReporteModel.query.get(id_reporte)

        if reporte is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        pudo_resolver = mecanico.resolver_reporte(reporte, nota_reparacion)

        if not pudo_resolver:
            return jsonify(
                {
                    "mensaje": "No podés resolver este reporte o falta la nota de reparación"
                }
            ), 400

        event_manager = EventManager()
        listener_notificacion = NotificacionReporteListener()

        event_manager.suscribir("reporte_resuelto", listener_notificacion)

        event_manager.notificar(
            "reporte_resuelto",
            {
                "id_usuario": reporte.Chofer_Usuario_idUsuario,
                "titulo": "Reporte resuelto",
                "mensaje": f"El reporte #{reporte.id_reporte} fue resuelto. Nota: {nota_reparacion}",
                "tipo": "reporte_resuelto",
            }
        )

        db.session.commit()

        return jsonify(
            {
                "mensaje": "Reporte marcado como resuelto",
                "reporte": reporte.to_dict(),
            }
        ), 200