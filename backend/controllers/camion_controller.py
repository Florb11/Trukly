from flask import g, jsonify, request

from db_instance import db
from models.camion_model import CamionModel
from models.reporte_model import ReporteModel

from src.Camion import Camion
from src.ReporteFalla import ReporteFalla
from utils.auth_decorators import admin_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer


logger = get_app_logger()


class CamionController:

    @staticmethod
    def _sanitizar_datos_camion(datos):
        return InputSanitizer.sanitizar_campos(
            datos,
            campos_texto=[
                "matricula",
                "marca",
                "modelo",
                "estado",
            ],
            campos_enteros=["nroTanque"],
            campos_decimales=["capacidad_carga"],
        )

    @staticmethod
    def _crear_camion_clase(
        datos,
        id_camion=None,
        camion_db=None
    ):
        return Camion(
            id_camion,
            datos.get(
                "matricula",
                camion_db.matricula if camion_db else None
            ),
            datos.get(
                "marca",
                camion_db.marca if camion_db else None
            ),
            datos.get(
                "modelo",
                camion_db.modelo if camion_db else None
            ),
            datos.get(
                "capacidad_carga",
                camion_db.capacidad_carga if camion_db else None
            ),
            datos.get(
                "estado",
                camion_db.estado if camion_db else None
            ),
            datos.get(
                "nroTanque",
                camion_db.nroTanque if camion_db else None
            ),
        )

    @staticmethod
    def _aplicar_datos_camion(camion_db, camion_clase):
        camion_db.matricula = camion_clase.matricula
        camion_db.marca = camion_clase.marca
        camion_db.modelo = camion_clase.modelo
        camion_db.capacidad_carga = camion_clase.capacidad_carga
        camion_db.estado = camion_clase.estado
        camion_db.nroTanque = camion_clase.nroTanque

    @staticmethod
    def _contar_reportes_activos(id_camion):
        return (
            ReporteModel.query
            .filter(
                ReporteModel.Camion_id_camion == id_camion,
                ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
            )
            .count()
        )

    @staticmethod
    def _preparar_respuesta_camion(camion_db):
        datos_camion = camion_db.to_dict()
        reportes_activos = CamionController._contar_reportes_activos(
            camion_db.id_camion
        )

        datos_camion["reportes_activos"] = reportes_activos

        if (
            reportes_activos > 0
            and camion_db.estado == Camion.ESTADO_DISPONIBLE
        ):
            datos_camion["estado"] = Camion.ESTADO_EN_MANTENIMIENTO
            datos_camion["estado_guardado"] = camion_db.estado

        return datos_camion

    @staticmethod
    def _puede_usar_estado(camion_db, nuevo_estado):
        reportes_activos = CamionController._contar_reportes_activos(
            camion_db.id_camion
        )

        if (
            reportes_activos > 0
            and nuevo_estado == Camion.ESTADO_DISPONIBLE
        ):
            return False, (
                "No se puede marcar como disponible un camion con "
                "reportes activos. Activarlo debe dejarlo en mantenimiento"
            )

        return True, None

    @staticmethod
    @admin_required
    def listar_camiones():
        camiones = CamionModel.query.all()

        return jsonify({
            "camiones": [
                CamionController._preparar_respuesta_camion(camion)
                for camion in camiones
            ]
        }), 200

    @staticmethod
    @admin_required
    def obtener_camion(id_camion):
        camion = CamionModel.query.get(id_camion)

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        return jsonify({
            "camion": CamionController._preparar_respuesta_camion(camion)
        }), 200

    @staticmethod
    @admin_required
    def crear_camion():
        admin = g.admin_actual

        datos = CamionController._sanitizar_datos_camion(
            request.get_json(silent=True) or {}
        )

        camion_clase = CamionController._crear_camion_clase(datos)

        if not admin.registrar_camion(camion_clase):
            return jsonify({"mensaje": "Faltan datos obligatorios o hay datos invalidos"}), 400

        camion_existente = CamionModel.query.filter_by(
            matricula=camion_clase.matricula
        ).first()

        if camion_existente:
            return jsonify({"mensaje": "Ya existe un camion con esa matricula"}), 400

        nuevo_camion = CamionModel(
            matricula=camion_clase.matricula,
            marca=camion_clase.marca,
            modelo=camion_clase.modelo,
            capacidad_carga=camion_clase.capacidad_carga,
            estado=camion_clase.estado,
            nroTanque=camion_clase.nroTanque,
        )

        try:
            db.session.add(nuevo_camion)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo crear el camion")

            return jsonify({
                "mensaje": "No se pudo crear el camion"
            }), 500

        return jsonify({
            "mensaje": "Camion creado correctamente",
            "camion": nuevo_camion.to_dict(),
        }), 201

    @staticmethod
    @admin_required
    def modificar_camion(id_camion):
        admin = g.admin_actual

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = CamionController._sanitizar_datos_camion(
            request.get_json(silent=True) or {}
        )

        camion_clase = CamionController._crear_camion_clase(
            datos,
            camion_db.id_camion,
            camion_db
        )

        estado_permitido, mensaje_error = (
            CamionController._puede_usar_estado(
                camion_db,
                camion_clase.estado
            )
        )

        if not estado_permitido:
            return jsonify({"mensaje": mensaje_error}), 400

        if not admin.modificar_camion(camion_clase):
            return jsonify({"mensaje": "Faltan datos obligatorios o hay datos invalidos"}), 400

        camion_existente = CamionModel.query.filter_by(
            matricula=camion_clase.matricula
        ).first()

        if camion_existente and camion_existente.id_camion != id_camion:
            return jsonify({"mensaje": "Ya existe otro camion con esa matricula"}), 400

        CamionController._aplicar_datos_camion(
            camion_db,
            camion_clase
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo modificar el camion")

            return jsonify({
                "mensaje": "No se pudo modificar el camion"
            }), 500

        return jsonify({
            "mensaje": "Camion modificado correctamente",
            "camion": CamionController._preparar_respuesta_camion(camion_db),
        }), 200

    @staticmethod
    @admin_required
    def cambiar_estado_camion(id_camion):
        admin = g.admin_actual

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["estado"],
        )
        nuevo_estado = datos.get("estado")

        camion_clase = CamionController._crear_camion_clase(
            {},
            camion_db.id_camion,
            camion_db
        )

        if not admin.cambiar_estado_camion(camion_clase, nuevo_estado):
            return jsonify({"mensaje": "Estado invalido"}), 400

        estado_permitido, mensaje_error = (
            CamionController._puede_usar_estado(
                camion_db,
                camion_clase.estado
            )
        )

        if not estado_permitido:
            return jsonify({"mensaje": mensaje_error}), 400

        camion_db.estado = camion_clase.estado

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo modificar el estado del camion")

            return jsonify({
                "mensaje": "No se pudo modificar el estado del camion"
            }), 500

        return jsonify({
            "mensaje": "Estado del camion modificado correctamente",
            "camion": CamionController._preparar_respuesta_camion(camion_db),
        }), 200