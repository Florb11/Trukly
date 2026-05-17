from flask import jsonify, request
from db import db
from models.administrador_model import AdministradorModel


# funcion para listar todos los administradores

def listar_administradores():

    administradores = AdministradorModel.query.all()

    return jsonify ([administrador.to_dict() for administrador in administradores])

def obtener_administrador(id_usuario):
    # Busco administrador por id

    administrador = AdministradorModel.query.get(id_usuario)

    if administrador is None:
        return jsonify({"mensaje": "Administrador no encontrado"}), 404
    
    return jsonify(administrador.to_dict())

# funcion para crear administradores

def crear_administrador():
    datos = request.get_json()

    nuevo_administrador = AdministradorModel(
        Usuario_idUsuario=datos["Usuario_idUsuario"],
        legajo=datos["legajo"]
    )

    db.session.add(nuevo_administrador)
    db.session.commit()

    return jsonify({
        "mensaje": "Administrador creado correctamente",
        "administrador": nuevo_administrador.to_dict()
    })