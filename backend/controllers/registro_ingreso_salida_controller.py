from datetime import datetime

from flask import g, jsonify

from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from models.viaje_model import ViajeModel
from src.RegistroIngresoSalida import RegistroIngresoSalida
from src.Usuario import Usuario
from src.Viaje import Viaje
from utils.auth_decorators import roles_required
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidacionDatos,
    ValidadorCompuesto,
)


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
        consulta = RegistroIngresoSalidaModel.query
        if g.usuario_actual.rol == Usuario.ROL_CHOFER:
            consulta = consulta.join(
                ViajeModel, ViajeModel.id_viaje == RegistroIngresoSalidaModel.Viaje_id_viaje
            ).filter(ViajeModel.Chofer_Usuario_idUsuario == g.usuario_actual.id_usuario)
        registros = consulta.all()

        return jsonify([registro.to_dict() for registro in registros])

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
        Usuario.ROL_CHOFER,
    )
    def obtener_registro(id_registro):
        consulta = RegistroIngresoSalidaModel.query.filter_by(id_registro=id_registro)
        if g.usuario_actual.rol == Usuario.ROL_CHOFER:
            consulta = consulta.join(
                ViajeModel, ViajeModel.id_viaje == RegistroIngresoSalidaModel.Viaje_id_viaje
            ).filter(ViajeModel.Chofer_Usuario_idUsuario == g.usuario_actual.id_usuario)
        registro = consulta.first()

        if registro is None:
            return jsonify({"mensaje": "Registro no encontrado"}), 404

        return jsonify(registro.to_dict())

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def crear_registro():
        return jsonify({
            "mensaje": "La creación manual de controles está deshabilitada. El chofer debe registrar la salida y el regreso mediante el QR del viaje."
        }), 409
