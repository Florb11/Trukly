from flask import jsonify, request

from db_instance import db
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from models.operador_model import OperadorModel
from models.usuario_model import UsuarioModel
from models.viaje_model import ViajeModel

from src.Camion import Camion
from src.Chofer import Chofer
from src.OperadorLogistico import OperadorLogistico
from src.Usuario import Usuario
from src.Viaje import Viaje

from services.auth_service import AuthService
from utils.auth_decorators import roles_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidadorCompuesto,
)


logger = get_app_logger()


class ViajeController:

    @staticmethod
    def obtener_id_usuario_actual():
        # obtiene el id del usuario logueado
        return AuthService.obtener_id_usuario_actual()

    @staticmethod
    def obtener_rol_actual():
        # obtiene el rol del usuario logueado
        return AuthService.obtener_rol_actual()

    @staticmethod
    def crear_validador_creacion_viaje():
        # valida solo campos obligatorios del request
        return ValidadorCompuesto(
            [
                CampoObligatorio("fecha_salida"),
                CampoObligatorio("origen"),
                CampoObligatorio("destino"),
            ]
        )

    @staticmethod
    def crear_validador_cancelacion_viaje():
        # valida que venga el motivo de cancelacion
        return ValidadorCompuesto(
            [
                CampoObligatorio(
                    "motivo",
                    "Tenes que ingresar un motivo de cancelacion"
                ),
            ]
        )

    @staticmethod
    def preparar_datos_viaje(datos):
        # prepara los datos para crear el objeto de dominio
        fecha_llegada = (
            datos.get("fecha_llegada")
            or datos.get("fecha_estimada_llegada")
        )

        return {
            "fecha_salida": Viaje.convertir_fecha(
                datos.get("fecha_salida")
            ),
            "fecha_llegada": Viaje.convertir_fecha(fecha_llegada),
            "origen": datos.get("origen"),
            "destino": datos.get("destino"),
            "estado": Viaje.normalizar_estado(
                datos.get("estado", Viaje.ESTADO_PENDIENTE)
            ),
            "observaciones": datos.get("observaciones"),
            "recorrido": datos.get("recorrido", 0),
        }

    @staticmethod
    def crear_objeto_camion(camion_model):
        if camion_model is None:
            return None

        return Camion.crear_desde_datos(
            {
                "id_camion": camion_model.id_camion,
                "matricula": camion_model.matricula,
                "marca": camion_model.marca,
                "modelo": camion_model.modelo,
                "capacidad_carga": camion_model.capacidad_carga,
                "estado": camion_model.estado,
                "nroTanque": camion_model.nroTanque,
            }
        )

    @staticmethod
    def crear_objeto_chofer(usuario_model, chofer_model):
        if usuario_model is None or chofer_model is None:
            return None

        return Chofer.crear_desde_datos(
            {
                "id_usuario": usuario_model.id_usuario,
                "username": usuario_model.username,
                "email": usuario_model.email,
                "password": usuario_model.password,
                "nombre": usuario_model.nombre,
                "apellido": usuario_model.apellido,
                "estado": usuario_model.estado,
                "rol": usuario_model.rol,
                "licencia": chofer_model.licencia,
                "vencimientoLicencia": chofer_model.vencimientoLicencia,
                "legajo": chofer_model.legajo,
                "foto_perfil": usuario_model.foto_perfil,
            }
        )

    @staticmethod
    def crear_objeto_operador(usuario_model, operador_model):
        if usuario_model is None or operador_model is None:
            return None

        return OperadorLogistico.crear_desde_datos(
            {
                "id_usuario": usuario_model.id_usuario,
                "username": usuario_model.username,
                "email": usuario_model.email,
                "password": usuario_model.password,
                "nombre": usuario_model.nombre,
                "apellido": usuario_model.apellido,
                "estado": usuario_model.estado,
                "rol": usuario_model.rol,
                "legajo": operador_model.legajo,
                "sector": operador_model.sector,
                "foto_perfil": usuario_model.foto_perfil,
            }
        )

    @staticmethod
    def obtener_chofer_clase(id_chofer):
        if not id_chofer:
            return None

        usuario = UsuarioModel.query.get(id_chofer)
        chofer = ChoferModel.query.get(id_chofer)

        return ViajeController.crear_objeto_chofer(usuario, chofer)

    @staticmethod
    def obtener_operador_clase(id_operador):
        if not id_operador:
            return None

        usuario = UsuarioModel.query.get(id_operador)
        operador = OperadorModel.query.get(id_operador)

        return ViajeController.crear_objeto_operador(usuario, operador)

    @staticmethod
    def obtener_camion_clase(id_camion):
        if not id_camion:
            return None

        camion = CamionModel.query.get(id_camion)

        return ViajeController.crear_objeto_camion(camion)

    @staticmethod
    def crear_objeto_viaje(viaje_model, cargar_relaciones=True):
        operador = None
        chofer = None
        camion = None

        if cargar_relaciones:
            operador = ViajeController.obtener_operador_clase(
                viaje_model.OperadorLogistico_Usuario_idUsuario
            )
            chofer = ViajeController.obtener_chofer_clase(
                viaje_model.Chofer_Usuario_idUsuario
            )
            camion = ViajeController.obtener_camion_clase(
                viaje_model.Camion_id_camion
            )

        return Viaje.crear_desde_datos(
            {
                "fecha_salida": viaje_model.fecha_salida,
                "fecha_llegada": viaje_model.fecha_llegada,
                "origen": viaje_model.origen,
                "destino": viaje_model.destino,
                "estado": viaje_model.estado,
                "observaciones": viaje_model.observaciones,
                "recorrido": viaje_model.recorrido,
                "id_operador": (
                    viaje_model.OperadorLogistico_Usuario_idUsuario
                ),
                "id_chofer": viaje_model.Chofer_Usuario_idUsuario,
                "id_camion": viaje_model.Camion_id_camion,
            },
            id_viaje=viaje_model.id_viaje,
            operador=operador,
            chofer=chofer,
            camion=camion,
        )

    @staticmethod
    def crear_modelo_viaje(viaje):
        return ViajeModel(
            fecha_salida=viaje.fecha_salida,
            fecha_llegada=viaje.fecha_llegada,
            origen=viaje.origen,
            destino=viaje.destino,
            estado=viaje.estado,
            observaciones=viaje.observaciones,
            recorrido=viaje.recorrido,
            OperadorLogistico_Usuario_idUsuario=viaje.id_operador,
            Chofer_Usuario_idUsuario=viaje.id_chofer,
            Camion_id_camion=viaje.id_camion,
        )

    @staticmethod
    def actualizar_modelo_viaje(viaje_model, viaje):
        viaje_model.fecha_salida = viaje.fecha_salida
        viaje_model.fecha_llegada = viaje.fecha_llegada
        viaje_model.origen = viaje.origen
        viaje_model.destino = viaje.destino
        viaje_model.estado = viaje.estado
        viaje_model.observaciones = viaje.observaciones
        viaje_model.recorrido = viaje.recorrido
        viaje_model.OperadorLogistico_Usuario_idUsuario = (
            viaje.id_operador
        )
        viaje_model.Chofer_Usuario_idUsuario = viaje.id_chofer
        viaje_model.Camion_id_camion = viaje.id_camion

    @staticmethod
    def obtener_viajes_por_rol(rol, id_usuario):
        if rol == Usuario.ROL_ADMIN:
            return ViajeModel.query.all()

        if rol == Usuario.ROL_CHOFER:
            return ViajeModel.query.filter_by(
                Chofer_Usuario_idUsuario=id_usuario
            ).all()

        if rol == Usuario.ROL_OPERADOR:
            return ViajeModel.query.filter_by(
                OperadorLogistico_Usuario_idUsuario=id_usuario
            ).all()

        return None

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_CHOFER,
        Usuario.ROL_OPERADOR,
    )
    def listar_viajes():
        # lista viajes segun el rol logueado
        rol = ViajeController.obtener_rol_actual()
        id_usuario = ViajeController.obtener_id_usuario_actual()

        viajes = ViajeController.obtener_viajes_por_rol(rol, id_usuario)

        if viajes is None:
            return jsonify({
                "mensaje": "No tenes permiso para ver los viajes"
            }), 403

        return jsonify([viaje.to_dict() for viaje in viajes]), 200

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_CHOFER,
        Usuario.ROL_OPERADOR,
    )
    def obtener_viaje(id_viaje):
        viaje_model = ViajeModel.query.get(id_viaje)

        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        rol = ViajeController.obtener_rol_actual()
        id_usuario = ViajeController.obtener_id_usuario_actual()

        viaje = ViajeController.crear_objeto_viaje(viaje_model)

        if not viaje.puede_ser_visto_por(rol, id_usuario):
            return jsonify({
                "mensaje": "No tenes permiso para ver este viaje"
            }), 403

        return jsonify(viaje_model.to_dict()), 200

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def crear_viaje():
        # recibe el request
        rol = ViajeController.obtener_rol_actual()
        id_usuario = ViajeController.obtener_id_usuario_actual()

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=[
                "fecha_salida",
                "fecha_llegada",
                "fecha_estimada_llegada",
                "origen",
                "destino",
                "estado",
                "observaciones",
            ],
            campos_enteros=[
                "OperadorLogistico_Usuario_idUsuario",
                "id_operador",
                "Chofer_Usuario_idUsuario",
                "id_chofer",
                "Camion_id_camion",
                "id_camion",
            ],
            campos_decimales=["recorrido"],
        )

        # valores por defecto
        datos["estado"] = Viaje.normalizar_estado(
            datos.get("estado") or Viaje.ESTADO_PENDIENTE
        )
        datos["recorrido"] = datos.get("recorrido", 0)

        # valida campos obligatorios del request
        validador = ViajeController.crear_validador_creacion_viaje()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # valida reglas propias del viaje
        datos_validos, mensaje_error = Viaje.validar_datos_viaje(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # obtiene ids segun nombres posibles
        id_operador = (
            datos.get("OperadorLogistico_Usuario_idUsuario")
            or datos.get("id_operador")
        )

        if rol == Usuario.ROL_OPERADOR:
            id_operador = id_usuario

        id_chofer = (
            datos.get("Chofer_Usuario_idUsuario")
            or datos.get("id_chofer")
        )

        id_camion = (
            datos.get("Camion_id_camion")
            or datos.get("id_camion")
        )

        if not id_operador:
            return jsonify({"mensaje": "El operador es obligatorio"}), 400

        if not id_chofer:
            return jsonify({"mensaje": "El chofer es obligatorio"}), 400

        if not id_camion:
            return jsonify({"mensaje": "El camion es obligatorio"}), 400

        operador = ViajeController.obtener_operador_clase(id_operador)
        chofer = ViajeController.obtener_chofer_clase(id_chofer)
        camion = ViajeController.obtener_camion_clase(id_camion)

        if operador is None:
            return jsonify({"mensaje": "Operador no encontrado"}), 404

        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        if not camion.esta_disponible():
            return jsonify({
                "mensaje": "El camion no esta disponible para asignar un viaje"
            }), 400

        datos_viaje = ViajeController.preparar_datos_viaje(datos)

        viaje = Viaje.crear_desde_datos(
            datos_viaje,
            operador=operador,
            chofer=chofer,
            camion=camion,
        )

        if viaje is None or not viaje.validar_datos():
            return jsonify({
                "mensaje": "Los datos del viaje no son validos"
            }), 400

        nuevo_viaje = ViajeController.crear_modelo_viaje(viaje)

        try:
            db.session.add(nuevo_viaje)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo crear el viaje")

            return jsonify({
                "mensaje": "No se pudo crear el viaje"
            }), 500

        return jsonify({
            "mensaje": "Viaje creado correctamente",
            "viaje": nuevo_viaje.to_dict(),
        }), 201

    @staticmethod
    @roles_required(Usuario.ROL_ADMIN)
    def listar_viajes_admin():
        viajes = ViajeModel.query.all()

        return jsonify([viaje.to_dict() for viaje in viajes]), 200

    @staticmethod
    @roles_required(Usuario.ROL_ADMIN)
    def obtener_viaje_admin(id_viaje):
        viaje = ViajeModel.query.get(id_viaje)

        if viaje is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        return jsonify(viaje.to_dict()), 200

    @staticmethod
    @roles_required(Usuario.ROL_ADMIN)
    def cancelar_viaje_admin(id_viaje):
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["motivo"],
        )

        motivo = datos.get("motivo")

        validador = ViajeController.crear_validador_cancelacion_viaje()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        viaje_model = ViajeModel.query.get(id_viaje)

        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        viaje = ViajeController.crear_objeto_viaje(viaje_model)

        if not viaje.cancelar(motivo):
            return jsonify({
                "mensaje": "No se pudo cancelar el viaje"
            }), 400

        ViajeController.actualizar_modelo_viaje(viaje_model, viaje)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo cancelar el viaje")

            return jsonify({
                "mensaje": "No se pudo cancelar el viaje"
            }), 500

        return jsonify({
            "mensaje": "Viaje cancelado correctamente",
            "viaje": viaje_model.to_dict()
        }), 200


