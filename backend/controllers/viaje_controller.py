from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db_instance import db
from models.viaje_model import ViajeModel
from src.Viaje import Viaje


class ViajeController:

    @staticmethod
    def obtener_id_usuario_actual():
        identidad = get_jwt_identity()

        try:
            return int(identidad)
        except (TypeError, ValueError):
            return identidad

    @staticmethod
    def obtener_rol_actual():
        return get_jwt().get("rol")

    @staticmethod
    def crear_objeto_viaje(viaje_model):
        return Viaje(
            id_viaje=viaje_model.id_viaje,
            fecha_salida=viaje_model.fecha_salida,
            fecha_llegada=viaje_model.fecha_llegada,
            origen=viaje_model.origen,
            destino=viaje_model.destino,
            estado=viaje_model.estado,
            observaciones=viaje_model.observaciones,
            recorrido=viaje_model.recorrido,
            OperadorLogistico_Usuario_idUsuario=(
                viaje_model.OperadorLogistico_Usuario_idUsuario
            ),
            Chofer_Usuario_idUsuario=(
                viaje_model.Chofer_Usuario_idUsuario
            ),
            Camion_id_camion=viaje_model.Camion_id_camion,
        )

    @staticmethod
    def crear_modelo_viaje(viaje):
        return ViajeModel(
            fecha_salida=viaje.fecha_salida,
            fecha_llegada=viaje.fecha_llegada,
            origen=viaje.origen,
            destino=viaje.destino,
            estado=viaje.estado,
            observaciones=viaje.observaciones,
            recorrido=viaje.recorrido,
            OperadorLogistico_Usuario_idUsuario=(
                viaje.OperadorLogistico_Usuario_idUsuario
            ),
            Chofer_Usuario_idUsuario=viaje.Chofer_Usuario_idUsuario,
            Camion_id_camion=viaje.Camion_id_camion,
        )

    @staticmethod
    def actualizar_modelo_viaje(viaje_model, viaje):
        viaje_model.fecha_salida = viaje.fecha_salida
        viaje_model.fecha_llegada = viaje.fecha_llegada
        viaje_model.origen = viaje.origen
        viaje_model.destino = viaje.destino
        viaje_model.estado = viaje.estado
        viaje_model.observaciones = viaje.observaciones
        viaje_model.recorrido = viaje.recorrido
        viaje_model.OperadorLogistico_Usuario_idUsuario = (
            viaje.OperadorLogistico_Usuario_idUsuario
        )
        viaje_model.Chofer_Usuario_idUsuario = (
            viaje.Chofer_Usuario_idUsuario
        )
        viaje_model.Camion_id_camion = viaje.Camion_id_camion

    @staticmethod
    def obtener_viajes_por_rol(rol, id_usuario):
        if rol == "admin":
            return ViajeModel.query.all()

        if rol == "chofer":
            return ViajeModel.query.filter_by(
                Chofer_Usuario_idUsuario=id_usuario
            ).all()

        if rol == "operador":
            return ViajeModel.query.filter_by(
                OperadorLogistico_Usuario_idUsuario=id_usuario
            ).all()

        return None

    @staticmethod
    @jwt_required()
    def listar_viajes():
        rol = ViajeController.obtener_rol_actual()
        id_usuario = ViajeController.obtener_id_usuario_actual()

        viajes = ViajeController.obtener_viajes_por_rol(rol, id_usuario)

        if viajes is None:
            return jsonify({
                "mensaje": "No tenes permiso para ver los viajes"
            }), 403

        return jsonify([viaje.to_dict() for viaje in viajes]), 200

    @staticmethod
    @jwt_required()
    def obtener_viaje(id_viaje):
        viaje_model = ViajeModel.query.get(id_viaje)

        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        rol = ViajeController.obtener_rol_actual()
        id_usuario = ViajeController.obtener_id_usuario_actual()
        viaje = ViajeController.crear_objeto_viaje(viaje_model)

        if not viaje.puede_ser_visto_por(rol, id_usuario):
            return jsonify({
                "mensaje": "No tenes permiso para ver este viaje"
            }), 403

        return jsonify(viaje_model.to_dict()), 200

    @staticmethod
    @jwt_required()
    def crear_viaje():
        rol = ViajeController.obtener_rol_actual()
        id_usuario = ViajeController.obtener_id_usuario_actual()

        if rol not in ["admin", "operador"]:
            return jsonify({
                "mensaje": "No tenes permiso para crear viajes"
            }), 403

        datos = request.get_json(silent=True) or {}

        campos_obligatorios = [
            "fecha_salida",
            "origen",
            "destino",
        ]

        for campo in campos_obligatorios:
            if campo not in datos or str(datos[campo]).strip() == "":
                return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

        id_operador = (
            datos.get("OperadorLogistico_Usuario_idUsuario")
            or datos.get("id_operador")
        )

        if rol == "operador":
            id_operador = id_usuario

        id_chofer = (
            datos.get("Chofer_Usuario_idUsuario")
            or datos.get("id_chofer")
        )
        id_camion = datos.get("Camion_id_camion") or datos.get("id_camion")

        viaje = Viaje(
            id_viaje=None,
            fecha_salida=datos["fecha_salida"],
            fecha_llegada=(
                datos.get("fecha_llegada")
                or datos.get("fecha_estimada_llegada")
            ),
            origen=datos["origen"],
            destino=datos["destino"],
            estado=datos.get("estado", "pendiente"),
            observaciones=datos.get("observaciones"),
            recorrido=datos.get("recorrido", 0),
            OperadorLogistico_Usuario_idUsuario=id_operador,
            Chofer_Usuario_idUsuario=id_chofer,
            Camion_id_camion=id_camion,
        )

        if not viaje.validar_datos():
            return jsonify({
                "mensaje": "Los datos del viaje no son validos"
            }), 400

        viaje.normalizar_datos()
        nuevo_viaje = ViajeController.crear_modelo_viaje(viaje)

        try:
            db.session.add(nuevo_viaje)
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo crear el viaje"
            }), 500

        return jsonify({
            "mensaje": "Viaje creado correctamente",
            "viaje": nuevo_viaje.to_dict(),
        }), 201

    @staticmethod
    @jwt_required()
    def listar_viajes_admin():
        rol = ViajeController.obtener_rol_actual()

        if rol != "admin":
            return jsonify({
                "mensaje": "No tenes permiso para ver los viajes"
            }), 403

        viajes = ViajeModel.query.all()

        return jsonify([viaje.to_dict() for viaje in viajes]), 200

    @staticmethod
    @jwt_required()
    def obtener_viaje_admin(id_viaje):
        rol = ViajeController.obtener_rol_actual()

        if rol != "admin":
            return jsonify({
                "mensaje": "No tenes permiso para ver este viaje"
            }), 403

        viaje = ViajeModel.query.get(id_viaje)

        if viaje is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        return jsonify(viaje.to_dict()), 200

    @staticmethod
    @jwt_required()
    def cancelar_viaje_admin(id_viaje):
        rol = ViajeController.obtener_rol_actual()

        if rol != "admin":
            return jsonify({
                "mensaje": "No tenes permiso para cancelar viajes"
            }), 403

        datos = request.get_json(silent=True) or {}
        motivo = datos.get("motivo")

        if not motivo or motivo.strip() == "":
            return jsonify({
                "mensaje": "Tenes que ingresar un motivo de cancelacion"
            }), 400

        viaje_model = ViajeModel.query.get(id_viaje)

        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        viaje = ViajeController.crear_objeto_viaje(viaje_model)

        if not viaje.cancelar(motivo):
            return jsonify({
                "mensaje": "No se pudo cancelar el viaje"
            }), 400

        ViajeController.actualizar_modelo_viaje(viaje_model, viaje)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo cancelar el viaje"
            }), 500

        return jsonify({
            "mensaje": "Viaje cancelado correctamente",
            "viaje": viaje_model.to_dict()
        }), 200