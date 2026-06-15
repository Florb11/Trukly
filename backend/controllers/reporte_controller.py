from datetime import datetime

from flask import jsonify, request

from db_instance import db
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.reporte_model import ReporteModel
from models.usuario_model import UsuarioModel

from src.Camion import Camion
from src.Chofer import Chofer
from src.Mecanico import Mecanico
from src.ReporteFalla import ReporteFalla
from src.Usuario import Usuario
from src.observer.EventManager import EventManager
from src.observer.NotificacionReporteListener import (
    NotificacionReporteListener
)

from services.auth_service import AuthService
from services.notificacion_service import NotificacionService
from utils.auth_decorators import obtener_admin_actual_desde_token
from utils.auth_decorators import roles_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidadorCompuesto,
)


logger = get_app_logger()


class ReporteController:

    @staticmethod
    def crear_validador_creacion_reporte():
        # valida campos obligatorios para crear reporte
        return ValidadorCompuesto(
            [
                CampoObligatorio("descripcion"),
                CampoObligatorio("Camion_id_camion"),
            ]
        )

    @staticmethod
    def crear_validador_cambio_estado():
        # valida solo que venga el estado
        return ValidadorCompuesto(
            [
                CampoObligatorio("estado"),
            ]
        )

    @staticmethod
    def crear_validador_asignacion_mecanico():
        # valida que venga el mecanico
        return ValidadorCompuesto(
            [
                CampoObligatorio("Mecanico_Usuario_idUsuario"),
            ]
        )

    @staticmethod
    def crear_objeto_camion(camion_model):
        # convierte CamionModel a Camion de dominio
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
        # convierte UsuarioModel y ChoferModel a Chofer de dominio
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
    def crear_objeto_mecanico(usuario_model, mecanico_model):
        # convierte UsuarioModel y MecanicoModel a Mecanico de dominio
        if usuario_model is None or mecanico_model is None:
            return None

        return Mecanico.crear_desde_datos(
            {
                "id_usuario": usuario_model.id_usuario,
                "username": usuario_model.username,
                "email": usuario_model.email,
                "password": usuario_model.password,
                "nombre": usuario_model.nombre,
                "apellido": usuario_model.apellido,
                "estado": usuario_model.estado,
                "rol": usuario_model.rol,
                "legajo": mecanico_model.legajo,
                "especialidad": mecanico_model.especialidad,
                "foto_perfil": usuario_model.foto_perfil,
            }
        )

    @staticmethod
    def obtener_chofer_clase(id_chofer):
        # busca chofer en BD y lo convierte a dominio
        if not id_chofer:
            return None

        usuario = UsuarioModel.query.get(id_chofer)
        chofer = ChoferModel.query.get(id_chofer)

        return ReporteController.crear_objeto_chofer(
            usuario,
            chofer
        )

    @staticmethod
    def obtener_mecanico_clase(id_mecanico):
        # busca mecanico en BD y lo convierte a dominio
        if not id_mecanico:
            return None

        usuario = UsuarioModel.query.get(id_mecanico)
        mecanico = MecanicoModel.query.get(id_mecanico)

        return ReporteController.crear_objeto_mecanico(
            usuario,
            mecanico
        )

    @staticmethod
    def obtener_camion_clase(id_camion):
        # busca camion en BD y lo convierte a dominio
        if not id_camion:
            return None

        camion = CamionModel.query.get(id_camion)

        return ReporteController.crear_objeto_camion(camion)

    @staticmethod
    def crear_objeto_reporte(reporte_model, cargar_relaciones=True):
        # convierte ReporteModel a ReporteFalla de dominio
        camion = None
        mecanico = None
        chofer = None

        if cargar_relaciones:
            camion = ReporteController.obtener_camion_clase(
                reporte_model.Camion_id_camion
            )

            chofer = ReporteController.obtener_chofer_clase(
                reporte_model.Chofer_Usuario_idUsuario
            )

            if reporte_model.Mecanico_Usuario_idUsuario:
                mecanico = ReporteController.obtener_mecanico_clase(
                    reporte_model.Mecanico_Usuario_idUsuario
                )

        return ReporteFalla.crear_desde_datos(
            {
                "id_reporte": reporte_model.id_reporte,
                "fecha_hora": reporte_model.fecha_hora,
                "descripcion": reporte_model.descripcion,
                "estado": reporte_model.estado,
                "id_camion": reporte_model.Camion_id_camion,
                "id_mecanico": reporte_model.Mecanico_Usuario_idUsuario,
                "id_chofer": reporte_model.Chofer_Usuario_idUsuario,
                "nota_reparacion": reporte_model.nota_reparacion,
                "fecha_resolucion": reporte_model.fecha_resolucion,
            },
            camion=camion,
            mecanico=mecanico,
            chofer=chofer,
        )

    @staticmethod
    def actualizar_modelo_reporte(reporte_model, reporte_clase):
        # copia cambios del dominio al modelo
        reporte_model.estado = reporte_clase.estado
        reporte_model.Mecanico_Usuario_idUsuario = (
            reporte_clase.id_mecanico
        )
        reporte_model.nota_reparacion = reporte_clase.nota_reparacion
        reporte_model.fecha_resolucion = reporte_clase.fecha_resolucion

    @staticmethod
    def preparar_respuesta_reporte(reporte_model):
        # arma la respuesta para el frontend
        reporte_clase = ReporteController.crear_objeto_reporte(
            reporte_model,
            cargar_relaciones=False
        )

        datos = reporte_clase.to_dict()

        datos["Camion_id_camion"] = datos.pop("id_camion")
        datos["Mecanico_Usuario_idUsuario"] = datos.pop("id_mecanico")
        datos["Chofer_Usuario_idUsuario"] = datos.pop("id_chofer")

        return datos

    @staticmethod
    def actualizar_modelo_camion(camion_model, camion_clase):
        # copia el estado del dominio al modelo
        camion_model.estado = camion_clase.estado

    @staticmethod
    def obtener_reportes_activos_camion(id_camion, id_reporte_excluido):
        # busca reportes activos del camion
        return (
            ReporteModel.query
            .filter(
                ReporteModel.Camion_id_camion == id_camion,
                ReporteModel.id_reporte != id_reporte_excluido,
                ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
            )
            .all()
        )

    @staticmethod
    def liberar_camion_si_corresponde(reporte_clase):
        # libera el camion si ya no tiene reportes activos
        if reporte_clase.estado in ReporteFalla.ESTADOS_ACTIVOS:
            return False

        camion_model = CamionModel.query.get(reporte_clase.id_camion)
        camion = ReporteController.crear_objeto_camion(camion_model)

        if camion is None:
            return False

        reportes_activos = ReporteController.obtener_reportes_activos_camion(
            reporte_clase.id_camion,
            reporte_clase.id_reporte
        )

        camion_liberado = camion.liberar_si_no_tiene_reportes_activos(
            reportes_activos
        )

        if camion_liberado:
            ReporteController.actualizar_modelo_camion(
                camion_model,
                camion
            )

        return camion_liberado

    @staticmethod
    def marcar_camion_en_mantenimiento_si_corresponde(reporte_clase):
        # manda el camion a mantenimiento si el reporte esta activo
        if reporte_clase.estado not in ReporteFalla.ESTADOS_ACTIVOS:
            return False

        camion_model = CamionModel.query.get(reporte_clase.id_camion)
        camion = ReporteController.crear_objeto_camion(camion_model)

        if camion is None:
            return False

        camion_en_mantenimiento = camion.marcar_en_mantenimiento()

        if camion_en_mantenimiento:
            ReporteController.actualizar_modelo_camion(
                camion_model,
                camion
            )

        return camion_en_mantenimiento

    @staticmethod
    def notificar_reporte_asignado(reporte_clase, mecanico):
        # notifica al mecanico cuando se le asigna un reporte
        event_manager = EventManager()
        listener_notificacion = NotificacionReporteListener(
            NotificacionService.agregar_a_sesion
        )

        event_manager.suscribir(
            "reporte_asignado",
            listener_notificacion
        )

        event_manager.notificar(
            "reporte_asignado",
            {
                "id_usuario": mecanico.id_usuario,
                "titulo": "Nueva reparacion asignada",
                "mensaje": (
                    f"Se te asigno el reporte #{reporte_clase.id_reporte} "
                    f"del camion #{reporte_clase.id_camion}."
                ),
                "tipo": "reporte_asignado",
            }
        )

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def listar_reportes():
        # lista todos los reportes
        reportes = ReporteModel.query.all()

        return jsonify({
            "reportes": [
                ReporteController.preparar_respuesta_reporte(reporte)
                for reporte in reportes
            ]
        }), 200

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
        Usuario.ROL_CHOFER,
    )
    def obtener_reporte(id_reporte):
        # obtiene un reporte por id
        reporte = ReporteModel.query.get(id_reporte)

        if reporte is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        rol = AuthService.obtener_rol_actual()
        id_usuario = AuthService.obtener_id_usuario_actual()

        if (
            rol == Usuario.ROL_CHOFER
            and reporte.Chofer_Usuario_idUsuario != id_usuario
        ):
            return jsonify({
                "mensaje": "No tenes permiso para ver este reporte"
            }), 403

        return jsonify({
            "reporte": ReporteController.preparar_respuesta_reporte(reporte)
        }), 200

    @staticmethod
    @roles_required(Usuario.ROL_CHOFER)
    def crear_reporte():
    
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["descripcion"],
            campos_enteros=["Camion_id_camion"],
        )

      
        validador = ReporteController.crear_validador_creacion_reporte()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        id_chofer = AuthService.obtener_id_usuario_actual()
        camion_id = datos.get("Camion_id_camion")
        descripcion = datos.get("descripcion")

     
        datos_validos, mensaje_error = ReporteFalla.validar_datos_reporte(
            {
                "descripcion": descripcion,
                "estado": ReporteFalla.ESTADO_PENDIENTE,
            }
        )

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        chofer = ReporteController.obtener_chofer_clase(id_chofer)
        camion = ReporteController.obtener_camion_clase(camion_id)

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404

        reporte_clase = ReporteFalla.crear_desde_datos(
            {
                "fecha_hora": datetime.now(),
                "descripcion": descripcion,
                "estado": ReporteFalla.ESTADO_PENDIENTE,
            }
        )

        if reporte_clase is None:
            return jsonify({"mensaje": "No se pudo crear el reporte"}), 400


        if not chofer.registrar_reporte(reporte_clase):
            return jsonify({
                "mensaje": "No se pudo asociar el reporte al chofer"
            }), 400

        if not camion.registrar_reporte(reporte_clase):
            return jsonify({
                "mensaje": "No se pudo asociar el reporte al camion"
            }), 400

        if not reporte_clase.validar_datos():
            return jsonify({"mensaje": "Faltan datos obligatorios"}), 400

        if not reporte_clase.validar_estado():
            return jsonify({"mensaje": "Estado invalido"}), 400

     
        nuevo_reporte = ReporteModel(
            fecha_hora=reporte_clase.fecha_hora,
            descripcion=reporte_clase.descripcion,
            estado=reporte_clase.estado,
            Camion_id_camion=reporte_clase.id_camion,
            Mecanico_Usuario_idUsuario=reporte_clase.id_mecanico,
            Chofer_Usuario_idUsuario=reporte_clase.id_chofer,
        )

        camion_en_mantenimiento = (
            ReporteController.marcar_camion_en_mantenimiento_si_corresponde(
                reporte_clase
            )
        )

        ReporteController.notificar_reporte_creado(reporte_clase)

        try:
            db.session.add(nuevo_reporte)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo crear el reporte")

            return jsonify({
                "mensaje": "No se pudo crear el reporte"
            }), 500

        return jsonify({
            "mensaje": "Reporte creado correctamente",
            "reporte": ReporteController.preparar_respuesta_reporte(
                nuevo_reporte
            ),
            "camion_en_mantenimiento": camion_en_mantenimiento,
        }), 201
    
    @staticmethod
    def notificar_reporte_creado(reporte_clase):
        from models.operador_model import OperadorModel

        event_manager = EventManager()
        listener = NotificacionReporteListener(NotificacionService.agregar_a_sesion)
        operadores = OperadorModel.query.all()

        reporte_clase.notificar_creacion(event_manager, listener, operadores)

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def cambiar_estado_reporte(id_reporte):
        # cambia el estado de un reporte
        reporte_db = ReporteModel.query.get(id_reporte)

        if reporte_db is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["estado"],
        )

        datos["estado"] = str(datos.get("estado") or "").strip().lower()

        # valida que venga el estado
        validador = ReporteController.crear_validador_cambio_estado()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        nuevo_estado = datos.get("estado")

        # crea objeto de dominio
        reporte_clase = ReporteController.crear_objeto_reporte(reporte_db)
        rol = AuthService.obtener_rol_actual()

        if rol == Usuario.ROL_ADMIN:
            admin = obtener_admin_actual_desde_token()
            estado_cambiado = (
                admin.cambiar_estado_reporte(
                    reporte_clase,
                    nuevo_estado
                )
                if admin
                else False
            )
        else:
            estado_cambiado = reporte_clase.cambiar_estado(nuevo_estado)

        if not estado_cambiado:
            return jsonify({"mensaje": "Estado invalido"}), 400

        # aplica cambios al modelo
        ReporteController.actualizar_modelo_reporte(
            reporte_db,
            reporte_clase
        )

        # actualiza estado del camion si corresponde
        camion_liberado = ReporteController.liberar_camion_si_corresponde(
            reporte_clase
        )

        camion_en_mantenimiento = (
            ReporteController.marcar_camion_en_mantenimiento_si_corresponde(
                reporte_clase
            )
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo modificar el estado del reporte")

            return jsonify({
                "mensaje": "No se pudo modificar el estado del reporte"
            }), 500

        return jsonify({
            "mensaje": "Estado del reporte modificado correctamente",
            "reporte": ReporteController.preparar_respuesta_reporte(
                reporte_db
            ),
            "camion_liberado": camion_liberado,
            "camion_en_mantenimiento": camion_en_mantenimiento,
        }), 200

    @staticmethod
    @roles_required(Usuario.ROL_OPERADOR)
    def asignar_mecanico(id_reporte):
        # asigna un mecanico a un reporte
        reporte_db = ReporteModel.query.get(id_reporte)

        if reporte_db is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_enteros=["Mecanico_Usuario_idUsuario"],
        )

        # valida campo obligatorio
        validador = ReporteController.crear_validador_asignacion_mecanico()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        id_mecanico = datos.get("Mecanico_Usuario_idUsuario")

        # busca mecanico de dominio
        mecanico = ReporteController.obtener_mecanico_clase(id_mecanico)

        if mecanico is None:
            return jsonify({"mensaje": "Mecanico no encontrado"}), 404

        # crea reporte de dominio
        reporte_clase = ReporteController.crear_objeto_reporte(reporte_db)

        # el mecanico registra el reporte asignado
        if not mecanico.asignar_reporte(reporte_clase):
            return jsonify({
                "mensaje": "No se pudo asignar el mecanico"
            }), 400

        # aplica cambios al modelo
        ReporteController.actualizar_modelo_reporte(
            reporte_db,
            reporte_clase
        )

        # cambia camion a mantenimiento si corresponde
        camion_en_mantenimiento = (
            ReporteController.marcar_camion_en_mantenimiento_si_corresponde(
                reporte_clase
            )
        )

        # notifica al mecanico
        ReporteController.notificar_reporte_asignado(
            reporte_clase,
            mecanico
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo asignar el mecanico")

            return jsonify({
                "mensaje": "No se pudo asignar el mecanico"
            }), 500

        return jsonify({
            "mensaje": "Mecanico asignado correctamente",
            "reporte": ReporteController.preparar_respuesta_reporte(
                reporte_db
            ),
            "camion_en_mantenimiento": camion_en_mantenimiento,
        }), 200
    
    @staticmethod
    def notificar_reporte_creado(reporte_clase):
        from models.operador_model import OperadorModel

        event_manager = EventManager()
        listener = NotificacionReporteListener(NotificacionService.agregar_a_sesion)

        operadores = OperadorModel.query.all()

        for operador in operadores:
            event_manager.suscribir("reporte_creado", listener)
            event_manager.notificar(
                "reporte_creado",
                {
                    "id_usuario": operador.Usuario_idUsuario,
                    "titulo": "Nuevo reporte de falla",
                    "mensaje": (
                        f"El chofer #{reporte_clase.id_chofer} creó el reporte "
                    ),
                    "tipo": "reporte_creado",
                }
            )