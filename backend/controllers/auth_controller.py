from flask import jsonify, request
from db import db
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel


def registrar_chofer():
    # leo los datos que llegan en formato json
    datos = request.get_json()

    # valido que lleguen los datos necesarios
    campos_obligatorios = [
        "username",
        "password",
        "nombre",
        "apellido",
        "licencia",
        "vencimientoLicencia",
        "legajo"
    ]

    for campo in campos_obligatorios:
        if campo not in datos or datos[campo] == "":
            return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

    # reviso si ya existe un usuario con ese username
    usuario_existente = UsuarioModel.query.filter_by(username=datos["username"]).first()

    if usuario_existente:
        return jsonify({"mensaje": "Ya existe un usuario con ese username"}), 409

    # creo el usuario base con estado pendiente
    nuevo_usuario = UsuarioModel(
        username=datos["username"],
        password=datos["password"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        estado="pendiente"
    )

    db.session.add(nuevo_usuario)
    db.session.flush() #Eso sirve para que SQLAlchemy genere el id_usuario antes del commit, asi podemos usarlo para crear el Chofer

    # creo el chofer asociado al usuario creado
    nuevo_chofer = ChoferModel(
        Usuario_idUsuario=nuevo_usuario.id_usuario,
        licencia=datos["licencia"],
        vencimientoLicencia=datos["vencimientoLicencia"],
        legajo=datos["legajo"]
    )

    db.session.add(nuevo_chofer)
    db.session.commit()

    return jsonify({
        "mensaje": "Solicitud de registro enviada correctamente",
        "usuario": nuevo_usuario.to_dict(),
        "chofer": nuevo_chofer.to_dict()
    }), 201