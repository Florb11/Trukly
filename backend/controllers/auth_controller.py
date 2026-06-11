from flask import jsonify, request
from flask_jwt_extended import create_access_token

from db_instance import db
from extensions import bcrypt

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel

from src.Usuario import Usuario
from src.Chofer import Chofer
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidacionFuncion,
    ValidadorCompuesto,
)


logger = get_app_logger()


class AuthController:
    CAMPOS_REGISTRO_CHOFER = [
        "username",
        "password",
        "email",
        "nombre",
        "apellido",
        "licencia",
        "vencimientoLicencia",
        "legajo",
    ]

    CAMPOS_LOGIN = [
        "username",
        "password",
    ]

    @staticmethod
    def crear_objeto_usuario(usuario_model):
        return Usuario(
            usuario_model.id_usuario,
            usuario_model.username,
            usuario_model.email,
            usuario_model.password,
            usuario_model.nombre,
            usuario_model.apellido,
            usuario_model.estado,
            usuario_model.rol,
            usuario_model.foto_perfil,
        )

    @staticmethod
    def _crear_validador_campos_obligatorios(campos):
        validador = ValidadorCompuesto()

        for campo in campos:
            validador.agregar(CampoObligatorio(campo))

        return validador

    @staticmethod
    def _crear_validador_registro_chofer():
        validador = AuthController._crear_validador_campos_obligatorios(
            AuthController.CAMPOS_REGISTRO_CHOFER
        )

        validador.agregar(
            ValidacionFuncion(
                "password",
                Usuario.validar_password_registro
            )
        )
        validador.agregar(
            ValidacionFuncion(
                "licencia",
                Chofer.validar_licencia
            )
        )
        validador.agregar(
            ValidacionFuncion(
                "vencimientoLicencia",
                Chofer.validar_vencimiento_licencia
            )
        )

        return validador

    @staticmethod
    def _crear_validador_login():
        return AuthController._crear_validador_campos_obligatorios(
            AuthController.CAMPOS_LOGIN
        )

    @staticmethod
    def registrar_chofer():
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=[
                "username",
                "nombre",
                "apellido",
                "licencia",
                "vencimientoLicencia",
                "legajo",
            ],
            campos_email=["email"],
            campos_password=["password"],
        )

        validador = AuthController._crear_validador_registro_chofer()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        usuario_existente = UsuarioModel.query.filter_by(
            username=datos["username"]
        ).first()

        if usuario_existente:
            return jsonify({
                "mensaje": "Ya existe un usuario con ese username"
            }), 409

        email_existente = UsuarioModel.query.filter_by(
            email=datos["email"]
        ).first()

        if email_existente:
            return jsonify({
                "mensaje": "Ya existe un usuario con ese email"
            }), 409

        vencimiento_licencia = Chofer.convertir_vencimiento_licencia(
            datos["vencimientoLicencia"]
        )

        password_hash = bcrypt.generate_password_hash(
            datos["password"]
        ).decode("utf-8")

        chofer_clase = Chofer(
            None,
            datos["username"],
            datos["email"],
            password_hash,
            datos["nombre"],
            datos["apellido"],
            Usuario.ESTADO_PENDIENTE,
            Usuario.ROL_CHOFER,
            datos["licencia"],
            vencimiento_licencia,
            datos["legajo"],
        )

        nuevo_usuario = UsuarioModel(
            username=chofer_clase.username,
            email=chofer_clase.email,
            password=chofer_clase.password,
            nombre=chofer_clase.nombre,
            apellido=chofer_clase.apellido,
            estado=chofer_clase.estado,
            rol=chofer_clase.rol,
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.flush()

            chofer_clase.id_usuario = nuevo_usuario.id_usuario

            nuevo_chofer = ChoferModel(
                Usuario_idUsuario=chofer_clase.id_usuario,
                licencia=chofer_clase.licencia,
                vencimientoLicencia=chofer_clase.vencimientoLicencia,
                legajo=chofer_clase.legajo,
            )

            db.session.add(nuevo_chofer)
            db.session.commit()

        except Exception:
            db.session.rollback()
            logger.exception("No se pudo registrar el chofer")

            return jsonify({
                "mensaje": "No se pudo registrar el chofer"
            }), 500

        return jsonify({
            "mensaje": "Solicitud de registro enviada correctamente",
            "usuario": nuevo_usuario.to_dict(),
            "chofer": nuevo_chofer.to_dict(),
        }), 201

    @staticmethod
    def login():
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["username"],
            campos_password=["password"],
        )

        validador = AuthController._crear_validador_login()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({
                "mensaje": mensaje_error
            }), 400

        usuario = UsuarioModel.query.filter_by(
            username=datos["username"]
        ).first()

        if usuario is None:
            logger.warning(
                "Login fallido: usuario inexistente %s",
                datos.get("username")
            )

            return jsonify({
                "mensaje": "Usuario o contrasena incorrectos"
            }), 401

        usuario_clase = AuthController.crear_objeto_usuario(usuario)

        password_correcta = usuario_clase.verificar_password(
            datos["password"],
            bcrypt
        )

        if not password_correcta:
            logger.warning(
                "Login fallido: contrasena incorrecta para %s",
                datos.get("username")
            )

            return jsonify({
                "mensaje": "Usuario o contrasena incorrectos"
            }), 401

        if not usuario_clase.esta_activo():
            logger.warning(
                "Login rechazado: usuario inactivo %s",
                datos.get("username")
            )

            return jsonify({
                "mensaje": "La cuenta todavia no esta activa"
            }), 403

        token = create_access_token(
            identity=str(usuario_clase.id_usuario),
            additional_claims={
                "username": usuario_clase.username,
                "rol": usuario_clase.rol,
            }
        )

        return jsonify({
            "mensaje": "Login correcto",
            "token": token,
            "usuario": usuario_clase.to_dict(),
        }), 200
        