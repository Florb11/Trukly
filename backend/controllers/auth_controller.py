from flask import jsonify, request
from db_instance import db

from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from extensions import bcrypt
from flask_jwt_extended import create_access_token
from src.Usuario import Usuario
from src.Chofer import Chofer

#Controlador
#Recibe el request del frontend
#Valida que lleguen los datos necesarios
#Consulta la base de datos usando los Modelos
#Crea objetos de las clases 
#Le delega las decisiones a esas clases
#Arma el token JWT
#Devuelve la respuesta HTTP al frontend
class AuthController:

    @staticmethod
    def registrar_chofer():
        # recibe los datos que vienen desde el frontend
        datos = request.get_json()

        # valida que el request tenga los campos necesarios
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
            if campo not in datos or datos[campo] == "":
                return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

        # consulta la base para revisar si ya existe ese username
        usuario_existente = UsuarioModel.query.filter_by(
            username=datos["username"]
        ).first()
   
        if usuario_existente:
            return jsonify({"mensaje": "Ya existe un usuario con ese username"}), 409
        # consulta la base para revisar si ya existe ese email
        email_existente = UsuarioModel.query.filter_by(
            email=datos["email"]
        ).first()
        
        if email_existente:
            return jsonify({"mensaje": "Ya existe un usuario con ese email"}), 409
        
        #Valida la contraseña 
        password_valida, mensaje_error = Usuario.validar_password_registro(datos["password"])
        if not password_valida:
            return jsonify({"mensaje": mensaje_error}), 400
        
        #Validar licencia y vencimiento
        licencia_valida, mensaje_error = Chofer.validar_licencia(datos["licencia"])
        if not licencia_valida:
            return jsonify({"mensaje": mensaje_error}), 400
        
        vencimiento_valido, mensaje_error = Chofer.validar_vencimiento_licencia(datos["vencimientoLicencia"])
        if not vencimiento_valido:
            return jsonify({"mensaje": mensaje_error}), 400
    
        # hashea la contraseña antes de guardarla
        password_hash = bcrypt.generate_password_hash(
            datos["password"]
        ).decode("utf-8")

        # crea el objeto de la clase chofer con los datos que llegaron del front
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
            datos["vencimientoLicencia"],
            datos["legajo"],
        )

        # crea el registro en la tabla usuario
        nuevo_usuario = UsuarioModel(
            username=chofer_clase.username,
            email=chofer_clase.email,
            password=chofer_clase.password,
            nombre=chofer_clase.nombre,
            apellido=chofer_clase.apellido,
            estado=chofer_clase.estado,
            rol=chofer_clase.rol,
        )

        db.session.add(nuevo_usuario)

        # flush genera el id_usuario antes del commit
        # asi se puede usar ese id para crear el registro en chofer
        db.session.flush()

        # se actualiza el id en el objeto chofer porque recien ahora existe
        chofer_clase.id_usuario = nuevo_usuario.id_usuario

        # el controller crea el registro especifico en la tabla chofer
        nuevo_chofer = ChoferModel(
            Usuario_idUsuario=chofer_clase.id_usuario,
            licencia=chofer_clase.licencia,
            vencimientoLicencia=chofer_clase.vencimientoLicencia,
            legajo=chofer_clase.legajo,
        )

        db.session.add(nuevo_chofer)
        db.session.commit()

        # devuelve la respuesta http al frontend
        return jsonify({
            "mensaje": "Solicitud de registro enviada correctamente",
            "usuario": nuevo_usuario.to_dict(),
            "chofer": nuevo_chofer.to_dict(),
        }), 201

    @staticmethod
    def login():
        # recibe los datos que vienen desde el frontend
        datos = request.get_json()

        # el controller valida que el request tenga usuario y contrasena
        if "username" not in datos or "password" not in datos:
            return jsonify({"mensaje": "Faltan datos para iniciar sesion"}), 400

        # busca el usuario en la base de datos
        usuario = UsuarioModel.query.filter_by(
            username=datos["username"]
        ).first()

        # si no existe, el controller devuelve un error
        if usuario is None:
            return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

        # se pasan los datos del modelo a la clase usuario
        usuario_clase = Usuario(
            usuario.id_usuario,
            usuario.username,
             usuario.email,
            usuario.password,
            usuario.nombre,
            usuario.apellido,
            usuario.estado,
            usuario.rol,
        )

        # la clase Usuario verifica la contraseña
        password_correcta = usuario_clase.verificar_password(
            datos["password"],
            bcrypt
        )

        if not password_correcta:
            return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

        # la clase Usuario sabe si la cuenta esta activa
        if not usuario_clase.esta_activo():
            return jsonify({"mensaje": "La cuenta todavia no esta activa"}), 403

        # el controller crea el jwt porque pertenece al flujo de autenticacion
        token = create_access_token(
            identity=str(usuario_clase.id_usuario),
            additional_claims={
                "username": usuario_clase.username,
                "rol": usuario_clase.rol,
            }
        )

        # el controller responde al frontend
        return jsonify({
            "mensaje": "Login correcto",
            "token": token,
            "usuario": usuario_clase.to_dict(),
        }), 200
        
        