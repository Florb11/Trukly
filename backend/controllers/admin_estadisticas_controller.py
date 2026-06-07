from flask import jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import case, func

from db_instance import db

from controllers.administrador_controller import AdministradorController

from models.usuario_model import UsuarioModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.reporte_model import ReporteModel


class AdminEstadisticasController:

    @staticmethod
    @jwt_required()
    def obtener_estadisticas():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        total_viajes = ViajeModel.query.count()

        viajes_finalizados = ViajeModel.query.filter_by(
            estado="finalizado"
        ).count()

        viajes_cancelados = ViajeModel.query.filter_by(
            estado="cancelado"
        ).count()

        viajes_en_curso = ViajeModel.query.filter_by(
            estado="en-curso"
        ).count()

        total_reportes = ReporteModel.query.count()

        reportes_activos = ReporteModel.query.filter(
            ReporteModel.estado.in_([
                "pendiente",
                "en revision"
            ])
        ).count()

        reportes_resueltos = ReporteModel.query.filter_by(
            estado="resuelto"
        ).count()

        choferes_mas_viajes_db = (
            db.session.query(
                ViajeModel.Chofer_Usuario_idUsuario.label(
                    "id_usuario"
                ),
                UsuarioModel.nombre,
                UsuarioModel.apellido,
                func.count(
                    ViajeModel.id_viaje
                ).label("total_viajes"),
                func.sum(
                    case(
                        (
                            ViajeModel.estado == "finalizado",
                            1
                        ),
                        else_=0
                    )
                ).label("viajes_finalizados"),
                func.sum(
                    case(
                        (
                            ViajeModel.estado == "cancelado",
                            1
                        ),
                        else_=0
                    )
                ).label("viajes_cancelados")
            )
            .join(
                UsuarioModel,
                UsuarioModel.id_usuario
                == ViajeModel.Chofer_Usuario_idUsuario
            )
            .group_by(
                ViajeModel.Chofer_Usuario_idUsuario,
                UsuarioModel.nombre,
                UsuarioModel.apellido
            )
            .order_by(
                func.count(ViajeModel.id_viaje).desc()
            )
            .limit(10)
            .all()
        )

        choferes_mas_viajes = [
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
            for fila in choferes_mas_viajes_db
        ]

        operadores_mas_viajes_db = (
            db.session.query(
                ViajeModel
                .OperadorLogistico_Usuario_idUsuario
                .label("id_usuario"),
                UsuarioModel.nombre,
                UsuarioModel.apellido,
                func.count(
                    ViajeModel.id_viaje
                ).label("total_viajes"),
                func.sum(
                    case(
                        (
                            ViajeModel.estado == "finalizado",
                            1
                        ),
                        else_=0
                    )
                ).label("viajes_finalizados"),
                func.sum(
                    case(
                        (
                            ViajeModel.estado == "cancelado",
                            1
                        ),
                        else_=0
                    )
                ).label("viajes_cancelados")
            )
            .join(
                UsuarioModel,
                UsuarioModel.id_usuario
                == ViajeModel
                .OperadorLogistico_Usuario_idUsuario
            )
            .group_by(
                ViajeModel
                .OperadorLogistico_Usuario_idUsuario,
                UsuarioModel.nombre,
                UsuarioModel.apellido
            )
            .order_by(
                func.count(ViajeModel.id_viaje).desc()
            )
            .limit(10)
            .all()
        )

        operadores_mas_viajes = [
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
            for fila in operadores_mas_viajes_db
        ]

        choferes_mas_reportes_db = (
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
                            ReporteModel.estado == "resuelto",
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

        choferes_mas_reportes = [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_reportes": fila.total_reportes,
                "reportes_resueltos": int(
                    fila.reportes_resueltos or 0
                ),
            }
            for fila in choferes_mas_reportes_db
        ]

        mecanicos_mas_reparaciones_db = (
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
                            ReporteModel.estado == "resuelto",
                            1
                        ),
                        else_=0
                    )
                ).label("total_resueltos"),
                func.sum(
                    case(
                        (
                            ReporteModel.estado == "en revision",
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

        mecanicos_mas_reparaciones = [
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
            for fila in mecanicos_mas_reparaciones_db
        ]

        camiones_mas_reportes_db = (
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

        camiones_mas_reportes = [
            {
                "id_camion": fila.id_camion,
                "matricula": fila.matricula,
                "marca": fila.marca,
                "modelo": fila.modelo,
                "total_reportes": fila.total_reportes,
            }
            for fila in camiones_mas_reportes_db
        ]

        ultimos_viajes_db = (
            ViajeModel.query
            .order_by(ViajeModel.id_viaje.desc())
            .limit(10)
            .all()
        )

        ultimos_reportes_db = (
            ReporteModel.query
            .order_by(ReporteModel.fecha_hora.desc())
            .limit(10)
            .all()
        )

        return jsonify({
            "resumen": {
                "total_viajes": total_viajes,
                "viajes_finalizados": viajes_finalizados,
                "viajes_cancelados": viajes_cancelados,
                "viajes_en_curso": viajes_en_curso,
                "total_reportes": total_reportes,
                "reportes_activos": reportes_activos,
                "reportes_resueltos": reportes_resueltos,
            },
            "choferes_mas_viajes": choferes_mas_viajes,
            "operadores_mas_viajes": operadores_mas_viajes,
            "choferes_mas_reportes": choferes_mas_reportes,
            "mecanicos_mas_reparaciones": mecanicos_mas_reparaciones,
            "camiones_mas_reportes": camiones_mas_reportes,
            "ultimos_viajes": [
                viaje.to_dict()
                for viaje in ultimos_viajes_db
            ],
            "ultimos_reportes": [
                reporte.to_dict()
                for reporte in ultimos_reportes_db
            ],
        }), 200