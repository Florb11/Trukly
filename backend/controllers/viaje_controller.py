from flask import jsonify, request
from db_instance import db

from models.viaje_model import ViajeModel


def listar_viajes():

    viajes = ViajeModel.query.all()

    return jsonify([viaje.to_dict() for viaje in viajes])


def obtener_viaje(id_viaje):

    viaje = ViajeModel.query.get(id_viaje)

    if viaje is None:
        return jsonify({"mensaje": "Viaje no encontrado"}), 404 
    
    return jsonify(viaje.to_dict())



def crear_viaje():
    datos = request.get_json()

    nuevo_viaje = ViajeModel(
        fecha_salida=datos["fecha_salida"],
        fecha_llegada=datos["fecha_llegada"],
        origen=datos["origen"],
        destino=datos["destino"],
        estado=datos["estado"],
        observaciones=datos["observaciones"],
        recorrido=datos["recorrido"],
        OperadorLogistico_Usuario_idUsuario=datos["OperadorLogistico_Usuario_idUsuario"],
        Chofer_Usuario_idUsuario=datos["Chofer_Usuario_idUsuario"],
        Camion_id_camion=datos["Camion_id_camion"]
    )

    db.session.add(nuevo_viaje)
    db.session.commit()

    return jsonify(
        {
            "mensaje": "Viaje creado correctamente",
            "viaje": nuevo_viaje.to_dict(),
        }
    )