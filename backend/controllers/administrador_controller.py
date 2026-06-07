from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from db_instance import db

from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel

from src.Administrador import Administrador


class AdministradorController:

    @staticmethod
    def listar_administradores():
        administradores = AdministradorModel.query.all()

        return jsonify([
            administrador.to_dict()
            for administrador in administradores
        ]), 200

    @staticmethod
    def obtener_administrador(id_usuario):
        administrador = AdministradorModel.query.get(id_usuario)

        if administrador is None:
            return jsonify({
                "mensaje": "Administrador no encontrado"
            }), 404

        return jsonify(administrador.to_dict()), 200

    @staticmethod
    def crear_administrador():
        datos = request.get_json()

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        if not datos.get("Usuario_idUsuario"):
            return jsonify({
                "mensaje": "Falta el campo Usuario_idUsuario"
            }), 400

        if not datos.get("legajo"):
            return jsonify({
                "mensaje": "Falta el campo legajo"
            }), 400

        nuevo_administrador = AdministradorModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["legajo"]
        )

        db.session.add(nuevo_administrador)
        db.session.commit()

        return jsonify({
            "mensaje": "Administrador creado correctamente",
            "administrador": nuevo_administrador.to_dict()
        }), 201

    @staticmethod
    def obtener_admin_actual():
        id_usuario = get_jwt_identity()
        datos_token = get_jwt()

        if not id_usuario:
            return None

        if datos_token.get("rol") != "admin":
            return None

        usuario = UsuarioModel.query.get(int(id_usuario))

        if usuario is None:
            return None

        administrador = AdministradorModel.query.get(
            usuario.id_usuario
        )

        if administrador is None:
            return None

        return Administrador(
            usuario.id_usuario,
            usuario.username,
            usuario.email,
            usuario.password,
            usuario.nombre,
            usuario.apellido,
            usuario.estado,
            usuario.rol,
            administrador.legajo,
        )