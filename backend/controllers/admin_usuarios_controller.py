from flask import g, jsonify, request

from db_instance import db
from extensions import bcrypt

from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.operador_model import OperadorModel

from src.Chofer import Chofer
from src.Usuario import Usuario
from utils.auth_decorators import admin_required
from utils.app_logger import get_app_logger
from utils.input_sanitizer import InputSanitizer
from utils.validation_composite import (
    CampoObligatorio,
    ValidacionCondicional,
    ValidacionFuncion,
    ValidadorCompuesto,
    ValorPermitido,
)


logger = get_app_logger()


class AdminUsuariosController:
    CAMPOS_REGISTRO_USUARIO = [
        "username",
        "email",
        "password",
        "nombre",
        "apellido",
        "estado",
        "rol",
        "legajo",
    ]

    @staticmethod
    def _sanitizar_datos_usuario(datos):
        return InputSanitizer.sanitizar_campos(
            datos,
            campos_texto=[
                "username",
                "nombre",
                "apellido",
                "estado",
                "rol",
                "legajo",
                "licencia",
                "vencimientoLicencia",
                "especialidad",
                "sector",
            ],
            campos_email=["email"],
            campos_password=["password"],
        )

    @staticmethod
    def _crear_validador_campos_obligatorios(campos):
        validador = ValidadorCompuesto()

        for campo in campos:
            validador.agregar(CampoObligatorio(campo))

        return validador

    @staticmethod
    def _crear_validador_datos_chofer():
        return ValidadorCompuesto(
            [
                CampoObligatorio("licencia"),
                CampoObligatorio("vencimientoLicencia"),
                ValidacionFuncion(
                    "licencia",
                    Chofer.validar_licencia
                ),
                ValidacionFuncion(
                    "vencimientoLicencia",
                    Chofer.validar_vencimiento_licencia
                ),
            ]
        )

    @staticmethod
    def _crear_validador_datos_mecanico():
        return ValidadorCompuesto(
            [
                CampoObligatorio("especialidad"),
            ]
        )

    @staticmethod
    def _crear_validador_datos_operador():
        return ValidadorCompuesto(
            [
                CampoObligatorio("sector"),
            ]
        )

    @staticmethod
    def _crear_validador_registro_usuario():
        validador = (
            AdminUsuariosController
            ._crear_validador_campos_obligatorios(
                AdminUsuariosController.CAMPOS_REGISTRO_USUARIO
            )
        )

        validador.agregar(
            ValorPermitido(
                "rol",
                Usuario.ROLES_VALIDOS,
                "Rol"
            )
        )
        validador.agregar(
            ValorPermitido(
                "estado",
                Usuario.ESTADOS_VALIDOS,
                "Estado"
            )
        )
        validador.agregar(
            ValidacionFuncion(
                "password",
                Usuario.validar_password_registro
            )
        )
        validador.agregar(
            ValidacionCondicional(
                lambda datos: datos.get("rol") == Usuario.ROL_CHOFER,
                AdminUsuariosController._crear_validador_datos_chofer()
            )
        )
        validador.agregar(
            ValidacionCondicional(
                lambda datos: datos.get("rol") == Usuario.ROL_MECANICO,
                AdminUsuariosController._crear_validador_datos_mecanico()
            )
        )
        validador.agregar(
            ValidacionCondicional(
                lambda datos: datos.get("rol") == Usuario.ROL_OPERADOR,
                AdminUsuariosController._crear_validador_datos_operador()
            )
        )

        return validador

    @staticmethod
    def _validar_datos_especificos_por_rol(rol, datos):
        if rol == Usuario.ROL_CHOFER:
            validador = (
                AdminUsuariosController._crear_validador_datos_chofer()
            )
            datos_validos, mensaje_error = validador.validar(datos)

            if datos_validos:
                datos["vencimientoLicencia"] = (
                    Chofer.convertir_vencimiento_licencia(
                        datos["vencimientoLicencia"]
                    )
                )

            return datos_validos, mensaje_error

        if rol == Usuario.ROL_MECANICO:
            validador = (
                AdminUsuariosController._crear_validador_datos_mecanico()
            )
            return validador.validar(datos)

        if rol == Usuario.ROL_OPERADOR:
            validador = (
                AdminUsuariosController._crear_validador_datos_operador()
            )
            return validador.validar(datos)

        return True, None

    @staticmethod
    def _validar_datos_registro_usuario(datos):
        validador = (
            AdminUsuariosController._crear_validador_registro_usuario()
        )
        datos_validos, mensaje_error = validador.validar(datos)

        if not datos_validos:
            return False, mensaje_error

        if datos["rol"] == Usuario.ROL_CHOFER:
            datos["vencimientoLicencia"] = (
                Chofer.convertir_vencimiento_licencia(
                    datos["vencimientoLicencia"]
                )
            )

        return True, None

    @staticmethod
    def _validar_datos_especificos_modificacion(
        rol,
        datos,
        datos_actuales
    ):
        datos_validados = dict(datos_actuales)

        for campo, valor in datos.items():
            if campo in datos_validados:
                datos_validados[campo] = valor

        legajo_valido, mensaje_error = CampoObligatorio(
            "legajo",
            "El legajo es obligatorio"
        ).validar(datos_validados)

        if not legajo_valido:
            return False, mensaje_error, None

        valido, mensaje_error = (
            AdminUsuariosController._validar_datos_especificos_por_rol(
                rol,
                datos_validados
            )
        )

        if not valido:
            return False, mensaje_error, None

        return True, None, datos_validados

    @staticmethod
    def _crear_usuario_base(usuario_db):
        datos_usuario = usuario_db.to_dict()
        datos_usuario["password"] = usuario_db.password

        return Usuario.crear_desde_datos(datos_usuario)

    @staticmethod
    def _preparar_datos_usuario_clase(usuario_db):
        datos_usuario = usuario_db.to_dict()

        if usuario_db.rol == Usuario.ROL_ADMIN:
            administrador = AdministradorModel.query.get(
                usuario_db.id_usuario
            )

            if administrador:
                datos_usuario["legajo"] = administrador.legajo

                return datos_usuario

        elif usuario_db.rol == Usuario.ROL_CHOFER:
            chofer = ChoferModel.query.get(usuario_db.id_usuario)

            if chofer:
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["vencimientoLicencia"] = (
                    chofer.vencimientoLicencia
                )
                datos_usuario["legajo"] = chofer.legajo

                return datos_usuario

        elif usuario_db.rol == Usuario.ROL_MECANICO:
            mecanico = MecanicoModel.query.get(usuario_db.id_usuario)

            if mecanico:
                datos_usuario["legajo"] = mecanico.legajo
                datos_usuario["especialidad"] = mecanico.especialidad

                return datos_usuario

        elif usuario_db.rol == Usuario.ROL_OPERADOR:
            operador = OperadorModel.query.get(usuario_db.id_usuario)

            if operador:
                datos_usuario["legajo"] = operador.legajo
                datos_usuario["sector"] = operador.sector

                return datos_usuario

        return None

    @staticmethod
    def _crear_usuario_clase(admin, usuario_db):
        datos_usuario = AdminUsuariosController._preparar_datos_usuario_clase(
            usuario_db
        )

        if datos_usuario is None:
            return AdminUsuariosController._crear_usuario_base(usuario_db)

        usuario_clase = admin.crear_usuario(
            datos_usuario,
            usuario_db.password
        )

        if usuario_clase is None:
            return AdminUsuariosController._crear_usuario_base(usuario_db)

        usuario_clase.id_usuario = usuario_db.id_usuario
        usuario_clase.foto_perfil = usuario_db.foto_perfil

        return usuario_clase

    @staticmethod
    def _agregar_datos_por_rol(datos_usuario, id_usuario, rol):
        if rol == Usuario.ROL_ADMIN:
            administrador = AdministradorModel.query.get(id_usuario)

            if administrador:
                datos_usuario["legajo"] = administrador.legajo

        elif rol == Usuario.ROL_CHOFER:
            chofer = ChoferModel.query.get(id_usuario)

            if chofer:
                datos_usuario["legajo"] = chofer.legajo
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )

        elif rol == Usuario.ROL_MECANICO:
            mecanico = MecanicoModel.query.get(id_usuario)

            if mecanico:
                datos_usuario["legajo"] = mecanico.legajo
                datos_usuario["especialidad"] = mecanico.especialidad

        elif rol == Usuario.ROL_OPERADOR:
            operador = OperadorModel.query.get(id_usuario)

            if operador:
                datos_usuario["legajo"] = operador.legajo
                datos_usuario["sector"] = operador.sector

        return datos_usuario

    @staticmethod
    def _preparar_respuesta_usuario(usuario_db):
        datos_usuario = usuario_db.to_dict()

        return AdminUsuariosController._agregar_datos_por_rol(
            datos_usuario,
            usuario_db.id_usuario,
            usuario_db.rol
        )

    @staticmethod
    def _preparar_respuesta_usuarios(usuarios_db):
        return [
            AdminUsuariosController._preparar_respuesta_usuario(usuario)
            for usuario in usuarios_db
        ]

    @staticmethod
    def _validar_username_email_disponibles(
        username,
        email,
        id_usuario_actual=None
    ):
        username = str(username).strip()
        email = str(email).strip()

        usuario_existente = UsuarioModel.query.filter_by(
            username=username
        ).first()

        if (
            usuario_existente
            and usuario_existente.id_usuario != id_usuario_actual
        ):
            return False, "Ya existe un usuario con ese username", None, None

        email_existente = UsuarioModel.query.filter_by(
            email=email
        ).first()

        if (
            email_existente
            and email_existente.id_usuario != id_usuario_actual
        ):
            return False, "Ya existe un usuario con ese email", None, None

        return True, None, username, email

    @staticmethod
    def _aplicar_datos_usuario(usuario_db, usuario_clase):
        usuario_db.username = usuario_clase.username
        usuario_db.email = usuario_clase.email
        usuario_db.nombre = usuario_clase.nombre
        usuario_db.apellido = usuario_clase.apellido
        usuario_db.estado = usuario_clase.estado

    @staticmethod
    def _crear_modelo_especifico(id_usuario, datos):
        if datos["rol"] == Usuario.ROL_ADMIN:
            return AdministradorModel(
                Usuario_idUsuario=id_usuario,
                legajo=datos["legajo"],
            )

        if datos["rol"] == Usuario.ROL_CHOFER:
            return ChoferModel(
                Usuario_idUsuario=id_usuario,
                licencia=datos["licencia"],
                vencimientoLicencia=datos["vencimientoLicencia"],
                legajo=datos["legajo"],
            )

        if datos["rol"] == Usuario.ROL_MECANICO:
            return MecanicoModel(
                Usuario_idUsuario=id_usuario,
                legajo=datos["legajo"],
                especialidad=datos["especialidad"],
            )

        if datos["rol"] == Usuario.ROL_OPERADOR:
            return OperadorModel(
                Usuario_idUsuario=id_usuario,
                legajo=datos["legajo"],
                sector=datos["sector"],
            )

        return None

    @staticmethod
    def _actualizar_datos_especificos(usuario_db, datos):
        if usuario_db.rol == Usuario.ROL_ADMIN:
            administrador = AdministradorModel.query.get(
                usuario_db.id_usuario
            )

            if administrador:
                datos_validos, mensaje_error, datos_validados = (
                    AdminUsuariosController._validar_datos_especificos_modificacion(
                        usuario_db.rol,
                        datos,
                        {
                            "legajo": administrador.legajo
                        }
                    )
                )

                if not datos_validos:
                    return False, mensaje_error

                administrador.legajo = datos_validados["legajo"]

        elif usuario_db.rol == Usuario.ROL_CHOFER:
            chofer = ChoferModel.query.get(usuario_db.id_usuario)

            if chofer:
                datos_validos, mensaje_error, datos_validados = (
                    AdminUsuariosController._validar_datos_especificos_modificacion(
                        usuario_db.rol,
                        datos,
                        {
                            "legajo": chofer.legajo,
                            "licencia": chofer.licencia,
                            "vencimientoLicencia": (
                                chofer.vencimientoLicencia
                            ),
                        }
                    )
                )

                if not datos_validos:
                    return False, mensaje_error

                chofer.legajo = datos_validados["legajo"]
                chofer.licencia = datos_validados["licencia"]
                chofer.vencimientoLicencia = datos_validados[
                    "vencimientoLicencia"
                ]

        elif usuario_db.rol == Usuario.ROL_MECANICO:
            mecanico = MecanicoModel.query.get(usuario_db.id_usuario)

            if mecanico:
                datos_validos, mensaje_error, datos_validados = (
                    AdminUsuariosController._validar_datos_especificos_modificacion(
                        usuario_db.rol,
                        datos,
                        {
                            "legajo": mecanico.legajo,
                            "especialidad": mecanico.especialidad,
                        }
                    )
                )

                if not datos_validos:
                    return False, mensaje_error

                mecanico.legajo = datos_validados["legajo"]
                mecanico.especialidad = datos_validados["especialidad"]

        elif usuario_db.rol == Usuario.ROL_OPERADOR:
            operador = OperadorModel.query.get(usuario_db.id_usuario)

            if operador:
                datos_validos, mensaje_error, datos_validados = (
                    AdminUsuariosController._validar_datos_especificos_modificacion(
                        usuario_db.rol,
                        datos,
                        {
                            "legajo": operador.legajo,
                            "sector": operador.sector,
                        }
                    )
                )

                if not datos_validos:
                    return False, mensaje_error

                operador.legajo = datos_validados["legajo"]
                operador.sector = datos_validados["sector"]

        return True, None

    @staticmethod
    @admin_required
    def activar_usuario(id_usuario):
        admin = g.admin_actual

        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        usuario_clase = AdminUsuariosController._crear_usuario_clase(
            admin,
            usuario_db
        )

        accion_realizada = admin.activar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({
                "mensaje": "Este usuario no se puede activar"
            }), 400

        usuario_db.estado = usuario_clase.estado

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo activar el usuario")

            return jsonify({
                "mensaje": "No se pudo activar el usuario"
            }), 500

        datos_usuario = (
            AdminUsuariosController._preparar_respuesta_usuario(
                usuario_db
            )
        )

        return jsonify({
            "mensaje": "Usuario activado correctamente",
            "usuario": datos_usuario
        }), 200

    @staticmethod
    @admin_required
    def desactivar_usuario(id_usuario):
        admin = g.admin_actual

        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        usuario_clase = AdminUsuariosController._crear_usuario_clase(
            admin,
            usuario_db
        )

        accion_realizada = admin.desactivar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({
                "mensaje": "Este usuario no se puede desactivar"
            }), 400

        usuario_db.estado = usuario_clase.estado

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo desactivar el usuario")

            return jsonify({
                "mensaje": "No se pudo desactivar el usuario"
            }), 500

        datos_usuario = (
            AdminUsuariosController._preparar_respuesta_usuario(
                usuario_db
            )
        )

        return jsonify({
            "mensaje": "Usuario desactivado correctamente",
            "usuario": datos_usuario
        }), 200

    @staticmethod
    @admin_required
    def listar_usuarios_pendientes():
        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado=Usuario.ESTADO_PENDIENTE
        ).all()

        usuarios = AdminUsuariosController._preparar_respuesta_usuarios(
            usuarios_pendientes
        )

        return jsonify({
            "mensaje": "Usuarios pendientes obtenidos correctamente",
            "usuarios": usuarios
        }), 200

    @staticmethod
    @admin_required
    def listar_usuarios():
        usuarios_db = UsuarioModel.query.all()
        usuarios = AdminUsuariosController._preparar_respuesta_usuarios(
            usuarios_db
        )

        return jsonify({
            "mensaje": "Usuarios obtenidos correctamente",
            "usuarios": usuarios
        }), 200

    @staticmethod
    @admin_required
    def modificar_usuario(id_usuario):
        admin = g.admin_actual

        datos = AdminUsuariosController._sanitizar_datos_usuario(
            request.get_json(silent=True) or {}
        )

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({
                "mensaje": "Usuario no encontrado"
            }), 404

        datos_disponibles, mensaje_error, nuevo_username, nuevo_email = (
            AdminUsuariosController._validar_username_email_disponibles(
                datos.get("username", usuario_db.username),
                datos.get("email", usuario_db.email),
                usuario_db.id_usuario
            )
        )

        if not datos_disponibles:
            return jsonify({
                "mensaje": mensaje_error
            }), 409

        usuario_clase = AdminUsuariosController._crear_usuario_clase(
            admin,
            usuario_db
        )

        nombre = datos.get(
            "nombre",
            usuario_db.nombre
        )
        nombre = str(nombre).strip()

        apellido = datos.get(
            "apellido",
            usuario_db.apellido
        )
        apellido = str(apellido).strip()

        estado = datos.get(
            "estado",
            usuario_db.estado
        )
        estado = str(estado).strip()

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

        AdminUsuariosController._aplicar_datos_usuario(
            usuario_db,
            usuario_clase
        )

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

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo modificar el usuario")

            return jsonify({
                "mensaje": "No se pudo modificar el usuario"
            }), 500

        datos_usuario = (
            AdminUsuariosController._preparar_respuesta_usuario(
                usuario_db
            )
        )

        return jsonify({
            "mensaje": "Usuario modificado correctamente",
            "usuario": datos_usuario
        }), 200

    @staticmethod
    @admin_required
    def registrar_usuario():
        admin = g.admin_actual

        datos = AdminUsuariosController._sanitizar_datos_usuario(
            request.get_json(silent=True) or {}
        )

        if not datos:
            return jsonify({
                "mensaje": "No se recibieron datos"
            }), 400

        datos_validos, mensaje_error = (
            AdminUsuariosController._validar_datos_registro_usuario(datos)
        )

        if not datos_validos:
            return jsonify({
                "mensaje": mensaje_error
            }), 400

        datos_disponibles, mensaje_error, username, email = (
            AdminUsuariosController._validar_username_email_disponibles(
                datos["username"],
                datos["email"]
            )
        )

        if not datos_disponibles:
            return jsonify({
                "mensaje": mensaje_error
            }), 409

        password_hash = bcrypt.generate_password_hash(
            datos["password"]
        ).decode("utf-8")

        datos_usuario = dict(datos)
        datos_usuario["username"] = username
        datos_usuario["email"] = email

        usuario_clase = admin.crear_usuario(
            datos_usuario,
            password_hash
        )

        if usuario_clase is None:
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
            logger.exception("No se pudo registrar el usuario")

            return jsonify({
                "mensaje": "No se pudo registrar el usuario"
            }), 500

        datos_usuario = (
            AdminUsuariosController._preparar_respuesta_usuario(
                nuevo_usuario
            )
        )

        return jsonify({
            "mensaje": "Usuario registrado correctamente",
            "usuario": datos_usuario
        }), 201
