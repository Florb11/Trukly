from flask import jsonify, request
from flask_jwt_extended import jwt_required

from db_instance import db
from extensions import bcrypt

from controllers.administrador_controller import AdministradorController

from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.operador_model import OperadorModel

from src.Usuario import Usuario
from src.Chofer import Chofer


class AdminUsuariosController:

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
        )

    @staticmethod
    def _agregar_datos_por_rol(datos_usuario, id_usuario, rol):
        if rol == "admin":
            administrador = AdministradorModel.query.get(id_usuario)

            if administrador:
                datos_usuario["legajo"] = administrador.legajo

        elif rol == "chofer":
            chofer = ChoferModel.query.get(id_usuario)

            if chofer:
                datos_usuario["legajo"] = chofer.legajo
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )

        elif rol == "mecanico":
            mecanico = MecanicoModel.query.get(id_usuario)

            if mecanico:
                datos_usuario["legajo"] = mecanico.legajo
                datos_usuario["especialidad"] = mecanico.especialidad

        elif rol == "operador":
            operador = OperadorModel.query.get(id_usuario)

            if operador:
                datos_usuario["legajo"] = operador.legajo
                datos_usuario["sector"] = operador.sector

        return datos_usuario

    @staticmethod
    def _crear_modelo_especifico(id_usuario, datos):
        if datos["rol"] == "admin":
            return AdministradorModel(
                Usuario_idUsuario=id_usuario,
                legajo=datos["legajo"],
            )

        if datos["rol"] == "chofer":
            return ChoferModel(
                Usuario_idUsuario=id_usuario,
                licencia=datos["licencia"],
                vencimientoLicencia=datos["vencimientoLicencia"],
                legajo=datos["legajo"],
            )

        if datos["rol"] == "mecanico":
            return MecanicoModel(
                Usuario_idUsuario=id_usuario,
                legajo=datos["legajo"],
                especialidad=datos["especialidad"],
            )

        if datos["rol"] == "operador":
            return OperadorModel(
                Usuario_idUsuario=id_usuario,
                legajo=datos["legajo"],
                sector=datos["sector"],
            )

        return None

    @staticmethod
    def _actualizar_datos_especificos(usuario_db, datos):
        if usuario_db.rol == "admin":
            administrador = AdministradorModel.query.get(
                usuario_db.id_usuario
            )

            if administrador:
                administrador.legajo = datos.get(
                    "legajo",
                    administrador.legajo
                )

        elif usuario_db.rol == "chofer":
            chofer = ChoferModel.query.get(usuario_db.id_usuario)

            if chofer:
                nueva_licencia = datos.get(
                    "licencia",
                    chofer.licencia
                )

                nuevo_vencimiento = datos.get(
                    "vencimientoLicencia",
                    str(chofer.vencimientoLicencia)
                )

                licencia_valida, mensaje_error = Chofer.validar_licencia(
                    nueva_licencia
                )

                if not licencia_valida:
                    return False, mensaje_error

                vencimiento_valido, mensaje_error = (
                    Chofer.validar_vencimiento_licencia(
                        nuevo_vencimiento
                    )
                )

                if not vencimiento_valido:
                    return False, mensaje_error

                chofer.legajo = datos.get(
                    "legajo",
                    chofer.legajo
                )

                chofer.licencia = nueva_licencia
                chofer.vencimientoLicencia = nuevo_vencimiento

        elif usuario_db.rol == "mecanico":
            mecanico = MecanicoModel.query.get(usuario_db.id_usuario)

            if mecanico:
                mecanico.legajo = datos.get(
                    "legajo",
                    mecanico.legajo
                )

                mecanico.especialidad = datos.get(
                    "especialidad",
                    mecanico.especialidad
                )

        elif usuario_db.rol == "operador":
            operador = OperadorModel.query.get(usuario_db.id_usuario)

            if operador:
                operador.legajo = datos.get(
                    "legajo",
                    operador.legajo
                )

                operador.sector = datos.get(
                    "sector",
                    operador.sector
                )

        return True, None

    @staticmethod
    @jwt_required()
    def activar_usuario(id_usuario):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        usuario_clase = AdminUsuariosController._crear_usuario_clase(
            usuario_db
        )

        accion_realizada = admin.activar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({
                "mensaje": "Este usuario no se puede activar"
            }), 400

        usuario_db.estado = usuario_clase.estado

        db.session.commit()

        datos_usuario = usuario_db.to_dict()

        datos_usuario = AdminUsuariosController._agregar_datos_por_rol(
            datos_usuario,
            usuario_db.id_usuario,
            usuario_db.rol
        )

        return jsonify({
            "mensaje": "Usuario activado correctamente",
            "usuario": datos_usuario
        }), 200

    @staticmethod
    @jwt_required()
    def desactivar_usuario(id_usuario):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        usuario_clase = AdminUsuariosController._crear_usuario_clase(
            usuario_db
        )

        accion_realizada = admin.desactivar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({
                "mensaje": "Este usuario no se puede desactivar"
            }), 400

        usuario_db.estado = usuario_clase.estado

        db.session.commit()

        datos_usuario = usuario_db.to_dict()

        datos_usuario = AdminUsuariosController._agregar_datos_por_rol(
            datos_usuario,
            usuario_db.id_usuario,
            usuario_db.rol
        )

        return jsonify({
            "mensaje": "Usuario desactivado correctamente",
            "usuario": datos_usuario
        }), 200

    @staticmethod
    @jwt_required()
    def listar_usuarios_pendientes():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado="pendiente"
        ).all()

        usuarios = []

        for usuario in usuarios_pendientes:
            datos_usuario = usuario.to_dict()

            datos_usuario = (
                AdminUsuariosController._agregar_datos_por_rol(
                    datos_usuario,
                    usuario.id_usuario,
                    usuario.rol
                )
            )

            usuarios.append(datos_usuario)

        return jsonify({
            "mensaje": "Usuarios pendientes obtenidos correctamente",
            "usuarios": usuarios
        }), 200

    @staticmethod
    @jwt_required()
    def listar_usuarios():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        usuarios_db = UsuarioModel.query.all()
        usuarios = []

        for usuario in usuarios_db:
            datos_usuario = usuario.to_dict()

            datos_usuario = (
                AdminUsuariosController._agregar_datos_por_rol(
                    datos_usuario,
                    usuario.id_usuario,
                    usuario.rol
                )
            )

            usuarios.append(datos_usuario)

        return jsonify({
            "mensaje": "Usuarios obtenidos correctamente",
            "usuarios": usuarios
        }), 200

    @staticmethod
    @jwt_required()
    def modificar_usuario(id_usuario):
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        datos = request.get_json()

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        nuevo_username = datos.get(
            "username",
            usuario_db.username
        )

        usuario_existente = UsuarioModel.query.filter_by(
            username=nuevo_username
        ).first()

        if (
            usuario_existente
            and usuario_existente.id_usuario != usuario_db.id_usuario
        ):
            return jsonify({
                "mensaje": "Ya existe un usuario con ese username"
            }), 409

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

        usuario_clase = AdminUsuariosController._crear_usuario_clase(
            usuario_db
        )

        nombre = datos.get(
            "nombre",
            usuario_db.nombre
        )

        apellido = datos.get(
            "apellido",
            usuario_db.apellido
        )

        estado = datos.get(
            "estado",
            usuario_db.estado
        )

        accion_realizada = admin.modificar_usuario(
            usuario_clase,
            nuevo_username,
            nuevo_email,
            nombre,
            apellido,
            estado
        )

        if not accion_realizada:
            return jsonify({
                "mensaje": "No se pudo modificar el usuario"
            }), 400

        usuario_db.username = usuario_clase.username
        usuario_db.email = usuario_clase.email
        usuario_db.nombre = usuario_clase.nombre
        usuario_db.apellido = usuario_clase.apellido
        usuario_db.estado = usuario_clase.estado

        if datos.get("password"):
            password_valida, mensaje_error = (
                Usuario.validar_password_registro(
                    datos["password"]
                )
            )

            if not password_valida:
                return jsonify({
                    "mensaje": mensaje_error
                }), 400

            usuario_db.password = bcrypt.generate_password_hash(
                datos["password"]
            ).decode("utf-8")

        datos_actualizados, mensaje_error = (
            AdminUsuariosController._actualizar_datos_especificos(
                usuario_db,
                datos
            )
        )

        if not datos_actualizados:
            return jsonify({
                "mensaje": mensaje_error
            }), 400

        db.session.commit()

        datos_usuario = usuario_db.to_dict()

        datos_usuario = AdminUsuariosController._agregar_datos_por_rol(
            datos_usuario,
            usuario_db.id_usuario,
            usuario_db.rol
        )

        return jsonify({
            "mensaje": "Usuario modificado correctamente",
            "usuario": datos_usuario
        }), 200

    @staticmethod
    @jwt_required()
    def registrar_usuario():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({
                "mensaje": "No tenes permiso para realizar esta accion"
            }), 403

        datos = request.get_json()

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        campos_obligatorios = [
            "username",
            "email",
            "password",
            "nombre",
            "apellido",
            "estado",
            "rol",
            "legajo",
        ]

        for campo in campos_obligatorios:
            if campo not in datos or datos[campo] == "":
                return jsonify({
                    "mensaje": f"Falta el campo {campo}"
                }), 400

        roles_validos = [
            "admin",
            "chofer",
            "mecanico",
            "operador"
        ]

        if datos["rol"] not in roles_validos:
            return jsonify({
                "mensaje": "Rol no valido"
            }), 400

        estados_validos = [
            "pendiente",
            "activo",
            "inactivo"
        ]

        if datos["estado"] not in estados_validos:
            return jsonify({
                "mensaje": "Estado no valido"
            }), 400

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
            Usuario.validar_password_registro(
                datos["password"]
            )
        )

        if not password_valida:
            return jsonify({
                "mensaje": mensaje_error
            }), 400

        if datos["rol"] == "chofer":
            if not datos.get("licencia"):
                return jsonify({
                    "mensaje": "Falta el campo licencia"
                }), 400

            if not datos.get("vencimientoLicencia"):
                return jsonify({
                    "mensaje": "Falta el campo vencimientoLicencia"
                }), 400

            licencia_valida, mensaje_error = Chofer.validar_licencia(
                datos["licencia"]
            )

            if not licencia_valida:
                return jsonify({
                    "mensaje": mensaje_error
                }), 400

            vencimiento_valido, mensaje_error = (
                Chofer.validar_vencimiento_licencia(
                    datos["vencimientoLicencia"]
                )
            )

            if not vencimiento_valido:
                return jsonify({
                    "mensaje": mensaje_error
                }), 400

        if datos["rol"] == "mecanico" and not datos.get("especialidad"):
            return jsonify({
                "mensaje": "Falta el campo especialidad"
            }), 400

        if datos["rol"] == "operador" and not datos.get("sector"):
            return jsonify({
                "mensaje": "Falta el campo sector"
            }), 400

        password_hash = bcrypt.generate_password_hash(
            datos["password"]
        ).decode("utf-8")

        usuario_clase = Usuario(
            None,
            datos["username"],
            datos["email"],
            password_hash,
            datos["nombre"],
            datos["apellido"],
            datos["estado"],
            datos["rol"],
        )

        accion_realizada = admin.registrar_usuario(
            usuario_clase
        )

        if not accion_realizada:
            return jsonify({
                "mensaje": "No se pudo registrar el usuario"
            }), 400

        nuevo_usuario = UsuarioModel(
            username=usuario_clase.username,
            email=usuario_clase.email,
            password=usuario_clase.password,
            nombre=usuario_clase.nombre,
            apellido=usuario_clase.apellido,
            estado=usuario_clase.estado,
            rol=usuario_clase.rol,
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.flush()

            nuevo_especifico = (
                AdminUsuariosController._crear_modelo_especifico(
                    nuevo_usuario.id_usuario,
                    datos
                )
            )

            if nuevo_especifico is None:
                db.session.rollback()

                return jsonify({
                    "mensaje": "No se pudo crear el usuario"
                }), 400

            db.session.add(nuevo_especifico)
            db.session.commit()

        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo registrar el usuario"
            }), 500

        datos_usuario = nuevo_usuario.to_dict()

        datos_usuario = AdminUsuariosController._agregar_datos_por_rol(
            datos_usuario,
            nuevo_usuario.id_usuario,
            nuevo_usuario.rol
        )

        return jsonify({
            "mensaje": "Usuario registrado correctamente",
            "usuario": datos_usuario
        }), 201