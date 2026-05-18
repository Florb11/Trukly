from flask import jsonify, request
from db import db
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from extensions import bcrypt
from flask_jwt_extended import create_access_token
from src.Usuario import Usuario




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
        "legajo",
    ]

    for campo in campos_obligatorios:
        if campo not in datos or datos[campo] == "":
            return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

    # reviso si ya existe un usuario con ese username
    usuario_existente = UsuarioModel.query.filter_by(username=datos["username"]).first()

    if usuario_existente:
        return jsonify({"mensaje": "Ya existe un usuario con ese username"}), 409
    
    password_hash = bcrypt.generate_password_hash(datos["password"]).decode("utf-8")

    # creo el usuario base con estado pendiente
    nuevo_usuario = UsuarioModel(
        username=datos["username"],
        password=password_hash,
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        estado="pendiente",
    )

    db.session.add(nuevo_usuario)
    db.session.flush()  # Eso sirve para que SQLAlchemy genere el id_usuario antes del commit, asi podemos usarlo para crear el Chofer

    # creo el chofer asociado al usuario creado
    nuevo_chofer = ChoferModel(
        Usuario_idUsuario=nuevo_usuario.id_usuario,
        licencia=datos["licencia"],
        vencimientoLicencia=datos["vencimientoLicencia"],
        legajo=datos["legajo"],
    )

    db.session.add(nuevo_chofer)
    db.session.commit()

    return (
        jsonify(
            {
                "mensaje": "Solicitud de registro enviada correctamente",
                "usuario": nuevo_usuario.to_dict(),
                "chofer": nuevo_chofer.to_dict(),
            }
        ),
        201,
    )
def login():
    # leo los datos enviados desde el frontend
    datos = request.get_json()

    # valido que lleguen usuario y contraseña
    if "username" not in datos or "password" not in datos:
        return jsonify({"mensaje": "Faltan datos para iniciar sesion"}), 400

    # busco el usuario por username
    usuario = UsuarioModel.query.filter_by(username=datos["username"]).first()

    # si no existe, devuelvo error
    if usuario is None:
        return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

    # creo un objeto de la clase Usuario para poder usar sus metodos
    usuario_clase = Usuario(
        usuario.id_usuario,
        usuario.username,
        usuario.password,
        usuario.nombre,
        usuario.apellido,
        usuario.estado
    )

    # uso el metodo iniciar_sesion de la clase Usuario
    password_correcta = usuario_clase.iniciar_sesion(datos["password"], bcrypt)

    if not password_correcta:
        return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

    # uso el metodo de la clase Usuario para revisar si esta activo
    if not usuario_clase.esta_activo():
        return jsonify({
            "mensaje": "La cuenta todavia no esta activa"
        }), 403

    # por ahora detectamos si es chofer
    rol = None

    chofer = ChoferModel.query.get(usuario.id_usuario)

    if chofer:
        rol = "chofer"

    # creo el token con datos basicos del usuario
    token = create_access_token(identity={
        "id_usuario": usuario.id_usuario,
        "username": usuario.username,
        "rol": rol
    })

    return jsonify({
        "mensaje": "Login correcto",
        "token": token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "username": usuario.username,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "estado": usuario.estado,
            "rol": rol
        }
    }), 200