from datetime import datetime

from flask import jsonify, request
from db_instance import db

from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from models.viaje_model import ViajeModel
from src.RegistroIngresoSalida import RegistroIngresoSalida
from src.Usuario import Usuario
from src.Viaje import Viaje
from utils.auth_decorators import roles_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidacionDatos,
    ValidadorCompuesto,
)


logger = get_app_logger()


class RegistroIngresoSalidaController:

    @staticmethod
    def _sanitizar_datos_registro(datos):
        return InputSanitizer.sanitizar_campos(
            datos,
            campos_texto=[
                "fecha_hora",
                "tipo_registro",
                "observacion",
            ],
            campos_enteros=["Viaje_id_viaje"],
        )

    @staticmethod
    def _convertir_fecha_hora(fecha_hora):
        if isinstance(fecha_hora, datetime):
            return fecha_hora

        try:
            return datetime.fromisoformat(str(fecha_hora))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _validar_fecha_hora(datos):
        if RegistroIngresoSalidaController._convertir_fecha_hora(
            datos.get("fecha_hora")
        ) is None:
            return False, "La fecha y hora no es valida"

        return True, None

    @staticmethod
    def _crear_validador_registro():
        return ValidadorCompuesto(
            [
                CampoObligatorio("fecha_hora"),
                CampoObligatorio("tipo_registro"),
                CampoObligatorio("Viaje_id_viaje"),
                ValidacionDatos(
                    RegistroIngresoSalidaController._validar_fecha_hora
                ),
            ]
        )

    @staticmethod
    def crear_objeto_viaje(viaje_model):
        if viaje_model is None:
            return None

        return Viaje(
            id_viaje=viaje_model.id_viaje,
            fecha_salida=viaje_model.fecha_salida,
            fecha_llegada=viaje_model.fecha_llegada,
            origen=viaje_model.origen,
            destino=viaje_model.destino,
            estado=viaje_model.estado,
            observaciones=viaje_model.observaciones,
            recorrido=viaje_model.recorrido,
            id_operador=(
                viaje_model.OperadorLogistico_Usuario_idUsuario
            ),
            id_chofer=viaje_model.Chofer_Usuario_idUsuario,
            id_camion=viaje_model.Camion_id_camion,
        )

    @staticmethod
    def crear_objeto_registro(registro_ingreso_salida_model, viaje=None):
        return RegistroIngresoSalida(
            id_registro=registro_ingreso_salida_model.id_registro,
            fecha_hora=registro_ingreso_salida_model.fecha_hora,
            tipo_registro=registro_ingreso_salida_model.tipo_registro,
            observacion=registro_ingreso_salida_model.observacion,
            id_viaje=registro_ingreso_salida_model.Viaje_id_viaje,
            viaje=viaje,
        )

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
        Usuario.ROL_CHOFER,
    )
    def listar_registros():
        registros = RegistroIngresoSalidaModel.query.all()

        return jsonify([registro.to_dict() for registro in registros])

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
        Usuario.ROL_CHOFER,
    )
    def obtener_registro(id_registro):
        registro = RegistroIngresoSalidaModel.query.get(id_registro)

        if registro is None:
            return jsonify({"mensaje": "Registro no encontrado"}), 404

        return jsonify(registro.to_dict())

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
        Usuario.ROL_CHOFER,
    )
    def crear_registro():
        datos = RegistroIngresoSalidaController._sanitizar_datos_registro(
            request.get_json(silent=True) or {}
        )

        validador = (
            RegistroIngresoSalidaController._crear_validador_registro()
        )
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        viaje_model = ViajeModel.query.get(datos["Viaje_id_viaje"])
        viaje = RegistroIngresoSalidaController.crear_objeto_viaje(
            viaje_model
        )

        if viaje is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        registro = RegistroIngresoSalida(
            id_registro=None,
            fecha_hora=RegistroIngresoSalidaController._convertir_fecha_hora(
                datos["fecha_hora"]
            ),
            tipo_registro=datos["tipo_registro"],
            observacion=datos.get("observacion"),
            id_viaje=None,
        )

        if not viaje.agregar_registro(registro):
            return jsonify({"mensaje": "No se pudo asociar el registro"}), 400

        if not registro.validar_datos():
            return jsonify({"mensaje": "Faltan datos obligatorios"}), 400

        nuevo_registro = RegistroIngresoSalidaModel(
            fecha_hora=registro.fecha_hora,
            tipo_registro=registro.tipo_registro,
            observacion=registro.observacion,
            Viaje_id_viaje=registro.id_viaje,
        )

        try:
            db.session.add(nuevo_registro)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo crear el registro")

            return jsonify({
                "mensaje": "No se pudo crear el registro"
            }), 500

        return jsonify({
            "mensaje": "Registro creado correctamente",
            "registro": nuevo_registro.to_dict(),
        }), 201
