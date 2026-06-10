from flask import jsonify, request
from db_instance import db

from models.operador_model import OperadorModel
from utils.input_sanitizer import InputSanitizer


def listar_operadores():

    operadores = OperadorModel.query.all()

    return jsonify([operador.to_dict() for operador in operadores])


def obtener_operador(id_usuario):

    operador = OperadorModel.query.get(id_usuario)

    if operador is None:
        return jsonify({"mensaje": "Operador no encontrado"}), 404

    return jsonify(operador.to_dict())


def crear_operador():

    datos = InputSanitizer.sanitizar_campos(
        request.get_json(silent=True) or {},
        campos_texto=[
            "Legajo",
            "Sector",
        ],
        campos_enteros=["Usuario_idUsuario"],
    )

    nuevo_operador = OperadorModel(
        Usuario_idUsuario=datos["Usuario_idUsuario"],
        legajo=datos["Legajo"],
        sector=datos["Sector"],
    )

    db.session.add(nuevo_operador)
    db.session.commit()

    return jsonify(
        {
            "mensaje": "Operador creado correctamente",
            "operador": nuevo_operador.to_dict(),
        }
    )