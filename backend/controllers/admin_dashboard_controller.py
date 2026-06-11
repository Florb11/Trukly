from datetime import date, timedelta

from flask import jsonify

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.reporte_model import ReporteModel

from src.Usuario import Usuario
from src.Camion import Camion
from src.Viaje import Viaje
from src.ReporteFalla import ReporteFalla
from utils.auth_decorators import admin_required


class AdminDashboardController:

    @staticmethod
    def _calcular_porcentaje(parte, total):
        if total <= 0:
            return 0

        return round((parte / total) * 100)

    @staticmethod
    def _preparar_chofer_pendiente(datos_usuario, datos_chofer=None):
        if datos_usuario is None:
            return None

        datos = dict(datos_usuario)

        if datos_chofer:
            datos["licencia"] = datos_chofer.get("licencia")
            datos["legajo"] = datos_chofer.get("legajo")
            datos["vencimientoLicencia"] = datos_chofer.get(
                "vencimientoLicencia"
            )
        else:
            datos["licencia"] = "-"

        return datos

    @staticmethod
    def _armar_resumen_dashboard(
        usuarios_activos,
        camiones_registrados,
        camiones_disponibles,
        reportes_abiertos,
        reportes_resueltos,
        total_reportes,
        viajes_del_dia,
        viajes_en_curso,
        viajes_finalizados,
        total_viajes,
        actividad_operativa,
        usuarios_pendientes,
    ):
        return {
            "usuarios_activos": usuarios_activos,
            "camiones_registrados": camiones_registrados,
            "camiones_disponibles": camiones_disponibles,
            "reportes_abiertos": reportes_abiertos,
            "reportes_prioridad_alta": 0,
            "viajes_del_dia": viajes_del_dia,
            "viajes_en_curso": viajes_en_curso,
            "estado_general": {
                "flota_disponible": (
                    AdminDashboardController._calcular_porcentaje(
                        camiones_disponibles,
                        camiones_registrados
                    )
                ),
                "reportes_resueltos": (
                    AdminDashboardController._calcular_porcentaje(
                        reportes_resueltos,
                        total_reportes
                    )
                ),
                "viajes_finalizados": (
                    AdminDashboardController._calcular_porcentaje(
                        viajes_finalizados,
                        total_viajes
                    )
                ),
            },
            "actividad_operativa": actividad_operativa,
            "usuarios_pendientes": usuarios_pendientes,
        }

    @staticmethod
    @admin_required
    def obtener_resumen_dashboard():
        usuarios_activos = UsuarioModel.query.filter_by(
            estado=Usuario.ESTADO_ACTIVO
        ).count()

        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado=Usuario.ESTADO_PENDIENTE,
            rol=Usuario.ROL_CHOFER
        ).all()

        choferes_pendientes = []

        for usuario in usuarios_pendientes:
            chofer = ChoferModel.query.get(usuario.id_usuario)
            datos_chofer = None

            if chofer:
                datos_chofer = {
                    "licencia": chofer.licencia,
                    "legajo": chofer.legajo,
                    "vencimientoLicencia": str(
                        chofer.vencimientoLicencia
                    ),
                }

            choferes_pendientes.append(
                AdminDashboardController._preparar_chofer_pendiente(
                    usuario.to_dict(),
                    datos_chofer
                )
            )

        camiones_registrados = CamionModel.query.count()

        camiones_disponibles = CamionModel.query.filter_by(
            estado=Camion.ESTADO_DISPONIBLE
        ).count()

        total_reportes = ReporteModel.query.count()

        reportes_abiertos = ReporteModel.query.filter(
            ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS)
        ).count()

        reportes_resueltos = ReporteModel.query.filter_by(
            estado=ReporteFalla.ESTADO_RESUELTO
        ).count()

        hoy = date.today()

        viajes_del_dia = ViajeModel.query.filter(
            ViajeModel.fecha_salida == hoy
        ).count()

        viajes_en_curso = ViajeModel.query.filter(
            ViajeModel.estado.in_(
                Viaje.ESTADOS_EN_CURSO
            )
        ).count()

        total_viajes = ViajeModel.query.count()

        viajes_finalizados = ViajeModel.query.filter_by(
            estado=Viaje.ESTADO_FINALIZADO
        ).count()

        actividad_operativa = []

        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)

            cantidad_viajes = ViajeModel.query.filter(
                ViajeModel.fecha_salida == dia
            ).count()

            actividad_operativa.append(cantidad_viajes)

        resumen = AdminDashboardController._armar_resumen_dashboard(
            usuarios_activos=usuarios_activos,
            camiones_registrados=camiones_registrados,
            camiones_disponibles=camiones_disponibles,
            reportes_abiertos=reportes_abiertos,
            reportes_resueltos=reportes_resueltos,
            total_reportes=total_reportes,
            viajes_del_dia=viajes_del_dia,
            viajes_en_curso=viajes_en_curso,
            viajes_finalizados=viajes_finalizados,
            total_viajes=total_viajes,
            actividad_operativa=actividad_operativa,
            usuarios_pendientes=choferes_pendientes,
        )

        return jsonify(resumen), 200