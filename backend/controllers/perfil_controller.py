import os
import uuid

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db_instance import db
from extensions import bcrypt

from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.operador_model import OperadorModel

from src.Usuario import Usuario


class PerfilController:

    EXTENSIONES_PERMITIDAS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    CARPETA_PERFILES = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "uploads",
            "perfiles"
        )
    )

    # obtiene el usuario logueado usando el id guardado en el token
    @staticmethod
    def _obtener_usuario_actual():
        id_usuario = get_jwt_identity()

        if not id_usuario:
            return None

        return UsuarioModel.query.get(int(id_usuario))

    # crea el objeto Usuario para usar los metodos de la clase
    @staticmethod
    def _crear_usuario_clase(usuario_db):
        return Usuario(
            usuario_db.id_usuario,
            usuario_db.username,
            usuario_db.email,
            usuario_db.password,
            usuario_db.nombre,
            usuario_db.apellido,
            usuario_db.estado,
            usuario_db.rol,
            usuario_db.foto_perfil
        )

    # agrega los datos especificos segun el rol del usuario
    @staticmethod
    def _agregar_datos_por_rol(datos_usuario, usuario_db):
        if usuario_db.rol == "admin":
            administrador = AdministradorModel.query.get(
                usuario_db.id_usuario
            )

            if administrador:
                datos_usuario["legajo"] = administrador.legajo

        elif usuario_db.rol == "chofer":
            chofer = ChoferModel.query.get(
                usuario_db.id_usuario
            )

            if chofer:
                datos_usuario["legajo"] = chofer.legajo
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )

        elif usuario_db.rol == "mecanico":
            mecanico = MecanicoModel.query.get(
                usuario_db.id_usuario
            )

            if mecanico:
                datos_usuario["legajo"] = mecanico.legajo
                datos_usuario["especialidad"] = mecanico.especialidad

        elif usuario_db.rol == "operador":
            operador = OperadorModel.query.get(
                usuario_db.id_usuario
            )

            if operador:
                datos_usuario["legajo"] = operador.legajo
                datos_usuario["sector"] = operador.sector

        return datos_usuario

    # valida que la imagen tenga una extension permitida
    @staticmethod
    def _extension_valida(nombre_archivo):
        if "." not in nombre_archivo:
            return False

        extension = nombre_archivo.rsplit(".", 1)[1].lower()

        return extension in PerfilController.EXTENSIONES_PERMITIDAS

    @staticmethod
    @jwt_required()
    def obtener_perfil():
        usuario_db = PerfilController._obtener_usuario_actual()

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        datos_usuario = usuario_db.to_dict()

        datos_usuario = PerfilController._agregar_datos_por_rol(
            datos_usuario,
            usuario_db
        )

        return jsonify({
            "perfil": datos_usuario
        }), 200

    @staticmethod
    @jwt_required()
    def modificar_perfil():
        usuario_db = PerfilController._obtener_usuario_actual()

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        datos = request.get_json()

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        nuevo_email = datos.get(
            "email",
            usuario_db.email
        )

        email_existente = UsuarioModel.query.filter_by(
            email=nuevo_email
        ).first()

        if (
            email_existente
            and email_existente.id_usuario != usuario_db.id_usuario
        ):
            return jsonify({
                "mensaje": "Ya existe un usuario con ese email"
            }), 409

        usuario_clase = PerfilController._crear_usuario_clase(
            usuario_db
        )

        datos_modificados, mensaje_error = (
            usuario_clase.modificar_datos_personales(
                datos.get("nombre", usuario_db.nombre),
                datos.get("apellido", usuario_db.apellido),
                nuevo_email
            )
        )

        if not datos_modificados:
            return jsonify({
                "mensaje": mensaje_error
            }), 400

        usuario_db.nombre = usuario_clase.nombre
        usuario_db.apellido = usuario_clase.apellido
        usuario_db.email = usuario_clase.email

        db.session.commit()

        datos_usuario = usuario_db.to_dict()

        datos_usuario = PerfilController._agregar_datos_por_rol(
            datos_usuario,
            usuario_db
        )

        return jsonify({
            "mensaje": "Perfil actualizado correctamente",
            "perfil": datos_usuario
        }), 200

    @staticmethod
    @jwt_required()
    def cambiar_password():
        usuario_db = PerfilController._obtener_usuario_actual()

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        datos = request.get_json()

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        usuario_clase = PerfilController._crear_usuario_clase(
            usuario_db
        )

        password_valida, mensaje_error = (
            usuario_clase.puede_cambiar_password(
                datos.get("password_actual"),
                datos.get("password_nueva"),
                datos.get("confirmar_password"),
                bcrypt
            )
        )

        if not password_valida:
            return jsonify({
                "mensaje": mensaje_error
            }), 400

        usuario_db.password = bcrypt.generate_password_hash(
            datos["password_nueva"]
        ).decode("utf-8")

        db.session.commit()

        return jsonify({
            "mensaje": "Contraseña actualizada correctamente"
        }), 200

    @staticmethod
    @jwt_required()
    def subir_foto():
        usuario_db = PerfilController._obtener_usuario_actual()

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        if "foto" not in request.files:
            return jsonify({
                "mensaje": "No se recibio ninguna imagen"
            }), 400

        foto = request.files["foto"]

        if not foto or not foto.filename:
            return jsonify({
                "mensaje": "No se selecciono ninguna imagen"
            }), 400

        if not PerfilController._extension_valida(foto.filename):
            return jsonify({
                "mensaje": "Formato de imagen no permitido"
            }), 400

        foto.seek(0, os.SEEK_END)
        tamanio = foto.tell()
        foto.seek(0)

        if tamanio > 3 * 1024 * 1024:
            return jsonify({
                "mensaje": "La imagen no puede superar los 3 MB"
            }), 400

        os.makedirs(
            PerfilController.CARPETA_PERFILES,
            exist_ok=True
        )

        extension = foto.filename.rsplit(".", 1)[1].lower()

        nombre_archivo = f"{uuid.uuid4().hex}.{extension}"

        ruta_archivo = os.path.join(
            PerfilController.CARPETA_PERFILES,
            nombre_archivo
        )

        foto.save(ruta_archivo)

        if usuario_db.foto_perfil:
            nombre_anterior = os.path.basename(
                usuario_db.foto_perfil
            )

            ruta_anterior = os.path.join(
                PerfilController.CARPETA_PERFILES,
                nombre_anterior
            )

            if os.path.exists(ruta_anterior):
                os.remove(ruta_anterior)

        usuario_db.foto_perfil = (
            f"/uploads/perfiles/{nombre_archivo}"
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Foto de perfil actualizada correctamente",
            "foto_perfil": usuario_db.foto_perfil
        }), 200