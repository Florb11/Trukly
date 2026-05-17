from flask import jsonify, request
from db import db
from models.mecanico_model import MecanicoModel


def listar_mecanicos():

    mecanicos = MecanicoModel.query.all()

    return jsonify([mecanico.to_dict() for mecanico in mecanicos])


def obtener_mecanico(id_usuario):

    mecanico = MecanicoModel.query.get(id_usuario)

    if mecanico is None:
        return jsonify({"mensaje": "Mecanico no encontrador "}), 404

    return jsonify(mecanico.to_dict())


def crear_mecanico():

    datos = request.get_json()

    nuevo_mecanico = MecanicoModel(
        Usuario_idUsuario=datos["Usuario_idUsuario"],
        legajo=datos["Legajo"],
        especialidad=datos["Especialidad"],
    )

    db.session.add(nuevo_mecanico)
    db.session.commit()

    return jsonify(
        {
            "mensaje": "Mecanico creado correctamente",
            "mecanico": nuevo_mecanico.to_dict(),
        }
    )
