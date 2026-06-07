from datetime import date, timedelta

from flask import jsonify
from flask_jwt_extended import jwt_required

from controllers.administrador_controller import AdministradorController

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.reporte_model import ReporteModel

from src.Camion import Camion


class AdminDashboardController:

    @staticmethod
    @jwt_required()
    def obtener_resumen_dashboard():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        usuarios_activos = UsuarioModel.query.filter_by(
            estado="activo"
        ).count()

        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado="pendiente",
            rol="chofer"
        ).all()

        choferes_pendientes = []

        for usuario in usuarios_pendientes:
            chofer = ChoferModel.query.get(usuario.id_usuario)

            datos_usuario = usuario.to_dict()

            if chofer:
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["legajo"] = chofer.legajo
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )
            else:
                datos_usuario["licencia"] = "-"

            choferes_pendientes.append(datos_usuario)

        camiones_registrados = CamionModel.query.count()

        camiones_disponibles = CamionModel.query.filter_by(
            estado="disponible"
        ).count()

        porcentaje_flota_disponible = (
            Camion.calcular_porcentaje_disponible(
                camiones_disponibles,
                camiones_registrados
            )
        )

        total_reportes = ReporteModel.query.count()

        reportes_abiertos = ReporteModel.query.filter(
            ReporteModel.estado != "resuelto"
        ).count()

        reportes_resueltos = ReporteModel.query.filter_by(
            estado="resuelto"
        ).count()

        porcentaje_reportes_resueltos = 0

        if total_reportes > 0:
            porcentaje_reportes_resueltos = round(
                (reportes_resueltos / total_reportes) * 100
            )

        hoy = date.today()

        viajes_del_dia = ViajeModel.query.filter(
            ViajeModel.fecha_salida == hoy
        ).count()

        viajes_en_curso = ViajeModel.query.filter_by(
            estado="en-curso"
        ).count()

        total_viajes = ViajeModel.query.count()

        viajes_finalizados = ViajeModel.query.filter_by(
            estado="finalizado"
        ).count()

        porcentaje_viajes_finalizados = 0

        if total_viajes > 0:
            porcentaje_viajes_finalizados = round(
                (viajes_finalizados / total_viajes) * 100
            )

        actividad_operativa = []

        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)

            cantidad_viajes = ViajeModel.query.filter(
                ViajeModel.fecha_salida == dia
            ).count()

            actividad_operativa.append(cantidad_viajes)

        return jsonify({
            "usuarios_activos": usuarios_activos,
            "camiones_registrados": camiones_registrados,
            "camiones_disponibles": camiones_disponibles,
            "reportes_abiertos": reportes_abiertos,
            "reportes_prioridad_alta": 0,
            "viajes_del_dia": viajes_del_dia,
            "viajes_en_curso": viajes_en_curso,
            "estado_general": {
                "flota_disponible": porcentaje_flota_disponible,
                "reportes_resueltos": porcentaje_reportes_resueltos,
                "viajes_finalizados": porcentaje_viajes_finalizados,
            },
            "actividad_operativa": actividad_operativa,
            "usuarios_pendientes": choferes_pendientes,
        }), 200