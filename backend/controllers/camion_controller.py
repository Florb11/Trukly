from flask import jsonify, request
from db_instance import db

from models.camion_model import CamionModel


def listar_camiones():

    camiones = CamionModel.query.all()

    return jsonify([camion.to_dict() for camion in camiones])


def obtener_camion(id_camion):

    camion = CamionModel.query.get(id_camion)

    if camion is None:
        return jsonify({"mensaje": "Camion no encontrado"}), 404

    return jsonify(camion.to_dict())


def crear_camion():

    datos = request.get_json()

    nuevo_camion = CamionModel(
        id_camion=datos["id_camion"],
        matricula=datos["matricula"],
        marca=datos["marca"],
        modelo=datos["modelo"],
        capacidad_carga=datos["capacidad_carga"],
        estado=datos["estado"],
        nroTanque=datos["nroTanque"],
    )

    db.session.add(nuevo_camion)
    db.session.commit()

    return jsonify(
        {
            "mensaje": "Camion creado correctamnete", 
         "mecanico": nuevo_camion.to_dict()
         }
    )
