from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from db import db
from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.operador_model import OperadorModel
from src.Administrador import Administrador
from src.Usuario import Usuario



# funcion para listar todos los administradores
def listar_administradores():
    administradores = AdministradorModel.query.all()

    return jsonify([administrador.to_dict() for administrador in administradores])


def obtener_administrador(id_usuario):
    # busco administrador por id
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
        "administrador": nuevo_administrador.to_dict(),
    })


def obtener_admin_actual():
    # leo el id del usuario desde el token
    id_usuario = get_jwt_identity()

    # leo los datos extra del token, como el rol
    datos_token = get_jwt()

    if not id_usuario:
        return None

    # si el token no tiene rol admin, no dejo crear el objeto administrador
    if datos_token.get("rol") != "admin":
        return None

    # busco el usuario completo en la base
    usuario = UsuarioModel.query.get(int(id_usuario))

    if usuario is None:
        return None

    # busco los datos especificos del administrador
    administrador = AdministradorModel.query.get(usuario.id_usuario)

    if administrador is None:
        return None

    # creo el objeto administrador con datos de usuario y datos propios del admin
    admin = Administrador(
        usuario.id_usuario,
        usuario.username,
        usuario.password,
        usuario.nombre,
        usuario.apellido,
        usuario.estado,
        usuario.rol,
        administrador.legajo,
    )

    return admin


@jwt_required()
def activar_usuario(id_usuario):
    # obtengo el administrador que esta haciendo la accion
    admin = obtener_admin_actual()

    # si no se pudo obtener un admin valido, no tiene permiso
    if admin is None:
        return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

    # busco el usuario en la base
    usuario_db = UsuarioModel.query.get(id_usuario)

    if usuario_db is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    # paso los datos del modelo a un objeto Usuario para poder acceder a sus metodos
    usuario_clase = Usuario(
        usuario_db.id_usuario,
        usuario_db.username,
        usuario_db.password,
        usuario_db.nombre,
        usuario_db.apellido,
        usuario_db.estado,
        usuario_db.rol,
    )

    # la clase administrador valida y cambia el estado del usuario 
    accion_realizada = admin.activar_usuario(usuario_clase)

    if not accion_realizada:
        return jsonify({"mensaje": "Este usuario no se puede activar"}), 400

    # el controller pasa el cambio al modelo y guarda en la base
    usuario_db.estado = usuario_clase.estado

    db.session.commit()

    return jsonify({
        "mensaje": "Usuario activado correctamente",
        "usuario": usuario_db.to_dict()
    }), 200
    
@jwt_required()
def desactivar_usuario(id_usuario):
    # obtengo el administrador que esta haciendo la accion
    admin = obtener_admin_actual()

    # si no se pudo obtener un admin valido, no tiene permiso
    if admin is None:
        return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

    # busco el usuario en la base
    usuario_db = UsuarioModel.query.get(id_usuario)

    if usuario_db is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    # paso los datos del modelo a un objeto Usuario 
    usuario_clase = Usuario(
        usuario_db.id_usuario,
        usuario_db.username,
        usuario_db.password,
        usuario_db.nombre,
        usuario_db.apellido,
        usuario_db.estado,
        usuario_db.rol,
    )

    # la clase administrador valida y cambia el estado del usuario 
    accion_realizada = admin.desactivar_usuario(usuario_clase)

    if not accion_realizada:
        return jsonify({"mensaje": "Este usuario no se puede desactivar"}), 400

    # el controller copia el cambio al modelo y guarda en la base
    usuario_db.estado = usuario_clase.estado

    db.session.commit()

    return jsonify({
        "mensaje": "Usuario desactivado correctamente",
        "usuario": usuario_db.to_dict()
    }), 200
   
@jwt_required()
def listar_usuarios_pendientes():
    # obtengo el administrador que esta haciendo la accion
    admin = obtener_admin_actual()

    # si no se pudo obtener un admin valido, no tiene permiso
    if admin is None:
        return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

    # busco todos los usuarios que todavia estan pendientes
    usuarios_pendientes = UsuarioModel.query.filter_by(
        estado="pendiente"
    ).all()

    usuarios = []

    for usuario in usuarios_pendientes:
        datos_usuario = usuario.to_dict()

        # si el usuario pendiente es chofer, agrego sus datos especificos
        if usuario.rol == "chofer":
            chofer = ChoferModel.query.get(usuario.id_usuario)

            if chofer:
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )
                datos_usuario["legajo"] = chofer.legajo

        usuarios.append(datos_usuario)

    return jsonify({
        "mensaje": "Usuarios pendientes obtenidos correctamente",
        "usuarios": usuarios
    }), 200
    
@jwt_required()
def listar_usuarios():
    # obtengo el administrador que esta haciendo la accion
    admin = obtener_admin_actual()

    # si no se pudo obtener un admin valido, no tiene permiso
    if admin is None:
        return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

    # busco todos los usuarios
    usuarios_db = UsuarioModel.query.all()

    usuarios = []

    for usuario in usuarios_db:
        datos_usuario = usuario.to_dict()

        # si es chofer, agrego datos propios del chofer
        if usuario.rol == "chofer":
            chofer = ChoferModel.query.get(usuario.id_usuario)

            if chofer:
                datos_usuario["legajo"] = chofer.legajo
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )

        # si es administrador, agrego datos propios del administrador
        elif usuario.rol == "admin":
            administrador = AdministradorModel.query.get(usuario.id_usuario)

            if administrador:
                datos_usuario["legajo"] = administrador.legajo

        # si es mecanico, agrego datos propios del mecanico
        elif usuario.rol == "mecanico":
            mecanico = MecanicoModel.query.get(usuario.id_usuario)

            if mecanico:
                datos_usuario["legajo"] = mecanico.legajo
                datos_usuario["especialidad"] = mecanico.especialidad

        # si es operador, agrego datos propios del operador logistico
        elif usuario.rol == "operador":
            operador = OperadorModel.query.get(usuario.id_usuario)

            if operador:
                datos_usuario["legajo"] = operador.legajo
                datos_usuario["sector"] = operador.sector

        usuarios.append(datos_usuario)

    return jsonify({
        "mensaje": "Usuarios obtenidos correctamente",
        "usuarios": usuarios
    }), 200