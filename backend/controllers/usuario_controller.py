from flask import jsonify, request
from db import db
from models.usuario_model import UsuarioModel


def listar_usuarios():
    # busco todos los usuarios guardados en la base
    usuarios = UsuarioModel.query.all()

    # convierto cada usuario a diccionario para poder devolverlo como json
    return jsonify([usuario.to_dict() for usuario in usuarios])


def obtener_usuario(id_usuario):
    # busco un usuario por su id
    usuario = UsuarioModel.query.get(id_usuario)

    # si no existe, devuelvo un mensaje de error
    if usuario is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    # si existe, lo convierto a diccionario y lo devuelvo como json
    return jsonify(usuario.to_dict())


def crear_usuario():
    # leo los datos que llegan en formato json desde el frontend
    datos = request.get_json()

    # creo un nuevo usuario con los datos recibidos
    nuevo_usuario = UsuarioModel(
        username=datos["username"],
        password=datos["password"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        estado=datos["estado"],
    )

    # agrego el usuario a la sesion de la base
    db.session.add(nuevo_usuario)

    # confirmo el cambio para que se guarde en mysql
    db.session.commit()

    # devuelvo un mensaje y los datos del usuario creado
    return (
        jsonify(
            {
                "mensaje": "Usuario creado correctamente",
                "usuario": nuevo_usuario.to_dict(),
            }
        ),
        201,
    )
