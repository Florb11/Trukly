from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from db_instance import db
from models.reporte_model import ReporteModel
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from src.ReporteFalla import ReporteFalla


class ReporteController:

    @staticmethod
    def validar_rol(roles_permitidos):
        datos_token = get_jwt()
        rol = datos_token.get("rol")

        return rol in roles_permitidos

    @staticmethod
    def crear_objeto_reporte(reporte_model):
        return ReporteFalla(
            id_reporte=reporte_model.id_reporte,
            fecha_hora=reporte_model.fecha_hora,
            descripcion=reporte_model.descripcion,
            estado=reporte_model.estado,
            Camion_id_camion=reporte_model.Camion_id_camion,
            Mecanico_Usuario_idUsuario=(
                reporte_model.Mecanico_Usuario_idUsuario
            ),
            Chofer_Usuario_idUsuario=(
                reporte_model.Chofer_Usuario_idUsuario
            ),
            nota_reparacion=reporte_model.nota_reparacion,
            fecha_resolucion=reporte_model.fecha_resolucion,
        )

    @staticmethod
    def actualizar_modelo_reporte(reporte_model, reporte_clase):
        reporte_model.estado = reporte_clase.estado
        reporte_model.Mecanico_Usuario_idUsuario = (
            reporte_clase.Mecanico_Usuario_idUsuario
        )
        reporte_model.nota_reparacion = reporte_clase.nota_reparacion
        reporte_model.fecha_resolucion = reporte_clase.fecha_resolucion

    @staticmethod
    @jwt_required()
    def listar_reportes():
        if not ReporteController.validar_rol(["admin", "operador"]):
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        reportes = ReporteModel.query.all()

        return jsonify({
            "reportes": [reporte.to_dict() for reporte in reportes]
        }), 200

    @staticmethod
    @jwt_required()
    def obtener_reporte(id_reporte):
        if not ReporteController.validar_rol(["admin", "operador", "chofer"]):
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        reporte = ReporteModel.query.get(id_reporte)

        if reporte is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos_token = get_jwt()
        id_usuario = int(get_jwt_identity())

        if datos_token.get("rol") == "chofer" and reporte.Chofer_Usuario_idUsuario != id_usuario:
            return jsonify({"mensaje": "No tenes permiso para ver este reporte"}), 403

        return jsonify({
            "reporte": reporte.to_dict()
        }), 200

    @staticmethod
    @jwt_required()
    def crear_reporte():
        if not ReporteController.validar_rol(["chofer"]):
            return jsonify({"mensaje": "Solo un chofer puede crear reportes"}), 403

        datos = request.get_json(silent=True) or {}
        id_chofer = int(get_jwt_identity())

        camion_id = datos.get("Camion_id_camion")
        descripcion = datos.get("descripcion")

        chofer = ChoferModel.query.filter_by(
            Usuario_idUsuario=id_chofer
        ).first()

        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404

        camion = CamionModel.query.get(camion_id)

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        reporte_clase = ReporteFalla(
            None,
            datetime.now(),
            descripcion,
            "pendiente",
            camion_id,
            None,
            id_chofer,
        )

        if not reporte_clase.validar_datos():
            return jsonify({"mensaje": "Faltan datos obligatorios"}), 400

        if not reporte_clase.validar_estado():
            return jsonify({"mensaje": "Estado invalido"}), 400

        nuevo_reporte = ReporteModel(
            fecha_hora=reporte_clase.fecha_hora,
            descripcion=reporte_clase.descripcion,
            estado=reporte_clase.estado,
            Camion_id_camion=reporte_clase.Camion_id_camion,
            Mecanico_Usuario_idUsuario=reporte_clase.Mecanico_Usuario_idUsuario,
            Chofer_Usuario_idUsuario=reporte_clase.Chofer_Usuario_idUsuario,
        )

        db.session.add(nuevo_reporte)
        db.session.commit()

        return jsonify({
            "mensaje": "Reporte creado correctamente",
            "reporte": nuevo_reporte.to_dict(),
        }), 201

    @staticmethod
    @jwt_required()
    def cambiar_estado_reporte(id_reporte):
        if not ReporteController.validar_rol(["admin", "operador"]):
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        reporte_db = ReporteModel.query.get(id_reporte)

        if reporte_db is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos = request.get_json(silent=True) or {}
        nuevo_estado = datos.get("estado")

        reporte_clase = ReporteController.crear_objeto_reporte(reporte_db)

        if not reporte_clase.cambiar_estado(nuevo_estado):
            return jsonify({"mensaje": "Estado invalido"}), 400

        ReporteController.actualizar_modelo_reporte(
            reporte_db,
            reporte_clase
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Estado del reporte modificado correctamente",
            "reporte": reporte_db.to_dict(),
        }), 200

    @staticmethod
    @jwt_required()
    def asignar_mecanico(id_reporte):
        if not ReporteController.validar_rol(["admin", "operador"]):
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        reporte_db = ReporteModel.query.get(id_reporte)

        if reporte_db is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos = request.get_json(silent=True) or {}
        id_mecanico = datos.get("Mecanico_Usuario_idUsuario")

        mecanico = MecanicoModel.query.filter_by(
            Usuario_idUsuario=id_mecanico
        ).first()

        if mecanico is None:
            return jsonify({"mensaje": "Mecanico no encontrado"}), 404

        reporte_clase = ReporteController.crear_objeto_reporte(reporte_db)

        if not reporte_clase.asignar_mecanico(id_mecanico):
            return jsonify({"mensaje": "No se pudo asignar el mecanico"}), 400

        ReporteController.actualizar_modelo_reporte(
            reporte_db,
            reporte_clase
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Mecanico asignado correctamente",
            "reporte": reporte_db.to_dict(),
        }), 200