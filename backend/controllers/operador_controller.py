from flask import g, jsonify, request
from models.mecanico_model import MecanicoModel
from db_instance import db
from utils.app_logger import get_app_logger


from models.reporte_model import ReporteModel
from models.operador_model import OperadorModel
from models.viaje_model import ViajeModel
from models.chofer_model import ChoferModel
from models.camion_model import CamionModel
from utils.input_sanitizer import InputSanitizer
from utils.auth_decorators import operador_required

from models.usuario_model import UsuarioModel
from src.Viaje import Viaje

logger = get_app_logger()


class OperadorController:

    @staticmethod
    def listar_operadores():
        operadores = OperadorModel.query.all()
        return jsonify([operador.to_dict() for operador in operadores])

    @staticmethod
    def obtener_operador(id_usuario):
        operador = OperadorModel.query.get(id_usuario)
        if operador is None:
            return jsonify({"mensaje": "Operador no encontrado"}), 404
        return jsonify(operador.to_dict())

    @staticmethod
    def crear_operador():
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["Legajo", "Sector"],
            campos_enteros=["Usuario_idUsuario"],
        )
        nuevo_operador = OperadorModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["Legajo"],
            sector=datos["Sector"],
        )
        db.session.add(nuevo_operador)
        db.session.commit()
        return (
            jsonify(
                {
                    "mensaje": "Operador creado correctamente",
                    "operador": nuevo_operador.to_dict(),
                }
            ),
            201,
        )

    @staticmethod
    @operador_required
    def listar_viajes():
        operador = g.operador_actual
        try:
            viajes = ViajeModel.query.filter_by(
                OperadorLogistico_Usuario_idUsuario=operador.id_usuario
            ).all()
            return jsonify([v.to_dict() for v in viajes]), 200
        except Exception:
            logger.exception(
                f"Error al listar viajes del operador {operador.id_usuario}"
            )
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @operador_required
    def crear_viaje():
        operador = g.operador_actual

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["origen", "destino", "observaciones"],
            campos_enteros=["Chofer_Usuario_idUsuario", "Camion_id_camion"],
            campos_decimales=["recorrido"],
        )

        origen = datos.get("origen")
        destino = datos.get("destino")
        fecha_salida = datos.get("fecha_salida")
        fecha_llegada = datos.get("fecha_llegada")
        id_chofer = datos.get("Chofer_Usuario_idUsuario")
        id_camion = datos.get("Camion_id_camion")

        if (
            not origen
            or not destino
            or not fecha_salida
            or not id_chofer
            or not id_camion
        ):
            return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

        valido, error = Viaje.validar_datos_viaje(datos)
        if not valido:
            return jsonify({"mensaje": error}), 400

        try:
            nuevo_viaje = ViajeModel(
                OperadorLogistico_Usuario_idUsuario=operador.id_usuario,
                Chofer_Usuario_idUsuario=id_chofer,
                Camion_id_camion=id_camion,
                fecha_salida=fecha_salida,
                fecha_llegada=fecha_llegada,
                origen=origen,
                destino=destino,
                estado=Viaje.ESTADO_PENDIENTE,
                observaciones=datos.get("observaciones"),
                recorrido=datos.get("recorrido", 0),
            )
            db.session.add(nuevo_viaje)
            db.session.commit()
            return (
                jsonify(
                    {
                        "mensaje": "Viaje creado correctamente",
                        "viaje": nuevo_viaje.to_dict(),
                    }
                ),
                201,
            )

        except Exception:
            db.session.rollback()
            logger.exception(f"Error al crear viaje por operador {operador.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @operador_required
    def cancelar_viaje(id_viaje):
        operador = g.operador_actual

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["motivo"],
        )
        motivo = datos.get("motivo")
        if not motivo:
            return jsonify({"mensaje": "El motivo es obligatorio"}), 400

        viaje_model = ViajeModel.query.get(id_viaje)
        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        viaje = Viaje.crear_desde_datos(viaje_model.to_dict())

        if not operador.cancelar_viaje(viaje, motivo):
            return (
                jsonify(
                    {"mensaje": "El viaje no puede cancelarse en su estado actual"}
                ),
                400,
            )

        try:
            viaje_model.estado = viaje.estado
            viaje_model.observaciones = viaje.observaciones
            db.session.commit()
            return jsonify({"mensaje": "Viaje cancelado correctamente"}), 200

        except Exception:
            db.session.rollback()
            logger.exception(f"Error al cancelar viaje {id_viaje}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    # CORREGIR
    @staticmethod
    @operador_required
    def editar_viaje(id_viaje):
        operador = g.operador_actual

        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["origen", "destino", "observaciones"],
            campos_enteros=["Chofer_Usuario_idUsuario", "Camion_id_camion"],
            campos_decimales=["recorrido"],
        )

        viaje_model = ViajeModel.query.get(id_viaje)
        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        id_chofer = datos.get("Chofer_Usuario_idUsuario")
        id_camion = datos.get("Camion_id_camion")

        if id_chofer and not ChoferModel.query.get(id_chofer):
            return jsonify({"mensaje": "El chofer no existe"}), 400

        if id_camion and not CamionModel.query.get(id_camion):
            return jsonify({"mensaje": "El camión no existe"}), 400

        viaje_dict = viaje_model.to_dict()
        viaje_dict["id_operador"] = viaje_dict.get("OperadorLogistico_Usuario_idUsuario")
        viaje_dict["id_chofer"] = viaje_dict.get("Chofer_Usuario_idUsuario")
        viaje_dict["id_camion"] = viaje_dict.get("Camion_id_camion")

        viaje = Viaje.crear_desde_datos(viaje_dict)
        editado, mensaje_error = operador.editar_viaje(viaje, datos)

        if not editado:
            return jsonify({"mensaje": mensaje_error}), 400

        viaje_model.origen = viaje.origen
        viaje_model.destino = viaje.destino
        viaje_model.fecha_salida = viaje.fecha_salida
        viaje_model.fecha_llegada = viaje.fecha_llegada
        viaje_model.recorrido = viaje.recorrido
        viaje_model.observaciones = viaje.observaciones
        viaje_model.Chofer_Usuario_idUsuario = viaje.id_chofer
        viaje_model.Camion_id_camion = viaje.id_camion

        try:
            db.session.commit()
            return jsonify({"mensaje": "Viaje actualizado correctamente", "viaje": viaje_model.to_dict()}), 200
        except Exception:
            db.session.rollback()
            logger.exception(f"Error al editar viaje {id_viaje}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @operador_required
    def listar_camiones():
        try:
            camiones = CamionModel.query.all()
            return jsonify([c.to_dict() for c in camiones]), 200
        except Exception:
            logger.exception("Error al listar camiones")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @operador_required
    def listar_choferes():
        try:
            choferes = (
                db.session.query(ChoferModel, UsuarioModel)
                .join(
                    UsuarioModel,
                    ChoferModel.Usuario_idUsuario == UsuarioModel.id_usuario,
                )
                .all()
            )

            resultado = []
            for chofer, usuario in choferes:
                resultado.append(
                    {
                        "id_usuario": usuario.id_usuario,
                        "nombre": usuario.nombre,
                        "apellido": usuario.apellido,
                        "estado": usuario.estado,
                        "licencia": chofer.licencia,
                        "vencimientoLicencia": str(chofer.vencimientoLicencia),
                        "legajo": chofer.legajo,
                    }
                )

            return jsonify(resultado), 200
        except Exception:
            logger.exception("Error al listar choferes")
            return jsonify({"mensaje": "Error interno del servidor"}), 500

    @staticmethod
    @operador_required
    def obtener_estadisticas():
        operador = g.operador_actual

        try:
            viajes = ViajeModel.query.filter_by(
                OperadorLogistico_Usuario_idUsuario=operador.id_usuario
            ).all()

            total_viajes = len(viajes)
            viajes_pendientes = sum(1 for v in viajes if v.estado == Viaje.ESTADO_PENDIENTE)
            viajes_en_curso = sum(1 for v in viajes if v.estado == Viaje.ESTADO_EN_CURSO)
            viajes_finalizados = sum(1 for v in viajes if v.estado == Viaje.ESTADO_FINALIZADO)
            viajes_cancelados = sum(1 for v in viajes if v.estado == Viaje.ESTADO_CANCELADO)

            ultimos_viajes = (
                ViajeModel.query.filter_by(
                    OperadorLogistico_Usuario_idUsuario=operador.id_usuario
                )
                .order_by(ViajeModel.id_viaje.desc())
                .limit(5)
                .all()
            )

            id_camiones = list({v.Camion_id_camion for v in viajes})
            reportes = (
                ReporteModel.query.filter(
                    ReporteModel.Camion_id_camion.in_(id_camiones)
                ).all()
                if id_camiones
                else []
            )

            reportes_pendientes = sum(1 for r in reportes if r.estado == "pendiente")
            reportes_en_revision = sum(1 for r in reportes if r.estado == "en revision")
            reportes_resueltos = sum(1 for r in reportes if r.estado == "resuelto")

            ultimos_reportes = (
                ReporteModel.query.filter(ReporteModel.Camion_id_camion.in_(id_camiones))
                .order_by(ReporteModel.id_reporte.desc())
                .limit(5)
                .all()
                if id_camiones
                else []
            )

            from collections import Counter

            conteo_choferes = Counter(v.Chofer_Usuario_idUsuario for v in viajes)
            choferes_top = []
            for id_chofer, total in conteo_choferes.most_common(5):
                usuario = UsuarioModel.query.get(id_chofer)
                if usuario:
                    choferes_top.append({
                        "id_usuario": id_chofer,
                        "nombre": usuario.nombre,
                        "apellido": usuario.apellido,
                        "total_viajes": total,
                    })

            conteo_camiones = Counter(v.Camion_id_camion for v in viajes)
            camiones_top = []
            for id_camion, total in conteo_camiones.most_common(5):
                camion = CamionModel.query.get(id_camion)
                if camion:
                    camiones_top.append({
                        "id_camion": id_camion,
                        "matricula": camion.matricula,
                        "marca": camion.marca,
                        "modelo": camion.modelo,
                        "total_viajes": total,
                    })

            return jsonify({
                "resumen": {
                    "total_viajes": total_viajes,
                    "viajes_pendientes": viajes_pendientes,
                    "viajes_en_curso": viajes_en_curso,
                    "viajes_finalizados": viajes_finalizados,
                    "viajes_cancelados": viajes_cancelados,
                    "reportes_pendientes": reportes_pendientes,
                    "reportes_en_revision": reportes_en_revision,
                    "reportes_resueltos": reportes_resueltos,
                },
                "ultimos_viajes": [v.to_dict() for v in ultimos_viajes],
                "ultimos_reportes": [r.to_dict() for r in ultimos_reportes],
                "choferes_mas_usados": choferes_top,
                "camiones_mas_usados": camiones_top,
            }), 200

        except Exception:
            logger.exception(f"Error al obtener estadisticas del operador {operador.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
        
    @staticmethod
    @operador_required
    def listar_mecanicos():
        try:
            mecanicos = db.session.query(MecanicoModel, UsuarioModel).join(
                UsuarioModel, MecanicoModel.Usuario_idUsuario == UsuarioModel.id_usuario
            ).all()

            resultado = []
            for mecanico, usuario in mecanicos:
                resultado.append({
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "estado": usuario.estado,
                    "legajo": mecanico.legajo,
                    "especialidad": mecanico.especialidad,
                })

            return jsonify(resultado), 200
        except Exception:
            logger.exception("Error al listar mecanicos")
            return jsonify({"mensaje": "Error interno del servidor"}), 500