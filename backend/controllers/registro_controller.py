from flask import jsonify, request
from db_instance import db

from models.registro_model import RegistroModel


def listar_registros():
    
    registros = RegistroModel.query.all()

    return jsonify([registro.to_dict() for registro in registros])


def obtener_registro(id_registro):

    registro = RegistroModel.query.get(id_registro)

    if registro is None:
        return jsonify({"mensaje": "Registro no encontrado"}), 404

    return jsonify(registro.to_dict())


def crear_registro():
    datos = request.get_json()

    nuevo_registro = RegistroModel(
        fecha_hora=datos["fecha_hora"],
        tipo_registro=datos["tipo_registro"],
        observacion=datos.get(
            "observacion"
        ), 
        Viaje_id_viaje=datos["Viaje_id_viaje"],
    )

    db.session.add(nuevo_registro)
    db.session.commit()

    return jsonify(
        {
            "mensaje": "Registro creado correctamente",
            "registro": nuevo_registro.to_dict(),
        }
    )
