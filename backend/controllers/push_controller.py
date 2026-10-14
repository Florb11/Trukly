from hashlib import sha256

from flask import g, jsonify, request
from db_instance import db
from models.push_dispositivo_model import PushDispositivoModel
from utils.auth_decorators import usuario_required
from utils.app_logger import get_app_logger


class PushController:
    @staticmethod
    @usuario_required
    def dispositivo():
        token = (request.get_json(silent=True) or {}).get("token")
        if not isinstance(token, str) or not token.strip() or len(token) > 4096:
            return jsonify({"mensaje": "Token de dispositivo invalido"}), 400
        token_hash = sha256(token.encode()).hexdigest()
        try:
            dispositivo = PushDispositivoModel.query.filter_by(token_hash=token_hash).first()
            if request.method == "DELETE":
                if dispositivo and dispositivo.Usuario_idUsuario == g.usuario_actual.id_usuario:
                    db.session.delete(dispositivo)
            else:
                if dispositivo is None:
                    dispositivo = PushDispositivoModel(token_hash=token_hash, token=token)
                    db.session.add(dispositivo)
                dispositivo.Usuario_idUsuario = g.usuario_actual.id_usuario
            db.session.commit()
            return jsonify({"mensaje": "Dispositivo actualizado"}), 200
        except Exception:
            db.session.rollback()
            get_app_logger().exception("No se pudo actualizar el dispositivo push")
            return jsonify({"mensaje": "No se pudo registrar el dispositivo"}), 500
