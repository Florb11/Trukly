from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from db_instance import db
from models.viaje_model import ViajeModel
from src.Viaje import Viaje


class ViajeController:
  
    @staticmethod
    def listar_viajes():
        viajes = ViajeModel.query.all()
        return jsonify([viaje.to_dict() for viaje in viajes]), 200

    @staticmethod
    def obtener_viaje(id_viaje):
        viaje = ViajeModel.query.get(id_viaje)

        if viaje is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        return jsonify(viaje.to_dict()), 200

    @staticmethod
    def crear_viaje():
        datos = request.get_json()

        if not datos:
            return jsonify({"mensaje": "No se recibieron datos"}), 400

        campos_obligatorios = [
            "fecha_salida",
            "origen",
            "destino",
            "estado",
            "recorrido",
            "OperadorLogistico_Usuario_idUsuario",
            "Chofer_Usuario_idUsuario",
            "Camion_id_camion"
        ]

        for campo in campos_obligatorios:
            if campo not in datos:
                return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

        nuevo_viaje = ViajeModel(
            fecha_salida=datos["fecha_salida"],
            fecha_llegada=datos.get("fecha_llegada"),
            origen=datos["origen"],
            destino=datos["destino"],
            estado=datos["estado"],
            observaciones=datos.get("observaciones"),
            recorrido=datos["recorrido"],
            OperadorLogistico_Usuario_idUsuario=datos["OperadorLogistico_Usuario_idUsuario"],
            Chofer_Usuario_idUsuario=datos["Chofer_Usuario_idUsuario"],
            Camion_id_camion=datos["Camion_id_camion"]
        )

        db.session.add(nuevo_viaje)
        db.session.commit()

        return jsonify({
            "mensaje": "Viaje creado correctamente",
            "viaje": nuevo_viaje.to_dict(),
        }), 201

   
    # RUTAS ADMIN - SUPERVISION

    @staticmethod
    @jwt_required()
    def listar_viajes_admin():
        datos_token = get_jwt()

        if datos_token.get("rol") != "admin":
            return jsonify({"mensaje": "No tenes permiso para ver los viajes"}), 403

        viajes = ViajeModel.query.all()

        return jsonify([viaje.to_dict() for viaje in viajes]), 200

    @staticmethod
    @jwt_required()
    def obtener_viaje_admin(id_viaje):
        datos_token = get_jwt()

        if datos_token.get("rol") != "admin":
            return jsonify({"mensaje": "No tenes permiso para ver este viaje"}), 403

        viaje = ViajeModel.query.get(id_viaje)

        if viaje is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        return jsonify(viaje.to_dict()), 200

    @staticmethod
    @jwt_required()
    def cancelar_viaje_admin(id_viaje):
        datos_token = get_jwt()

        if datos_token.get("rol") != "admin":
            return jsonify({"mensaje": "No tenes permiso para cancelar viajes"}), 403

        datos = request.get_json()

        if not datos:
            return jsonify({"mensaje": "No se recibieron datos"}), 400

        motivo = datos.get("motivo")

        if not motivo or motivo.strip() == "":
            return jsonify({"mensaje": "Tenes que ingresar un motivo de cancelacion"}), 400

        viaje_model = ViajeModel.query.get(id_viaje)

        if viaje_model is None:
            return jsonify({"mensaje": "Viaje no encontrado"}), 404

        viaje = Viaje(
            id_viaje=viaje_model.id_viaje,
            fecha_salida=viaje_model.fecha_salida,
            fecha_llegada=viaje_model.fecha_llegada,
            origen=viaje_model.origen,
            destino=viaje_model.destino,
            estado=viaje_model.estado,
            observaciones=viaje_model.observaciones,
            recorrido=viaje_model.recorrido,
            OperadorLogistico_Usuario_idUsuario=viaje_model.OperadorLogistico_Usuario_idUsuario,
            Chofer_Usuario_idUsuario=viaje_model.Chofer_Usuario_idUsuario,
            Camion_id_camion=viaje_model.Camion_id_camion
        )

        if not viaje.cancelar(motivo):
            return jsonify({"mensaje": "No se pudo cancelar el viaje"}), 400

        viaje_model.estado = viaje.estado
        viaje_model.observaciones = viaje.observaciones

        db.session.commit()

        return jsonify({
            "mensaje": "Viaje cancelado correctamente",
            "viaje": viaje_model.to_dict()
        }), 200