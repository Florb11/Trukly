from datetime import date, timedelta

from flask import jsonify
from flask_jwt_extended import jwt_required

from controllers.administrador_controller import AdministradorController

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.reporte_model import ReporteModel

from src.Usuario import Usuario
from src.Camion import Camion
from src.Viaje import Viaje
from src.ReporteFalla import ReporteFalla


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
            estado=Usuario.ESTADO_ACTIVO
        ).count()

        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado=Usuario.ESTADO_PENDIENTE,
            rol=Usuario.ROL_CHOFER
        ).all()

        choferes_pendientes = []

        for usuario in usuarios_pendientes:
            chofer = ChoferModel.query.get(usuario.id_usuario)
            choferes_pendientes.append(
                admin.preparar_chofer_pendiente(
                    usuario,
                    chofer
                )
            )

        camiones_registrados = CamionModel.query.count()

        camiones_disponibles = CamionModel.query.filter_by(
            estado=Camion.ESTADO_DISPONIBLE
        ).count()

        total_reportes = ReporteModel.query.count()

        reportes_abiertos = ReporteModel.query.filter(
            ReporteModel.estado != ReporteFalla.ESTADO_RESUELTO
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

        resumen = admin.armar_resumen_dashboard(
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