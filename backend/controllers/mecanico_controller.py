from flask import g, jsonify, request

from src.observer.EventManager import EventManager
from src.observer.NotificacionReporteListener import (
    NotificacionReporteListener
)

from db_instance import db

from models.reporte_model import ReporteModel
from models.camion_model import CamionModel

from src.Camion import Camion
from src.ReporteFalla import ReporteFalla
from services.auth_service import AuthService
from services.notificacion_service import NotificacionService
from utils.auth_decorators import mecanico_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import CampoObligatorio, ValidadorCompuesto


logger = get_app_logger()


class MecanicoController:

    @staticmethod
    def crear_validador_resolucion_reporte():
        return ValidadorCompuesto(
            [
                CampoObligatorio(
                    "nota_reparacion",
                    "La nota de reparacion es obligatoria"
                ),
            ]
        )

    @staticmethod
    def obtener_mecanico_actual():
        return AuthService.obtener_mecanico_actual_desde_token()

    @staticmethod
    def crear_objeto_reporte(reporte_model):
        return ReporteFalla.crear_desde_datos(
            {
                "id_reporte": reporte_model.id_reporte,
                "fecha_hora": reporte_model.fecha_hora,
                "descripcion": reporte_model.descripcion,
                "estado": reporte_model.estado,
                "id_camion": reporte_model.Camion_id_camion,
                "id_mecanico": (
                    reporte_model.Mecanico_Usuario_idUsuario
                ),
                "id_chofer": (
                    reporte_model.Chofer_Usuario_idUsuario
                ),
                "nota_reparacion": reporte_model.nota_reparacion,
                "fecha_resolucion": reporte_model.fecha_resolucion,
            }
        )

    @staticmethod
    def actualizar_modelo_reporte(reporte_model, reporte_clase):
        reporte_model.estado = reporte_clase.estado
        reporte_model.nota_reparacion = reporte_clase.nota_reparacion
        reporte_model.fecha_resolucion = reporte_clase.fecha_resolucion

    @staticmethod
    def preparar_respuesta_reporte(reporte_model):
        reporte_clase = MecanicoController.crear_objeto_reporte(
            reporte_model
        )

        return MecanicoController.preparar_respuesta_reporte_clase(
            reporte_clase
        )

    @staticmethod
    def preparar_respuesta_reporte_clase(reporte_clase):
        datos = reporte_clase.to_dict()

        datos["Camion_id_camion"] = datos.pop("id_camion")
        datos["Mecanico_Usuario_idUsuario"] = datos.pop("id_mecanico")
        datos["Chofer_Usuario_idUsuario"] = datos.pop("id_chofer")

        return datos

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
    def actualizar_modelo_camion(camion_model, camion_clase):
        camion_model.estado = camion_clase.estado

    @staticmethod
    def obtener_reportes_activos_camion(id_camion, id_reporte_resuelto):
        return (
            ReporteModel.query
            .filter(
                ReporteModel.Camion_id_camion == id_camion,
                ReporteModel.id_reporte != id_reporte_resuelto,
                ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
            )
            .all()
        )

    @staticmethod
    def separar_reportes_mantenimiento(reportes):
        reportes_pendientes = []
        reparaciones_realizadas = []

        for reporte in reportes:
            if reporte.estado == ReporteFalla.ESTADO_RESUELTO:
                reparaciones_realizadas.append(reporte)
            else:
                reportes_pendientes.append(reporte)

        return reportes_pendientes, reparaciones_realizadas

    @staticmethod
    @mecanico_required
    def listar_reportes_asignados():
        mecanico = g.mecanico_actual

        reportes = ReporteModel.query.filter_by(
            Mecanico_Usuario_idUsuario=mecanico.id_usuario
        ).all()

        return jsonify(
            {
                "reportes": [
                    MecanicoController.preparar_respuesta_reporte(reporte)
                    for reporte in reportes
                ]
            }
        ), 200

    @staticmethod
    @mecanico_required
    def resolver_reporte(id_reporte):
        mecanico = g.mecanico_actual

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["nota_reparacion"],
        )
        validador = MecanicoController.crear_validador_resolucion_reporte()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        nota_reparacion = datos.get("nota_reparacion")

        reporte_model = ReporteModel.query.get(id_reporte)

        if reporte_model is None:
            return jsonify(
                {
                    "mensaje": "Reporte no encontrado"
                }
            ), 404

        reporte = MecanicoController.crear_objeto_reporte(reporte_model)

        pudo_resolver = mecanico.resolver_reporte(
            reporte,
            nota_reparacion
        )

        if not pudo_resolver:
            return jsonify(
                {
                    "mensaje": (
                        "No podes resolver este reporte o falta "
                        "la nota de reparacion"
                    )
                }
            ), 400

        MecanicoController.actualizar_modelo_reporte(
            reporte_model,
            reporte
        )

        camion_model = CamionModel.query.get(reporte_model.Camion_id_camion)
        camion = MecanicoController.crear_objeto_camion(camion_model)
        reportes_activos = (
            MecanicoController.obtener_reportes_activos_camion(
                reporte_model.Camion_id_camion,
                reporte_model.id_reporte
            )
        )

        camion_liberado = mecanico.liberar_camion_si_corresponde(
            camion,
            reportes_activos
        )

        if camion_liberado:
            MecanicoController.actualizar_modelo_camion(
                camion_model,
                camion
            )

        event_manager = EventManager()
        listener_notificacion = NotificacionReporteListener(
            NotificacionService.agregar_a_sesion
        )

        event_manager.suscribir(
            "reporte_resuelto",
            listener_notificacion
        )

        event_manager.notificar(
            "reporte_resuelto",
            {
                "id_usuario": reporte_model.Chofer_Usuario_idUsuario,
                "titulo": "Reporte resuelto",
                "mensaje": (
                    f"El reporte #{reporte_model.id_reporte} fue resuelto. "
                    f"Nota: {nota_reparacion}"
                ),
                "tipo": "reporte_resuelto",
            }
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo resolver el reporte")

            return jsonify(
                {
                    "mensaje": "No se pudo resolver el reporte"
                }
            ), 500

        return jsonify(
            {
                "mensaje": "Reporte marcado como resuelto",
                "reporte": MecanicoController.preparar_respuesta_reporte(
                    reporte_model
                ),
                "camion_liberado": camion_liberado,
            }
        ), 200

    @staticmethod
    @mecanico_required
    def listar_camiones_mantenimiento():
        mecanico = g.mecanico_actual

        if not mecanico.esta_activo():
            return jsonify(
                {
                    "mensaje": "El mecanico no esta activo"
                }
            ), 403

        camiones = CamionModel.query.all()
        resultado = []

        for camion in camiones:
            reportes = ReporteModel.query.filter_by(
                Camion_id_camion=camion.id_camion
            ).all()
            reportes_clase = [
                MecanicoController.crear_objeto_reporte(reporte)
                for reporte in reportes
            ]

            reportes_pendientes, reparaciones_realizadas = (
                MecanicoController.separar_reportes_mantenimiento(
                    reportes_clase
                )
            )

            resultado.append(
                {
                    "camion": camion.to_dict(),
                    "cantidad_reportes_pendientes": len(
                        reportes_pendientes
                    ),
                    "cantidad_reparaciones_realizadas": len(
                        reparaciones_realizadas
                    ),
                }
            )

        return jsonify(
            {
                "camiones": resultado
            }
        ), 200

    @staticmethod
    @mecanico_required
    def obtener_mantenimiento_camion(id_camion):
        mecanico = g.mecanico_actual

        if not mecanico.esta_activo():
            return jsonify(
                {
                    "mensaje": "El mecanico no esta activo"
                }
            ), 403

        camion = CamionModel.query.get(id_camion)

        if camion is None:
            return jsonify(
                {
                    "mensaje": "Camion no encontrado"
                }
            ), 404

        reportes = (
            ReporteModel.query
            .filter_by(Camion_id_camion=id_camion)
            .order_by(ReporteModel.fecha_hora.desc())
            .all()
        )
        reportes_clase = [
            MecanicoController.crear_objeto_reporte(reporte)
            for reporte in reportes
        ]

        reportes_pendientes, reparaciones_realizadas = (
            MecanicoController.separar_reportes_mantenimiento(
                reportes_clase
            )
        )

        return jsonify(
            {
                "camion": camion.to_dict(),
                "reportes_pendientes": [
                    MecanicoController.preparar_respuesta_reporte_clase(
                        reporte
                    )
                    for reporte in reportes_pendientes
                ],
                "reparaciones_realizadas": [
                    MecanicoController.preparar_respuesta_reporte_clase(
                        reporte
                    )
                    for reporte in reparaciones_realizadas
                ],
            }
        ), 200