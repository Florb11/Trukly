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
        # convierte UsuarioModel a Usuario de dominio
        if usuario_model is None:
            return None

        datos_usuario = usuario_model.to_dict()
        datos_usuario["password"] = usuario_model.password

        return Usuario.crear_desde_datos(datos_usuario)

    @staticmethod
    def _crear_validador_campos_obligatorios(campos):
        # crea un validador con campos obligatorios
        validador = ValidadorCompuesto()

        for campo in campos:
            validador.agregar(CampoObligatorio(campo))

        return validador

    @staticmethod
    def _crear_validador_registro_chofer():
        # valida campos y reglas para registrar chofer
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
        # valida campos obligatorios de login
        return AuthController._crear_validador_campos_obligatorios(
            AuthController.CAMPOS_LOGIN
        )

    @staticmethod
    def _sanitizar_datos_registro(datos):
        # limpia datos del registro
        return InputSanitizer.sanitizar_campos(
            datos,
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

    @staticmethod
    def _sanitizar_datos_login(datos):
        # limpia datos del login
        return InputSanitizer.sanitizar_campos(
            datos,
            campos_texto=["username"],
            campos_password=["password"],
        )

    @staticmethod
    def _validar_username_email_disponibles(username, email):
        # valida que username y email no esten repetidos
        usuario_existente = UsuarioModel.query.filter_by(
            username=username
        ).first()

        if usuario_existente:
            return False, "Ya existe un usuario con ese username"

        email_existente = UsuarioModel.query.filter_by(
            email=email
        ).first()

        if email_existente:
            return False, "Ya existe un usuario con ese email"

        return True, None

    @staticmethod
    def _crear_chofer_clase(datos, password_hash):
        # crea chofer de dominio desde datos validados
        vencimiento_licencia = Chofer.convertir_vencimiento_licencia(
            datos["vencimientoLicencia"]
        )

        return Chofer.crear_desde_datos(
            {
                "id_usuario": None,
                "username": datos["username"],
                "email": datos["email"],
                "password": password_hash,
                "nombre": datos["nombre"],
                "apellido": datos["apellido"],
                "estado": Usuario.ESTADO_PENDIENTE,
                "rol": Usuario.ROL_CHOFER,
                "licencia": datos["licencia"],
                "vencimientoLicencia": vencimiento_licencia,
                "legajo": datos["legajo"],
            }
        )

    @staticmethod
    def _crear_usuario_model_desde_chofer(chofer_clase):
        # convierte Chofer de dominio a UsuarioModel
        return UsuarioModel(
            username=chofer_clase.username,
            email=chofer_clase.email,
            password=chofer_clase.password,
            nombre=chofer_clase.nombre,
            apellido=chofer_clase.apellido,
            estado=chofer_clase.estado,
            rol=chofer_clase.rol,
        )

    @staticmethod
    def _crear_chofer_model_desde_chofer(chofer_clase):
        # convierte Chofer de dominio a ChoferModel
        return ChoferModel(
            Usuario_idUsuario=chofer_clase.id_usuario,
            licencia=chofer_clase.licencia,
            vencimientoLicencia=chofer_clase.vencimientoLicencia,
            legajo=chofer_clase.legajo,
        )

    @staticmethod
    def registrar_chofer():
        # recibe request de registro publico de chofer
        datos = AuthController._sanitizar_datos_registro(
            request.get_json(silent=True) or {}
        )

        # valida campos y reglas de dominio
        validador = AuthController._crear_validador_registro_chofer()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        # valida disponibilidad en BD
        datos_disponibles, mensaje_error = (
            AuthController._validar_username_email_disponibles(
                datos["username"],
                datos["email"]
            )
        )

        if not datos_disponibles:
            return jsonify({
                "mensaje": mensaje_error
            }), 409

        # hashea la contrasena
        password_hash = bcrypt.generate_password_hash(
            datos["password"]
        ).decode("utf-8")

        # crea objeto de dominio
        chofer_clase = AuthController._crear_chofer_clase(
            datos,
            password_hash
        )

        if chofer_clase is None:
            return jsonify({
                "mensaje": "No se pudo registrar el chofer"
            }), 400

        # convierte dominio a modelos
        nuevo_usuario = AuthController._crear_usuario_model_desde_chofer(
            chofer_clase
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.flush()

            chofer_clase.id_usuario = nuevo_usuario.id_usuario

            nuevo_chofer = AuthController._crear_chofer_model_desde_chofer(
                chofer_clase
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
        # recibe request de login
        datos = AuthController._sanitizar_datos_login(
            request.get_json(silent=True) or {}
        )

        # valida campos obligatorios
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

        if usuario_clase is None:
            return jsonify({
                "mensaje": "Usuario o contrasena incorrectos"
            }), 401

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
        