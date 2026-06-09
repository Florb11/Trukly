from flask import jsonify, request
from flask_jwt_extended import create_access_token

from db_instance import db
from extensions import bcrypt

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel

from src.Usuario import Usuario
from src.Chofer import Chofer


class AuthController:
#Controlador
#Recibe el request del frontend
#Valida que lleguen los datos necesarios
#Consulta la base de datos usando los Modelos
#Crea objetos de las clases 
#Le delega las decisiones a esas clases
#Arma el token JWT
#Devuelve la respuesta HTTP al frontend

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
    def registrar_chofer():
        datos = request.get_json(silent=True) or {}

        campos_obligatorios = [
            "username",
            "password",
            "email",
            "nombre",
            "apellido",
            "licencia",
            "vencimientoLicencia",
            "legajo",
        ]

        for campo in campos_obligatorios:
            if campo not in datos or str(datos[campo]).strip() == "":
                return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

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

        password_valida, mensaje_error = (
            Usuario.validar_password_registro(datos["password"])
        )

        if not password_valida:
            return jsonify({"mensaje": mensaje_error}), 400

        licencia_valida, mensaje_error = Chofer.validar_licencia(
            datos["licencia"]
        )

        if not licencia_valida:
            return jsonify({"mensaje": mensaje_error}), 400

        vencimiento_valido, mensaje_error = (
            Chofer.validar_vencimiento_licencia(
                datos["vencimientoLicencia"]
            )
        )

        if not vencimiento_valido:
            return jsonify({"mensaje": mensaje_error}), 400

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
            "pendiente",
            "chofer",
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
        datos = request.get_json(silent=True) or {}

        if not datos.get("username") or not datos.get("password"):
            return jsonify({
                "mensaje": "Faltan datos para iniciar sesion"
            }), 400

        usuario = UsuarioModel.query.filter_by(
            username=datos["username"]
        ).first()

        if usuario is None:
            return jsonify({
                "mensaje": "Usuario o contrasena incorrectos"
            }), 401

        usuario_clase = AuthController.crear_objeto_usuario(usuario)

        password_correcta = usuario_clase.verificar_password(
            datos["password"],
            bcrypt
        )

        if not password_correcta:
            return jsonify({
                "mensaje": "Usuario o contrasena incorrectos"
            }), 401

        if not usuario_clase.esta_activo():
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
        