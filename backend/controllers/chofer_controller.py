from flask import g, jsonify, request
from db_instance import db
from utils.app_logger import get_app_logger

from models.reporte_model import ReporteModel
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from utils.input_sanitizer import InputSanitizer
from utils.auth_decorators import chofer_required
from models.viaje_model import ViajeModel

logger = get_app_logger()


class ChoferController:

    @staticmethod
    def listar_choferes():
        choferes = ChoferModel.query.all()
        return jsonify([chofer.to_dict() for chofer in choferes])

    @staticmethod
    def obtener_chofer(id_usuario):
        chofer = ChoferModel.query.get(id_usuario)
        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404
        return jsonify(chofer.to_dict())

    @staticmethod
    def crear_chofer():
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["legajo", "vencimientoLicencia", "licencia"],
            campos_enteros=["Usuario_idUsuario"],
        )
        nuevo_chofer = ChoferModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["legajo"],
            vencimientoLicencia=datos["vencimientoLicencia"],
            licencia=datos["licencia"],
        )
        db.session.add(nuevo_chofer)
        db.session.commit()
        return jsonify({"mensaje": "Chofer creado correctamente", "chofer": nuevo_chofer.to_dict()}), 201

    @staticmethod
    @chofer_required
    def crear_reporte():
        chofer = g.chofer_actual
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["descripcion", "gravedad"],
            campos_enteros=["id_camion"],
        )
        id_camion = datos.get("id_camion")
        if not id_camion:
            return jsonify({"mensaje": "El id_camion es obligatorio"}), 400

        camion_model = CamionModel.query.get(id_camion)
        if not camion_model:
            return jsonify({"mensaje": "Camión no encontrado"}), 404

        camion = Camion.crear_desde_datos(camion_model.to_dict())
        if not camion.puede_entrar_en_mantenimiento():
            return jsonify({"mensaje": "El camión no puede reportar fallas en su estado actual"}), 400

        try:
            nuevo_reporte = ReporteFallaModel(
                descripcion=datos.get("descripcion"),
                gravedad=datos.get("gravedad"),
                estado="pendiente",
                Chofer_Usuario_idUsuario=chofer.id_usuario,
                Camion_id_camion=id_camion,
            )
            camion.marcar_en_mantenimiento()
            camion_model.estado = camion.estado
            db.session.add(nuevo_reporte)
            db.session.commit()
            return jsonify({"mensaje": "Reporte creado exitosamente. El camión pasó a mantenimiento."}), 201

        except Exception:
            db.session.rollback()
            logger.exception(f"Error al crear reporte del camión {id_camion} por el chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor al crear el reporte"}), 500

    @staticmethod
    @chofer_required
    def listar_reportes_propios():
        chofer = g.chofer_actual
        try:
            reportes = chofer.obtener_mis_reportes(ReporteModel.query)
            return jsonify([r.to_dict() for r in reportes]), 200
        except Exception:
            logger.exception(f"Error al listar reportes del chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
        

    @staticmethod
    @chofer_required
    def listar_viajes_propios():
        chofer = g.chofer_actual

        try:
            viajes = chofer.obtener_mis_viajes(ViajeModel.query)
            return jsonify([v.to_dict() for v in viajes]), 200
        except Exception:
            logger.exception(f"Error al listar viajes del chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
        
    @staticmethod
    @chofer_required
    def obtener_estadisticas():
        chofer = g.chofer_actual

        try:
            viajes = ViajeModel.query.filter_by(
                Chofer_Usuario_idUsuario=chofer.id_usuario
            ).all()

            total_viajes = len(viajes)
            viajes_pendientes = sum(1 for v in viajes if v.estado.lower() == "pendiente")
            viajes_en_curso = sum(1 for v in viajes if v.estado.lower() == "en curso")
            viajes_finalizados = sum(1 for v in viajes if v.estado.lower() == "finalizado")
            viajes_cancelados = sum(1 for v in viajes if v.estado.lower() == "cancelado")

            ultimos_viajes = ViajeModel.query.filter_by(
                Chofer_Usuario_idUsuario=chofer.id_usuario
            ).order_by(ViajeModel.id_viaje.desc()).limit(5).all()

            reportes = ReporteModel.query.filter_by(
                Chofer_Usuario_idUsuario=chofer.id_usuario
            ).all()

            reportes_pendientes = sum(1 for r in reportes if r.estado == "pendiente")
            reportes_en_revision = sum(1 for r in reportes if r.estado == "en revision")
            reportes_resueltos = sum(1 for r in reportes if r.estado == "resuelto")

            ultimos_reportes = ReporteModel.query.filter_by(
                Chofer_Usuario_idUsuario=chofer.id_usuario
            ).order_by(ReporteModel.id_reporte.desc()).limit(5).all()

            return jsonify({
                "resumen": {
                    "total_viajes": total_viajes,
                    "viajes_pendientes": viajes_pendientes,
                    "viajes_en_curso": viajes_en_curso,
                    "viajes_finalizados": viajes_finalizados,
                    "viajes_cancelados": viajes_cancelados,
                    "reportes_pendientes": reportes_pendientes,
                    "reportes_en_revision": reportes_en_revision,
                    "reportes_resueltos": reportes_resueltos,
                },
                "ultimos_viajes": [v.to_dict() for v in ultimos_viajes],
                "ultimos_reportes": [r.to_dict() for r in ultimos_reportes],
            }), 200

        except Exception:
            logger.exception(f"Error al obtener estadisticas del chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
    
    @staticmethod
    def listar_camiones():
        from models.camion_model import CamionModel
        camiones = CamionModel.query.all()
        return jsonify({
            "camiones": [c.to_dict() for c in camiones]
        }), 200