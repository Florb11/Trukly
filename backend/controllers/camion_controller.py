from flask import g, jsonify, request

from db_instance import db
from models.camion_model import CamionModel
from models.reporte_model import ReporteModel

from src.Camion import Camion
from src.ReporteFalla import ReporteFalla
from utils.auth_decorators import admin_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidacionDatos,
    ValidadorCompuesto,
    ValorPermitido,
)


logger = get_app_logger()


class CamionController:

    @staticmethod
    def _sanitizar_datos_camion(datos):
        datos_limpios = InputSanitizer.sanitizar_campos(
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

        if datos_limpios.get("estado") is not None:
            datos_limpios["estado"] = str(datos_limpios["estado"]).lower()

        return datos_limpios

    @staticmethod
    def _preparar_datos_camion(datos, camion_db=None):
        return {
            "matricula": datos.get(
                "matricula",
                camion_db.matricula if camion_db else None
            ),
            "marca": datos.get(
                "marca",
                camion_db.marca if camion_db else None
            ),
            "modelo": datos.get(
                "modelo",
                camion_db.modelo if camion_db else None
            ),
            "capacidad_carga": datos.get(
                "capacidad_carga",
                camion_db.capacidad_carga if camion_db else None
            ),
            "estado": datos.get(
                "estado",
                camion_db.estado if camion_db else None
            ),
            "nroTanque": datos.get(
                "nroTanque",
                camion_db.nroTanque if camion_db else None
            ),
        }

    @staticmethod
    def _validar_capacidad_carga(datos):
        capacidad_carga = datos.get("capacidad_carga")

        if capacidad_carga is None:
            return False, "La capacidad de carga es obligatoria"

        if capacidad_carga <= 0:
            return False, "La capacidad de carga debe ser mayor a 0"

        return True, None

    @staticmethod
    def _validar_nro_tanque(datos):
        nro_tanque = datos.get("nroTanque")

        if nro_tanque is None:
            return False, "El numero de tanque es obligatorio"

        if nro_tanque <= 0:
            return False, "El numero de tanque debe ser mayor a 0"

        return True, None

    @staticmethod
    def _crear_validador_camion():
        return ValidadorCompuesto(
            [
                CampoObligatorio("matricula"),
                CampoObligatorio("marca"),
                CampoObligatorio("modelo"),
                CampoObligatorio("estado"),
                ValorPermitido(
                    "estado",
                    Camion.ESTADOS_VALIDOS,
                    "Estado"
                ),
                ValidacionDatos(CamionController._validar_capacidad_carga),
                ValidacionDatos(CamionController._validar_nro_tanque),
            ]
        )

    @staticmethod
    def _crear_camion_clase(
        datos,
        id_camion=None,
        camion_db=None
    ):
        datos_camion = CamionController._preparar_datos_camion(
            datos,
            camion_db
        )

        return Camion(
            id_camion,
            datos_camion["matricula"],
            datos_camion["marca"],
            datos_camion["modelo"],
            datos_camion["capacidad_carga"],
            datos_camion["estado"],
            datos_camion["nroTanque"],
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
    def _ajustar_estado_por_reportes_activos(camion_db, camion_clase):
        reportes_activos = CamionController._contar_reportes_activos(
            camion_db.id_camion
        )

        return camion_clase.ajustar_estado_por_reportes_activos(
            reportes_activos
        )

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

        validador = CamionController._crear_validador_camion()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

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

        datos_camion = CamionController._preparar_datos_camion(
            datos,
            camion_db
        )
        validador = CamionController._crear_validador_camion()
        datos_validos, mensaje_error = validador.validar(datos_camion)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        camion_clase = CamionController._crear_camion_clase(
            datos_camion,
            camion_db.id_camion,
            camion_db
        )

        CamionController._ajustar_estado_por_reportes_activos(
            camion_db,
            camion_clase
        )

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

        if nuevo_estado is not None:
            nuevo_estado = str(nuevo_estado).lower()

        validador = ValidadorCompuesto(
            [
                CampoObligatorio("estado"),
                ValorPermitido(
                    "estado",
                    Camion.ESTADOS_VALIDOS,
                    "Estado"
                ),
            ]
        )
        datos_validos, mensaje_error = validador.validar({
            "estado": nuevo_estado
        })

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        camion_clase = CamionController._crear_camion_clase(
            {},
            camion_db.id_camion,
            camion_db
        )

        if not admin.cambiar_estado_camion(camion_clase, nuevo_estado):
            return jsonify({"mensaje": "Estado invalido"}), 400

        CamionController._ajustar_estado_por_reportes_activos(
            camion_db,
            camion_clase
        )

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