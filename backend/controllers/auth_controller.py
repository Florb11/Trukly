from flask import jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy import or_

from db_instance import db
from extensions import bcrypt

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from services.firebase_service import FirebaseAuthService, FirebaseConfigError

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
    ]

    CAMPOS_LOGIN = [
        "username",
        "password",
    ]

    CAMPOS_REGISTRO_FIREBASE_CHOFER = [
        "firebaseToken",
        "username",
        "email",
        "nombre",
        "apellido",
    ]

    @staticmethod
    def crear_objeto_usuario(usuario_model):
        # convierte UsuarioModel a objeto usuario
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
    def _crear_validador_registro_firebase_chofer():
        validador = AuthController._crear_validador_campos_obligatorios(
            AuthController.CAMPOS_REGISTRO_FIREBASE_CHOFER
        )

        return validador

    @staticmethod
    def _crear_validador_datos_chofer():
        validador = AuthController._crear_validador_campos_obligatorios(
            [
                "licencia",
                "vencimientoLicencia",
                "legajo",
            ]
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
    def _sanitizar_datos_registro_firebase(datos):
        return InputSanitizer.sanitizar_campos(
            datos,
            campos_texto=[
                "firebaseToken",
                "username",
                "nombre",
                "apellido",
                "licencia",
                "vencimientoLicencia",
                "legajo",
            ],
            campos_email=["email"],
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
        # crea chofer obj desde datos validados
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
        # convierte Chofer obj a UsuarioModel
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
    def _crear_usuario_model_firebase(datos, password_hash, firebase_uid):
        return UsuarioModel(
            username=datos["username"],
            email=datos["email"],
            password=password_hash,
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            estado=Usuario.ESTADO_PENDIENTE,
            rol=Usuario.ROL_CHOFER,
            firebase_uid=firebase_uid,
        )

    @staticmethod
    def _crear_usuario_model_chofer_pendiente(datos, password_hash):
        return UsuarioModel(
            username=datos["username"],
            email=datos["email"],
            password=password_hash,
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            estado=Usuario.ESTADO_PENDIENTE,
            rol=Usuario.ROL_CHOFER,
        )

    @staticmethod
    def _perfil_completo_usuario(usuario_model):
        if usuario_model.rol != Usuario.ROL_CHOFER:
            return True

        chofer = ChoferModel.query.get(usuario_model.id_usuario)

        return bool(
            chofer
            and chofer.licencia
            and chofer.vencimientoLicencia
            and chofer.legajo
        )

    @staticmethod
    def _usuario_to_dict_con_perfil(usuario_model):
        datos_usuario = usuario_model.to_dict()
        datos_usuario["perfil_completo"] = (
            AuthController._perfil_completo_usuario(usuario_model)
        )

        return datos_usuario

    @staticmethod
    def _crear_chofer_model_desde_chofer(chofer_clase):
        # convierte Chofer a ChoferModel
        return ChoferModel(
            Usuario_idUsuario=chofer_clase.id_usuario,
            licencia=chofer_clase.licencia,
            vencimientoLicencia=chofer_clase.vencimientoLicencia,
            legajo=chofer_clase.legajo,
        )

    @staticmethod
    def _crear_respuesta_login(usuario_clase):
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
            "usuario": AuthController._usuario_to_dict_con_perfil(usuario_clase),
        }), 200

    @staticmethod
    def registrar_chofer():
        # recibe request de registro publico de chofer
        datos = AuthController._sanitizar_datos_registro(
            request.get_json(silent=True) or {}
        )

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

        nuevo_usuario = AuthController._crear_usuario_model_chofer_pendiente(
            datos,
            password_hash
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()

        except Exception:
            db.session.rollback()
            logger.exception("No se pudo registrar el chofer")

            return jsonify({
                "mensaje": "No se pudo registrar el chofer"
            }), 500

        return jsonify({
            "mensaje": "Solicitud de registro enviada correctamente",
            "usuario": AuthController._usuario_to_dict_con_perfil(nuevo_usuario),
            "chofer": None,
        }), 201

    @staticmethod
    def registrar_chofer_firebase():
        datos = AuthController._sanitizar_datos_registro_firebase(
            request.get_json(silent=True) or {}
        )

        validador = AuthController._crear_validador_registro_firebase_chofer()
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return jsonify({"mensaje": mensaje_error}), 400

        try:
            firebase_usuario = FirebaseAuthService.verificar_token(
                datos["firebaseToken"]
            )
        except FirebaseConfigError as error:
            logger.exception("Firebase Admin no está configurado")
            return jsonify({"mensaje": str(error)}), 500
        except Exception:
            logger.exception("No se pudo verificar el token de Firebase")
            return jsonify({"mensaje": "Token de Firebase inválido"}), 401

        firebase_uid = firebase_usuario.get("uid")
        firebase_email = firebase_usuario.get("email")

        emails_coinciden = (
            firebase_email
            and firebase_email.lower() == datos["email"].lower()
        )

        if not firebase_uid or not emails_coinciden:
            return jsonify({
                "mensaje": "El email no coincide con la cuenta de Firebase"
            }), 400

        datos_disponibles, mensaje_error = (
            AuthController._validar_username_email_disponibles(
                datos["username"],
                datos["email"]
            )
        )

        if not datos_disponibles:
            return jsonify({"mensaje": mensaje_error}), 409

        firebase_uid_existente = UsuarioModel.query.filter_by(
            firebase_uid=firebase_uid
        ).first()

        if firebase_uid_existente:
            return jsonify({
                "mensaje": "Ya existe un usuario vinculado a esa cuenta de Firebase"
            }), 409

        password_hash = bcrypt.generate_password_hash(
            f"firebase:{firebase_uid}"
        ).decode("utf-8")

        nuevo_usuario = AuthController._crear_usuario_model_firebase(
            datos,
            password_hash,
            firebase_uid
        )
        nuevo_chofer = None
        campos_chofer = [
            datos.get("licencia"),
            datos.get("vencimientoLicencia"),
            datos.get("legajo"),
        ]

        if any(campos_chofer):
            validador_chofer = AuthController._crear_validador_datos_chofer()
            datos_validos, mensaje_error = validador_chofer.validar(datos)

            if not datos_validos:
                return jsonify({"mensaje": mensaje_error}), 400

        try:
            db.session.add(nuevo_usuario)
            db.session.flush()

            if any(campos_chofer):
                chofer_clase = AuthController._crear_chofer_clase(
                    datos,
                    password_hash
                )

                if chofer_clase is None:
                    return jsonify({
                        "mensaje": "No se pudo registrar el chofer"
                    }), 400

                chofer_clase.id_usuario = nuevo_usuario.id_usuario
                nuevo_chofer = AuthController._crear_chofer_model_desde_chofer(
                    chofer_clase
                )
                db.session.add(nuevo_chofer)

            db.session.commit()

        except Exception:
            db.session.rollback()
            logger.exception("No se pudo registrar el chofer con Firebase")

            return jsonify({
                "mensaje": "No se pudo registrar el chofer"
            }), 500

        return jsonify({
            "mensaje": "Solicitud de registro enviada correctamente",
            "usuario": AuthController._usuario_to_dict_con_perfil(nuevo_usuario),
            "chofer": nuevo_chofer.to_dict() if nuevo_chofer else None,
        }), 201

    @staticmethod
    def login_firebase():
        datos = request.get_json(silent=True) or {}
        firebase_token = datos.get("token")

        if not firebase_token:
            return jsonify({"mensaje": "Falta el token de Firebase"}), 400

        try:
            firebase_usuario = FirebaseAuthService.verificar_token(
                firebase_token
            )
        except FirebaseConfigError as error:
            logger.exception("Firebase Admin no está configurado")
            return jsonify({"mensaje": str(error)}), 500
        except Exception:
            logger.exception("No se pudo verificar el token de Firebase")
            return jsonify({"mensaje": "Token de Firebase inválido"}), 401

        firebase_uid = firebase_usuario.get("uid")
        firebase_email = firebase_usuario.get("email")

        usuario = UsuarioModel.query.filter(
            or_(
                UsuarioModel.firebase_uid == firebase_uid,
                UsuarioModel.email == firebase_email,
            )
        ).first()

        if usuario is None:
            return jsonify({
                "mensaje": (
                    "La cuenta existe en Firebase, pero todavía no tiene "
                    "solicitud de alta en Trukly. Registrate primero desde "
                    "Solicitá acceso."
                )
            }), 404

        if not usuario.firebase_uid:
            usuario.firebase_uid = firebase_uid
            db.session.commit()

        usuario_clase = AuthController.crear_objeto_usuario(usuario)

        if usuario_clase is None or not usuario_clase.esta_activo():
            return jsonify({
                "mensaje": "Tu cuenta se encuentra desactivada o pendiente de aprobación"
            }), 403

        return AuthController._crear_respuesta_login(usuario_clase)

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

        usuario = UsuarioModel.query.filter(
            or_(
                UsuarioModel.username == datos["username"],
                UsuarioModel.email == datos["username"],
            )
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
                "mensaje": "Tu cuenta se encuentra desactivada. Contactá al administrador"
            }), 403

        return AuthController._crear_respuesta_login(usuario_clase)
        
