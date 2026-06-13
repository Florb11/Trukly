from flask import jsonify

from models.usuario_model import UsuarioModel
from utils.auth_decorators import admin_required


class UsuarioController:

    @staticmethod
    @admin_required
    def listar_usuarios():
        # lista usuarios desde la base
        usuarios = UsuarioModel.query.all()

        return jsonify([
            usuario.to_dict()
            for usuario in usuarios
        ]), 200

    @staticmethod
    @admin_required
    def obtener_usuario(id_usuario):
        # busca un usuario por id
        usuario = UsuarioModel.query.get(id_usuario)

        if usuario is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        return jsonify(usuario.to_dict()), 200
