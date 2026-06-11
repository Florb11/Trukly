from flask import jsonify
from sqlalchemy import case, func

from db_instance import db

from models.usuario_model import UsuarioModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.reporte_model import ReporteModel

from src.Viaje import Viaje
from src.ReporteFalla import ReporteFalla
from utils.auth_decorators import admin_required


class AdminEstadisticasController:

    @staticmethod
    def _convertir_modelos_a_diccionario(modelos):
        return [
            modelo.to_dict()
            for modelo in modelos
        ]

    @staticmethod
    def _armar_ranking_viajes(filas):
        return [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_viajes": fila.total_viajes,
                "viajes_finalizados": int(
                    fila.viajes_finalizados or 0
                ),
                "viajes_cancelados": int(
                    fila.viajes_cancelados or 0
                ),
            }
            for fila in filas
        ]

    @staticmethod
    def _armar_ranking_reportes_chofer(filas):
        return [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_reportes": fila.total_reportes,
                "reportes_resueltos": int(
                    fila.reportes_resueltos or 0
                ),
            }
            for fila in filas
        ]

    @staticmethod
    def _armar_ranking_reparaciones_mecanico(filas):
        return [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_asignados": fila.total_asignados,
                "total_resueltos": int(
                    fila.total_resueltos or 0
                ),
                "en_revision": int(
                    fila.en_revision or 0
                ),
            }
            for fila in filas
        ]

    @staticmethod
    def _armar_ranking_reportes_camion(filas):
        return [
            {
                "id_camion": fila.id_camion,
                "matricula": fila.matricula,
                "marca": fila.marca,
                "modelo": fila.modelo,
                "total_reportes": fila.total_reportes,
            }
            for fila in filas
        ]

    @staticmethod
    def _armar_resumen_estadisticas(
        total_viajes,
        viajes_finalizados,
        viajes_cancelados,
        viajes_en_curso,
        total_reportes,
        reportes_activos,
        reportes_resueltos,
    ):
        return {
            "total_viajes": total_viajes,
            "viajes_finalizados": viajes_finalizados,
            "viajes_cancelados": viajes_cancelados,
            "viajes_en_curso": viajes_en_curso,
            "total_reportes": total_reportes,
            "reportes_activos": reportes_activos,
            "reportes_resueltos": reportes_resueltos,
        }

    @staticmethod
    def _armar_estadisticas(
        resumen,
        choferes_mas_viajes,
        operadores_mas_viajes,
        choferes_mas_reportes,
        mecanicos_mas_reparaciones,
        camiones_mas_reportes,
        ultimos_viajes,
        ultimos_reportes,
    ):
        return {
            "resumen": resumen,
            "choferes_mas_viajes": choferes_mas_viajes,
            "operadores_mas_viajes": operadores_mas_viajes,
            "choferes_mas_reportes": choferes_mas_reportes,
            "mecanicos_mas_reparaciones": mecanicos_mas_reparaciones,
            "camiones_mas_reportes": camiones_mas_reportes,
            "ultimos_viajes": ultimos_viajes,
            "ultimos_reportes": ultimos_reportes,
        }

    @staticmethod
    def _obtener_resumen():
        total_viajes = ViajeModel.query.count()

        viajes_finalizados = ViajeModel.query.filter_by(
            estado=Viaje.ESTADO_FINALIZADO
        ).count()

        viajes_cancelados = ViajeModel.query.filter_by(
            estado=Viaje.ESTADO_CANCELADO
        ).count()

        viajes_en_curso = ViajeModel.query.filter(
            ViajeModel.estado.in_(
                Viaje.ESTADOS_EN_CURSO
            )
        ).count()

        total_reportes = ReporteModel.query.count()

        reportes_activos = ReporteModel.query.filter(
            ReporteModel.estado.in_(
                ReporteFalla.ESTADOS_ACTIVOS
            )
        ).count()

        reportes_resueltos = ReporteModel.query.filter_by(
            estado=ReporteFalla.ESTADO_RESUELTO
        ).count()

        return AdminEstadisticasController._armar_resumen_estadisticas(
            total_viajes=total_viajes,
            viajes_finalizados=viajes_finalizados,
            viajes_cancelados=viajes_cancelados,
            viajes_en_curso=viajes_en_curso,
            total_reportes=total_reportes,
            reportes_activos=reportes_activos,
            reportes_resueltos=reportes_resueltos,
        )

    @staticmethod
    def _obtener_ranking_viajes_por_usuario(columna_usuario):
        viajes_db = (
            db.session.query(
                columna_usuario.label("id_usuario"),
                UsuarioModel.nombre,
                UsuarioModel.apellido,
                func.count(
                    ViajeModel.id_viaje
                ).label("total_viajes"),
                func.sum(
                    case(
                        (
                            ViajeModel.estado
                            == Viaje.ESTADO_FINALIZADO,
                            1
                        ),
                        else_=0
                    )
                ).label("viajes_finalizados"),
                func.sum(
                    case(
                        (
                            ViajeModel.estado
                            == Viaje.ESTADO_CANCELADO,
                            1
                        ),
                        else_=0
                    )
                ).label("viajes_cancelados")
            )
            .join(
                UsuarioModel,
                UsuarioModel.id_usuario == columna_usuario
            )
            .group_by(
                columna_usuario,
                UsuarioModel.nombre,
                UsuarioModel.apellido
            )
            .order_by(
                func.count(ViajeModel.id_viaje).desc()
            )
            .limit(10)
            .all()
        )

        return AdminEstadisticasController._armar_ranking_viajes(viajes_db)

    @staticmethod
    def _obtener_choferes_mas_reportes():
        reportes_db = (
            db.session.query(
                ReporteModel
                .Chofer_Usuario_idUsuario
                .label("id_usuario"),
                UsuarioModel.nombre,
                UsuarioModel.apellido,
                func.count(
                    ReporteModel.id_reporte
                ).label("total_reportes"),
                func.sum(
                    case(
                        (
                            ReporteModel.estado
                            == ReporteFalla.ESTADO_RESUELTO,
                            1
                        ),
                        else_=0
                    )
                ).label("reportes_resueltos")
            )
            .join(
                UsuarioModel,
                UsuarioModel.id_usuario
                == ReporteModel.Chofer_Usuario_idUsuario
            )
            .group_by(
                ReporteModel.Chofer_Usuario_idUsuario,
                UsuarioModel.nombre,
                UsuarioModel.apellido
            )
            .order_by(
                func.count(ReporteModel.id_reporte).desc()
            )
            .limit(10)
            .all()
        )

        return (
            AdminEstadisticasController
            ._armar_ranking_reportes_chofer(reportes_db)
        )

    @staticmethod
    def _obtener_mecanicos_mas_reparaciones():
        reparaciones_db = (
            db.session.query(
                ReporteModel
                .Mecanico_Usuario_idUsuario
                .label("id_usuario"),
                UsuarioModel.nombre,
                UsuarioModel.apellido,
                func.count(
                    ReporteModel.id_reporte
                ).label("total_asignados"),
                func.sum(
                    case(
                        (
                            ReporteModel.estado
                            == ReporteFalla.ESTADO_RESUELTO,
                            1
                        ),
                        else_=0
                    )
                ).label("total_resueltos"),
                func.sum(
                    case(
                        (
                            ReporteModel.estado
                            == ReporteFalla.ESTADO_EN_REVISION,
                            1
                        ),
                        else_=0
                    )
                ).label("en_revision")
            )
            .join(
                UsuarioModel,
                UsuarioModel.id_usuario
                == ReporteModel.Mecanico_Usuario_idUsuario
            )
            .filter(
                ReporteModel
                .Mecanico_Usuario_idUsuario
                .isnot(None)
            )
            .group_by(
                ReporteModel.Mecanico_Usuario_idUsuario,
                UsuarioModel.nombre,
                UsuarioModel.apellido
            )
            .order_by(
                func.count(ReporteModel.id_reporte).desc()
            )
            .limit(10)
            .all()
        )

        return AdminEstadisticasController._armar_ranking_reparaciones_mecanico(
            reparaciones_db
        )

    @staticmethod
    def _obtener_camiones_mas_reportes():
        reportes_db = (
            db.session.query(
                ReporteModel.Camion_id_camion.label(
                    "id_camion"
                ),
                CamionModel.matricula,
                CamionModel.marca,
                CamionModel.modelo,
                func.count(
                    ReporteModel.id_reporte
                ).label("total_reportes")
            )
            .join(
                CamionModel,
                CamionModel.id_camion
                == ReporteModel.Camion_id_camion
            )
            .group_by(
                ReporteModel.Camion_id_camion,
                CamionModel.matricula,
                CamionModel.marca,
                CamionModel.modelo
            )
            .order_by(
                func.count(ReporteModel.id_reporte).desc()
            )
            .limit(10)
            .all()
        )

        return (
            AdminEstadisticasController
            ._armar_ranking_reportes_camion(reportes_db)
        )

    @staticmethod
    def _obtener_ultimos_movimientos():
        ultimos_viajes = (
            ViajeModel.query
            .order_by(ViajeModel.id_viaje.desc())
            .limit(10)
            .all()
        )

        ultimos_reportes = (
            ReporteModel.query
            .order_by(ReporteModel.fecha_hora.desc())
            .limit(10)
            .all()
        )

        return ultimos_viajes, ultimos_reportes

    @staticmethod
    @admin_required
    def obtener_estadisticas():
        resumen = AdminEstadisticasController._obtener_resumen()

        choferes_mas_viajes = (
            AdminEstadisticasController
            ._obtener_ranking_viajes_por_usuario(
                ViajeModel.Chofer_Usuario_idUsuario
            )
        )

        operadores_mas_viajes = (
            AdminEstadisticasController
            ._obtener_ranking_viajes_por_usuario(
                ViajeModel.OperadorLogistico_Usuario_idUsuario
            )
        )

        choferes_mas_reportes = (
            AdminEstadisticasController._obtener_choferes_mas_reportes()
        )

        mecanicos_mas_reparaciones = (
            AdminEstadisticasController
            ._obtener_mecanicos_mas_reparaciones()
        )

        camiones_mas_reportes = (
            AdminEstadisticasController._obtener_camiones_mas_reportes()
        )

        ultimos_viajes_db, ultimos_reportes_db = (
            AdminEstadisticasController
            ._obtener_ultimos_movimientos()
        )
        ultimos_viajes = (
            AdminEstadisticasController._convertir_modelos_a_diccionario(
                ultimos_viajes_db
            )
        )
        ultimos_reportes = (
            AdminEstadisticasController._convertir_modelos_a_diccionario(
                ultimos_reportes_db
            )
        )

        respuesta = AdminEstadisticasController._armar_estadisticas(
            resumen=resumen,
            choferes_mas_viajes=choferes_mas_viajes,
            operadores_mas_viajes=operadores_mas_viajes,
            choferes_mas_reportes=choferes_mas_reportes,
            mecanicos_mas_reparaciones=mecanicos_mas_reparaciones,
            camiones_mas_reportes=camiones_mas_reportes,
            ultimos_viajes=ultimos_viajes,
            ultimos_reportes=ultimos_reportes,
        )

        return jsonify(respuesta), 200