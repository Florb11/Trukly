from services.carga_service import comprobar_capacidad, ErrorCarga
from services.viaje_asignaciones_service import obtener_asignaciones
from services.horas_viaje_service import horas_chofer, limites_mes, tipos_control
from services.notificacion_service import NotificacionService
from services.viaje_notificacion_service import notificar_aceptacion_operador
from services.viaje_cambios_service import registrar, snapshot
import datetime

from flask import g, jsonify, request
from src.Camion import Camion
from src.ReporteFalla import ReporteFalla
from src.Viaje import Viaje
from db_instance import db
from utils.app_logger import get_app_logger

from models.reporte_model import ReporteModel
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from services.licencia_service import licencia_vigente, MENSAJE_LICENCIA
from utils.fecha_operativa import hoy_operativo
from utils.input_sanitizer import InputSanitizer
from utils.auth_decorators import chofer_required, roles_required, admin_required
from models.usuario_model import UsuarioModel
from src.Chofer import Chofer
from models.viaje_model import ViajeModel

logger = get_app_logger()


class ChoferController:

    @staticmethod
    @roles_required("admin", "operador")
    def listar_choferes():
        choferes = ChoferModel.query.all()
        return jsonify([chofer.to_dict() for chofer in choferes])

    @staticmethod
    @roles_required("admin", "operador", "chofer")
    def obtener_chofer(id_usuario):
        usuario = g.usuario_actual
        if usuario.rol == "chofer" and usuario.id_usuario != id_usuario:
            return jsonify({"mensaje": "Solo podés consultar tus propios datos de chofer"}), 403
        chofer = ChoferModel.query.get(id_usuario)
        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404
        return jsonify(chofer.to_dict())

    @staticmethod
    @admin_required
    def crear_chofer():
        cuerpo = request.get_json(silent=True)
        if not isinstance(cuerpo, dict):
            return jsonify({"mensaje": "Los datos del chofer no son válidos"}), 400
        id_usuario = cuerpo.get("Usuario_idUsuario")
        texto_id = str(id_usuario)
        if (isinstance(id_usuario, bool) or not texto_id.isascii() or not texto_id.isdigit()
                or len(texto_id) > 10 or not 1 <= int(texto_id) <= 2147483647):
            return jsonify({"mensaje": "El usuario del chofer no es válido"}), 400
        datos = InputSanitizer.sanitizar_campos(
            cuerpo,
            campos_texto=["legajo", "vencimientoLicencia", "licencia"],
            campos_enteros=["Usuario_idUsuario"],
        )
        for campo in ("legajo", "licencia"):
            if not datos.get(campo) or len(datos[campo]) > 50:
                return jsonify({"mensaje": f"El campo {campo} es obligatorio y admite hasta 50 caracteres"}), 400
        for campo, validar in [("licencia", Chofer.validar_licencia),
                               ("vencimientoLicencia", Chofer.validar_vencimiento_licencia)]:
            valido, mensaje = validar(datos.get(campo))
            if not valido:
                return jsonify({"mensaje": mensaje}), 400
        usuario = db.session.get(UsuarioModel, datos["Usuario_idUsuario"])
        if usuario is None:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        if usuario.rol != "chofer":
            return jsonify({"mensaje": "El usuario no tiene rol de chofer"}), 400
        if db.session.get(ChoferModel, usuario.id_usuario) is not None:
            return jsonify({"mensaje": "Este usuario ya tiene datos de chofer"}), 409
        nuevo_chofer = ChoferModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["legajo"],
            vencimientoLicencia=Chofer.convertir_vencimiento_licencia(datos["vencimientoLicencia"]),
            licencia=datos["licencia"],
        )
        try:
            db.session.add(nuevo_chofer)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudieron guardar los datos del chofer")
            return jsonify({"mensaje": "No se pudieron guardar los datos del chofer"}), 500
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
        from controllers.reporte_controller import ReporteController
        chofer = g.chofer_actual
        try:
            reportes = chofer.obtener_mis_reportes(ReporteModel.query)
            return jsonify([
                ReporteController.preparar_respuesta_reporte(reporte)
                for reporte in reportes
            ]), 200
        except Exception:
            logger.exception(f"Error al listar reportes del chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
        

    @staticmethod
    @chofer_required
    def listar_viajes_propios():
        chofer = g.chofer_actual

        try:
            viajes = chofer.obtener_mis_viajes(ViajeModel.query)
            ids_camiones = {viaje.Camion_id_camion for viaje in viajes}
            camiones = {
                camion.id_camion: camion.to_dict()
                for camion in CamionModel.query.filter(
                    CamionModel.id_camion.in_(ids_camiones)
                ).all()
            } if ids_camiones else {}

            respuesta = []
            for viaje in viajes:
                datos_viaje = viaje.to_dict()
                datos_viaje.update(obtener_asignaciones(viaje))
                datos_viaje["camion"] = camiones.get(
                    viaje.Camion_id_camion
                )
                respuesta.append(datos_viaje)

            return jsonify(respuesta), 200
        except Exception:
            logger.exception(f"Error al listar viajes del chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @chofer_required
    def listar_registros_propios():
        chofer = g.chofer_actual

        try:
            resultados = (
                db.session.query(RegistroIngresoSalidaModel, ViajeModel)
                .join(
                    ViajeModel,
                    RegistroIngresoSalidaModel.Viaje_id_viaje
                    == ViajeModel.id_viaje,
                )
                .filter(
                    ViajeModel.Chofer_Usuario_idUsuario
                    == chofer.id_usuario
                )
                .order_by(
                    RegistroIngresoSalidaModel.fecha_hora.desc(),
                    RegistroIngresoSalidaModel.id_registro.desc(),
                )
                .all()
            )

            controles_por_viaje = {}
            for registro, viaje in resultados:
                controles_por_viaje.setdefault(viaje.id_viaje, []).append(registro)
            esquemas = {id_viaje: tipos_control(controles) for id_viaje, controles in controles_por_viaje.items()}
            registros = []
            for registro, viaje in resultados:
                inicio, regreso = esquemas[viaje.id_viaje]
                tipo_original = registro.tipo_registro.strip().lower()
                tipo_registro = "ingreso" if tipo_original == inicio else "salida" if tipo_original == regreso else tipo_original
                registros.append({
                    "id_registro": registro.id_registro,
                    "fecha_hora": registro.fecha_hora.isoformat(),
                    "tipo_registro": tipo_registro,
                    "observacion": registro.observacion_texto,
                    "id_viaje": viaje.id_viaje,
                    "origen": viaje.origen_texto,
                    "destino": viaje.destino_texto,
                    "id_camion": viaje.Camion_id_camion,
                })

            return jsonify(registros), 200
        except Exception:
            logger.exception(
                f"Error al listar registros del chofer {chofer.id_usuario}"
            )
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @chofer_required
    def registrar_ingreso_salida(id_viaje):
        chofer = g.chofer_actual
        cuerpo = request.get_json(silent=True)
        if not isinstance(cuerpo, dict):
            return jsonify({"mensaje": "Los datos del control no son válidos."}), 400
        if cuerpo.get("observacion") is not None and not isinstance(cuerpo["observacion"], str):
            return jsonify({"mensaje": "La observación debe ser un texto."}), 400
        datos = InputSanitizer.sanitizar_campos(
            cuerpo,
            campos_texto=["tipo_registro", "observacion"],
        )
        if len(datos.get("observacion") or "") > 100:
            return jsonify({"mensaje": "La observación es demasiado larga. Acortá el texto o reducí los símbolos (máximo 100 caracteres almacenados) y volvé a confirmar el QR."}), 400
        tipo_registro = (datos.get("tipo_registro") or "").strip().lower()

        if tipo_registro not in {"ingreso", "salida"}:
            return jsonify({"mensaje": "El tipo debe ser ingreso o salida"}), 400

        chofer_model = ChoferModel.query.filter_by(Usuario_idUsuario=chofer.id_usuario).populate_existing().with_for_update().first()
        viaje_model = ViajeModel.query.filter_by(
            id_viaje=id_viaje,
            Chofer_Usuario_idUsuario=chofer.id_usuario,
        ).with_for_update().first()

        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado o no asignado al chofer"}), 404

        estado_actual = (viaje_model.estado or "").strip().lower()
        estado_esperado = "aceptado" if tipo_registro == "ingreso" else "en curso"

        if tipo_registro == "ingreso" and estado_actual == "pendiente":
            return jsonify({"mensaje": "Primero aceptá el viaje en Mis viajes antes de escanear la salida."}), 400

        if estado_actual != estado_esperado:
            accion = "iniciar" if tipo_registro == "ingreso" else "finalizar"
            return jsonify({
                "mensaje": f"El viaje no se puede {accion} desde el estado {viaje_model.estado}"
            }), 400

        if tipo_registro == "ingreso":
            if viaje_model.fecha_salida is None:
                return jsonify({"mensaje": "El viaje no tiene fecha de salida. Contactá al operador."}), 409
            if viaje_model.fecha_salida > hoy_operativo():
                return jsonify({
                    "mensaje": "La salida por QR se habilita el "
                    f"{viaje_model.fecha_salida.strftime('%d/%m/%Y')} a las 00:00 (hora de Argentina)."
                }), 409
            if not licencia_vigente(chofer_model):
                return jsonify({"mensaje": MENSAJE_LICENCIA}), 409
            otro_en_curso = ViajeModel.query.filter(
                ViajeModel.Chofer_Usuario_idUsuario == chofer.id_usuario,
                ViajeModel.id_viaje != id_viaje,
                ViajeModel.estado == "en curso",
            ).with_for_update().first()
            if otro_en_curso:
                return jsonify({"mensaje": "Registrá el regreso del viaje en curso antes de iniciar otro."}), 409

        ahora = datetime.datetime.now()
        registros = viaje_model.registros_horarios
        inicios = [r for r in registros if r.tipo_registro in {"ingreso", "entrada"}]
        finales = [r for r in registros if r.tipo_registro == "salida"]
        if tipo_registro == "ingreso" and registros:
            return jsonify({"mensaje": "El viaje ya tiene controles registrados. Revisá su historial."}), 409
        if tipo_registro == "salida" and (
            len(inicios) != 1 or finales or len(registros) != 1
            or inicios[0].fecha_hora >= ahora
        ):
            return jsonify({"mensaje": "Se necesita un único control de inicio válido antes de registrar el regreso."}), 409
        if tipo_registro == "ingreso":
            camion_carga = CamionModel.query.filter_by(id_camion=viaje_model.Camion_id_camion).populate_existing().with_for_update().first()
            if camion_carga is None:
                return jsonify({"mensaje": "Camión no encontrado"}), 404
            # "En viaje" también representa la reserva hecha al asignar el camión.
            if camion_carga.estado not in {Camion.ESTADO_DISPONIBLE, Camion.ESTADO_EN_VIAJE}:
                return jsonify({
                    "mensaje": "No podés iniciar el viaje: el camión está inactivo o en mantenimiento. Contactá al operador."
                }), 409
            try:
                comprobar_capacidad(viaje_model.id_viaje, camion_carga)
            except ErrorCarga as error:
                return jsonify({"mensaje": str(error)}), error.codigo

        nuevo_estado = "en curso" if tipo_registro == "ingreso" else "finalizado"
        nuevo_registro = RegistroIngresoSalidaModel(
            fecha_hora=ahora,
            tipo_registro=tipo_registro,
            observacion=datos.get("observacion") or None,
            Viaje_id_viaje=viaje_model.id_viaje,
        )

        antes = snapshot(viaje_model)
        viaje_model.estado = nuevo_estado
        if tipo_registro == "ingreso":
            camion_carga.estado = Camion.ESTADO_EN_VIAJE
        if tipo_registro == "salida":
            camion_model = CamionModel.query.get(viaje_model.Camion_id_camion)
            if camion_model and camion_model.estado == Camion.ESTADO_EN_VIAJE:
                tiene_reportes_activos = ReporteModel.query.filter(
                    ReporteModel.Camion_id_camion == camion_model.id_camion,
                    ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
                ).first() is not None
                camion_model.estado = (
                    Camion.ESTADO_EN_MANTENIMIENTO
                    if tiene_reportes_activos
                    else Camion.ESTADO_DISPONIBLE
                )

        try:
            db.session.add(nuevo_registro)
            registrar(viaje_model, chofer.id_usuario,
                "viaje_iniciado" if tipo_registro == "ingreso" else "viaje_finalizado", antes,
                {"tipo_registro": tipo_registro, "fecha_control": ahora.isoformat()})
            db.session.commit()
            return jsonify({
                "mensaje": (
                    "Check-in registrado correctamente"
                    if tipo_registro == "ingreso"
                    else "Check-out registrado correctamente"
                ),
                "registro": nuevo_registro.to_dict(),
                "viaje": viaje_model.to_dict(),
            }), 201
        except Exception:
            db.session.rollback()
            logger.exception(
                f"Error al registrar {tipo_registro} del viaje {id_viaje}"
            )
            return jsonify({"mensaje": "Error interno del servidor"}), 500
        
    @staticmethod
    @chofer_required
    def obtener_estadisticas():
        chofer = g.chofer_actual
        mes = request.args.get("mes", datetime.datetime.now().strftime("%Y-%m"))
        try:
            limites_mes(mes)
        except ValueError as error:
            return jsonify({"mensaje": str(error)}), 400

        try:
            viajes = ViajeModel.query.filter_by(
                Chofer_Usuario_idUsuario=chofer.id_usuario
            ).all()

            total_viajes = len(viajes)
            viajes_pendientes = sum(1 for v in viajes if v.estado.lower() == "pendiente")
            viajes_en_curso = sum(1 for v in viajes if v.estado.lower() == "en curso")
            viajes_aceptados = sum(1 for v in viajes if v.estado.lower() == "aceptado")
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
                    "viajes_aceptados": viajes_aceptados,
                    "viajes_finalizados": viajes_finalizados,
                    "viajes_cancelados": viajes_cancelados,
                    "reportes_pendientes": reportes_pendientes,
                    "reportes_en_revision": reportes_en_revision,
                    "reportes_resueltos": reportes_resueltos,
                },
                "horas_viaje": horas_chofer(chofer.id_usuario, mes),
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
    
    @staticmethod
    @chofer_required
    def iniciar_viaje(id_viaje):
        chofer = g.chofer_actual

        viaje_model = ViajeModel.query.filter_by(id_viaje=id_viaje, Chofer_Usuario_idUsuario=chofer.id_usuario).populate_existing().with_for_update().first()
        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        viaje_dict = viaje_model.to_dict()
        viaje_dict["id_chofer"] = viaje_dict.get("Chofer_Usuario_idUsuario")
        viaje_dict["id_camion"] = viaje_dict.get("Camion_id_camion")
        viaje_dict["id_operador"] = viaje_dict.get("OperadorLogistico_Usuario_idUsuario")

        viaje = Viaje.crear_desde_datos(viaje_dict)
        iniciado, mensaje_error = chofer.iniciar_viaje(viaje)

        if not iniciado:
            return jsonify({"mensaje": mensaje_error}), 400

        antes = snapshot(viaje_model)
        viaje_model.estado = viaje.estado

        try:
            notificar_aceptacion_operador(viaje_model)
            registrar(viaje_model, chofer.id_usuario, "viaje_aceptado", antes)
            db.session.commit()
            NotificacionService.enviar_push_pendientes()
            return jsonify({"mensaje": "Viaje aceptado correctamente", "viaje": viaje_model.to_dict()}), 200
        except Exception:
            db.session.rollback()
            logger.exception(f"Error al iniciar viaje {id_viaje}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @chofer_required
    def finalizar_viaje(id_viaje):
        # Compatibilidad con clientes antiguos: el cierre se registra por QR.
        viaje = ViajeModel.query.filter_by(
            id_viaje=id_viaje, Chofer_Usuario_idUsuario=g.chofer_actual.id_usuario
        ).first()
        if viaje is None:
            return jsonify({"mensaje": "Viaje no encontrado o no asignado al chofer"}), 404
        return jsonify({"mensaje": "Para finalizar el viaje, escaneá el QR de regreso en la app móvil."}), 409
