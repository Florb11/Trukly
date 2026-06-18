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
    ValidadorCompuesto,
)


logger = get_app_logger()


class CamionController:

    @staticmethod
    def _sanitizar_datos_camion(datos):
        # limpia los datos que vienen del request
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
            datos_limpios["estado"] = str(
                datos_limpios["estado"]
            ).lower()

        return datos_limpios

    @staticmethod
    def _preparar_datos_camion(datos, camion_db=None):
        # arma los datos completos para crear o modificar
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
    def _crear_validador_camion():
        # valida que los campos existan en el request preparado
        return ValidadorCompuesto(
            [
                CampoObligatorio("matricula"),
                CampoObligatorio("marca"),
                CampoObligatorio("modelo"),
                CampoObligatorio("capacidad_carga"),
                CampoObligatorio("estado"),
                CampoObligatorio("nroTanque"),
            ]
        )

    @staticmethod
    def _validar_datos_basicos(datos):
        # valida campos obligatorios
        validador = CamionController._crear_validador_camion()
        return validador.validar(datos)

    @staticmethod
    def _validar_datos_dominio(admin, datos):
        # delega las reglas de camion a la clase
        return admin.validar_datos_camion(datos)

    @staticmethod
    def _aplicar_datos_camion(camion_db, camion_clase):
        # copia el objeto al modelo de BD
        camion_db.matricula = camion_clase.matricula
        camion_db.marca = camion_clase.marca
        camion_db.modelo = camion_clase.modelo
        camion_db.capacidad_carga = camion_clase.capacidad_carga
        camion_db.estado = camion_clase.estado
        camion_db.nroTanque = camion_clase.nroTanque

    @staticmethod
    def _obtener_reportes_activos(id_camion):
        # busca reportes activos asociados al camion
        return (
            ReporteModel.query
            .filter(
                ReporteModel.Camion_id_camion == id_camion,
                ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
            )
            .all()
        )

    @staticmethod
    def _preparar_respuesta_camion(camion_db):
        # arma la respuesta que se devuelve al front
        datos_camion = camion_db.to_dict()

        reportes_activos = CamionController._obtener_reportes_activos(
            camion_db.id_camion
        )

        datos_camion["reportes_activos"] = len(reportes_activos)

        if (
            len(reportes_activos) > 0
            and camion_db.estado == Camion.ESTADO_DISPONIBLE
        ):
            datos_camion["estado"] = Camion.ESTADO_EN_MANTENIMIENTO
            datos_camion["estado_guardado"] = camion_db.estado

        return datos_camion

    @staticmethod
    def _ajustar_estado_por_reportes_activos(camion_db, camion_clase):
        # ajusta el estado del objeto segun sus reportes
        reportes_activos = CamionController._obtener_reportes_activos(
            camion_db.id_camion
        )

        return camion_clase.ajustar_estado_por_reportes_activos(
            reportes_activos
        )

    @staticmethod
    @admin_required
    def listar_camiones():
        # lista todos los camiones
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
        # obtiene un camion por id
        camion = CamionModel.query.get(id_camion)

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        return jsonify({
            "camion": CamionController._preparar_respuesta_camion(camion)
        }), 200

    @staticmethod
    @admin_required
    def crear_camion():
        # recibe el request
        admin = g.admin_actual

        datos = CamionController._sanitizar_datos_camion(
            request.get_json(silent=True) or {}
        )

        # valida campos obligatorios
        datos_validos, mensaje_error = CamionController._validar_datos_basicos(
            datos
        )

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # valida reglas de negocio
        datos_validos, mensaje_error = CamionController._validar_datos_dominio(
            admin,
            datos
        )

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # el admin crea el objeto 
        camion_clase = admin.crear_camion(datos)

        if camion_clase is None:
            return jsonify({
                "mensaje": "Faltan datos obligatorios o hay datos invalidos"
            }), 400

        # valida unicidad en BD
        camion_existente = CamionModel.query.filter_by(
            matricula=camion_clase.matricula
        ).first()

        if camion_existente:
            return jsonify({
                "mensaje": "Ya existe un camion con esa matricula"
            }), 400

        # convierte el objeto ( clase) a modelo
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
        # recibe el request
        admin = g.admin_actual

        camion_db = CamionModel.query.get(id_camion)

        if camion_db is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        datos = CamionController._sanitizar_datos_camion(
            request.get_json(silent=True) or {}
        )

        # completa datos faltantes con los datos actuales
        datos_camion = CamionController._preparar_datos_camion(
            datos,
            camion_db
        )

        # valida campos obligatorios
        datos_validos, mensaje_error = CamionController._validar_datos_basicos(
            datos_camion
        )

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # valida reglas de negocio 
        datos_validos, mensaje_error = CamionController._validar_datos_dominio(
            admin,
            datos_camion
        )

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # el admin prepara el objeto modificado
        camion_clase = admin.preparar_modificacion_camion(
            datos_camion,
            camion_db.id_camion
        )

        if camion_clase is None:
            return jsonify({
                "mensaje": "Faltan datos obligatorios o hay datos invalidos"
            }), 400

        # aplica reglas por reportes activos
        CamionController._ajustar_estado_por_reportes_activos(
            camion_db,
            camion_clase
        )

        # valida que la matricula no este repetida
        camion_existente = CamionModel.query.filter_by(
            matricula=camion_clase.matricula
        ).first()

        if camion_existente and camion_existente.id_camion != id_camion:
            return jsonify({
                "mensaje": "Ya existe otro camion con esa matricula"
            }), 400

        # aplica los cambios al modelo
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
        # recibe el request
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

        # el controller solo valida que el campo venga
        if nuevo_estado is None or str(nuevo_estado).strip() == "":
            return jsonify({"mensaje": "El estado es obligatorio"}), 400

        # reconstruye el objeto desde la BD
        camion_clase = admin.preparar_modificacion_camion(
            CamionController._preparar_datos_camion(
                {},
                camion_db
            ),
            camion_db.id_camion
        )

        if camion_clase is None:
            return jsonify({
                "mensaje": "Faltan datos obligatorios o hay datos invalidos"
            }), 400

        # el admin intenta cambiar el estado en el objeto
        if not admin.cambiar_estado_camion(camion_clase, nuevo_estado):
            return jsonify({"mensaje": "Estado invalido"}), 400

        # aplica reglas por reportes activos
        CamionController._ajustar_estado_por_reportes_activos(
            camion_db,
            camion_clase
        )

        # persiste el nuevo estado
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