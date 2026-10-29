from uuid import uuid4
from sqlalchemy.exc import DBAPIError
from flask import g, jsonify, request
from db_instance import db
from models.viaje_model import ViajeModel
from services import carga_service
from utils.auth_decorators import operador_required, roles_required
from services.auth_service import AuthService
from utils.app_logger import get_app_logger


class CargaController:
    @staticmethod
    @roles_required("admin", "operador", "chofer")
    def consultar(id_viaje):
        try:
            rol = AuthService.obtener_rol_actual()
            id_usuario = AuthService.obtener_id_usuario_actual()
            consulta = ViajeModel.query.filter_by(id_viaje=id_viaje)
            if rol == "operador":
                consulta = consulta.filter_by(OperadorLogistico_Usuario_idUsuario=id_usuario)
            elif rol == "chofer":
                consulta = consulta.filter_by(Chofer_Usuario_idUsuario=id_usuario)
            elif rol != "admin":
                return jsonify({"mensaje": "No tenés permiso para consultar las cargas"}), 403
            viaje = consulta.one_or_none()
            if viaje is None:
                return jsonify({"mensaje": "Viaje no encontrado o no asignado al usuario"}), 404
            datos = carga_service.resumen(viaje)
            datos["editable"] = False
            return jsonify(datos), 200
        except carga_service.ErrorCarga as error:
            return jsonify({"mensaje": str(error)}), error.codigo
        except Exception:
            db.session.rollback()
            referencia = uuid4().hex[:12]
            get_app_logger().exception("Error al consultar cargas ref=%s viaje=%s", referencia, id_viaje)
            return jsonify({"mensaje": f"No se pudieron consultar las cargas. Referencia: {referencia}"}), 500

    @staticmethod
    @operador_required
    def gestionar(id_viaje, id_carga=None):
        try:
            # El mismo bloqueo serializa cargas, cambios de camión e inicio por QR.
            viaje = ViajeModel.query.filter_by(id_viaje=id_viaje,
                OperadorLogistico_Usuario_idUsuario=g.operador_actual.id_usuario).with_for_update().one_or_none()
            if viaje is None:
                return jsonify({"mensaje": "Viaje no encontrado o no asignado al operador"}), 404
            if request.method == "GET":
                return jsonify(carga_service.resumen(viaje)), 200
            if request.method == "DELETE":
                datos = carga_service.eliminar(viaje, id_carga)
            else:
                datos = carga_service.guardar(viaje, request.get_json(silent=True), id_carga)
            db.session.commit()
            return jsonify(datos), 201 if request.method == "POST" else 200
        except carga_service.ErrorCarga as error:
            db.session.rollback()
            return jsonify({"mensaje": str(error)}), error.codigo
        except Exception as error:
            db.session.rollback()
            referencia = uuid4().hex[:12]
            get_app_logger().exception(
                "Error de cargas ref=%s metodo=%s viaje=%s operador=%s",
                referencia, request.method, id_viaje, g.operador_actual.id_usuario,
            )
            codigo_db = error.orig.args[0] if isinstance(error, DBAPIError) and getattr(error.orig, "args", ()) else None
            if codigo_db in {1054, 1146}:
                mensaje = "La base de datos no tiene el esquema de cargas actualizado. Aplicá la migración de cargas en la base conectada al backend."
            else:
                mensaje = "No se pudieron cargar los datos del viaje." if request.method == "GET" else "No se pudo guardar la carga."
            return jsonify({"mensaje": f"{mensaje} Referencia: {referencia}", "referencia": referencia}), 500
