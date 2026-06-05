from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import date, timedelta

from db_instance import db

from models.administrador_model import AdministradorModel
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.operador_model import OperadorModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.reporte_model import ReporteModel

from src.Administrador import Administrador
from src.Usuario import Usuario
from src.Camion import Camion

from extensions import bcrypt
from src.Chofer import Chofer

#Ahora el controlador es una clase que contiene todos los metodos
#Usamos staticmethod porque no necesitamos crear un objeto del controlador 
#Porque este controller no necesita guardar informacion entre requests. Cada request llega, se procesa y termina.
class AdministradorController:

    @staticmethod
    def listar_administradores():
        administradores = AdministradorModel.query.all()

        return jsonify([
            administrador.to_dict()
            for administrador in administradores
        ])

    @staticmethod
    def obtener_administrador(id_usuario):
        # busco administrador por id
        administrador = AdministradorModel.query.get(id_usuario)

        if administrador is None:
            return jsonify({"mensaje": "Administrador no encontrado"}), 404

        return jsonify(administrador.to_dict())

    @staticmethod
    def crear_administrador():
        datos = request.get_json()

        nuevo_administrador = AdministradorModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["legajo"]
        )

        db.session.add(nuevo_administrador)
        db.session.commit()

        return jsonify({
            "mensaje": "Administrador creado correctamente",
            "administrador": nuevo_administrador.to_dict(),
        })

    @staticmethod
    def obtener_admin_actual():
        # leo el id del usuario desde el token
        id_usuario = get_jwt_identity()

        # leo los datos extra del token, como el rol
        datos_token = get_jwt()

        if not id_usuario:
            return None

        # si el token no tiene rol admin, no dejo crear el objeto administrador
        if datos_token.get("rol") != "admin":
            return None

        # busco el usuario completo en la base
        usuario = UsuarioModel.query.get(int(id_usuario))

        if usuario is None:
            return None

        # busco los datos especificos del administrador
        administrador = AdministradorModel.query.get(usuario.id_usuario)

        if administrador is None:
            return None

        # creo el objeto administrador con datos de usuario y datos propios del admin
        admin = Administrador(
            usuario.id_usuario,
            usuario.username,
            usuario.email,
            usuario.password,
            usuario.nombre,
            usuario.apellido,
            usuario.estado,
            usuario.rol,
            administrador.legajo,
        )

        return admin

    @staticmethod
    @jwt_required()
    def activar_usuario(id_usuario):
        # obtengo el administrador que esta haciendo la accion
        admin = AdministradorController.obtener_admin_actual()

        # si no se pudo obtener un admin valido, no tiene permiso
        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        # busco el usuario en la base
        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        # paso los datos del modelo a un objeto Usuario para poder acceder a sus metodos
        usuario_clase = Usuario(
            usuario_db.id_usuario,
            usuario_db.username,
            usuario_db.email,
            usuario_db.password,
            usuario_db.nombre,
            usuario_db.apellido,
            usuario_db.estado,
            usuario_db.rol,
        )

        # la clase administrador valida y cambia el estado del usuario
        accion_realizada = admin.activar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({"mensaje": "Este usuario no se puede activar"}), 400

        # el controller pasa el cambio al modelo y guarda en la base
        usuario_db.estado = usuario_clase.estado

        db.session.commit()

        return jsonify({
            "mensaje": "Usuario activado correctamente",
            "usuario": usuario_db.to_dict()
        }), 200

    @staticmethod
    @jwt_required()
    def desactivar_usuario(id_usuario):
        # obtengo el administrador que esta haciendo la accion
        admin = AdministradorController.obtener_admin_actual()

        # si no se pudo obtener un admin valido, no tiene permiso
        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        # busco el usuario en la base
        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        # paso los datos del modelo a un objeto Usuario
        usuario_clase = Usuario(
            usuario_db.id_usuario,
            usuario_db.username,
            usuario_db.email,
            usuario_db.password,
            usuario_db.nombre,
            usuario_db.apellido,
            usuario_db.estado,
            usuario_db.rol,
        )

        # la clase administrador valida y cambia el estado del usuario
        accion_realizada = admin.desactivar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({"mensaje": "Este usuario no se puede desactivar"}), 400

        # el controller copia el cambio al modelo y guarda en la base
        usuario_db.estado = usuario_clase.estado

        db.session.commit()

        return jsonify({
            "mensaje": "Usuario desactivado correctamente",
            "usuario": usuario_db.to_dict()
        }), 200

    @staticmethod
    @jwt_required()
    def listar_usuarios_pendientes():
        # obtengo el administrador que esta haciendo la accion
        admin = AdministradorController.obtener_admin_actual()

        # si no se pudo obtener un admin valido, no tiene permiso
        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        # busco todos los usuarios que todavia estan pendientes
        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado="pendiente"
        ).all()

        usuarios = []

        for usuario in usuarios_pendientes:
            datos_usuario = usuario.to_dict()

            # si el usuario pendiente es chofer, agrego sus datos especificos
            if usuario.rol == "chofer":
                chofer = ChoferModel.query.get(usuario.id_usuario)

                if chofer:
                    datos_usuario["licencia"] = chofer.licencia
                    datos_usuario["vencimientoLicencia"] = str(
                        chofer.vencimientoLicencia
                    )
                    datos_usuario["legajo"] = chofer.legajo

            usuarios.append(datos_usuario)

        return jsonify({
            "mensaje": "Usuarios pendientes obtenidos correctamente",
            "usuarios": usuarios
        }), 200

    @staticmethod
    @jwt_required()
    def listar_usuarios():
        # obtengo el administrador que esta haciendo la accion
        admin = AdministradorController.obtener_admin_actual()

        # si no se pudo obtener un admin valido, no tiene permiso
        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        # busco todos los usuarios
        usuarios_db = UsuarioModel.query.all()

        usuarios = []

        for usuario in usuarios_db:
            datos_usuario = usuario.to_dict()

            # si es chofer, agrego datos propios del chofer
            if usuario.rol == "chofer":
                chofer = ChoferModel.query.get(usuario.id_usuario)

                if chofer:
                    datos_usuario["legajo"] = chofer.legajo
                    datos_usuario["licencia"] = chofer.licencia
                    datos_usuario["vencimientoLicencia"] = str(
                        chofer.vencimientoLicencia
                    )

            # si es administrador, agrego datos propios del administrador
            elif usuario.rol == "admin":
                administrador = AdministradorModel.query.get(usuario.id_usuario)

                if administrador:
                    datos_usuario["legajo"] = administrador.legajo

            # si es mecanico, agrego datos propios del mecanico
            elif usuario.rol == "mecanico":
                mecanico = MecanicoModel.query.get(usuario.id_usuario)

                if mecanico:
                    datos_usuario["legajo"] = mecanico.legajo
                    datos_usuario["especialidad"] = mecanico.especialidad

            # si es operador, agrego datos propios del operador logistico
            elif usuario.rol == "operador":
                operador = OperadorModel.query.get(usuario.id_usuario)

                if operador:
                    datos_usuario["legajo"] = operador.legajo
                    datos_usuario["sector"] = operador.sector

            usuarios.append(datos_usuario)

        return jsonify({
            "mensaje": "Usuarios obtenidos correctamente",
            "usuarios": usuarios
        }), 200
        
    @staticmethod
    @jwt_required()
    def modificar_usuario(id_usuario):
        # obtengo el administrador que esta haciendo la accion
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        datos = request.get_json()

        # busco el usuario en la base
        usuario_db = UsuarioModel.query.get(id_usuario)

        if usuario_db is None:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        # si cambia el username, reviso que no exista otro usuario con ese username
        nuevo_username = datos.get("username", usuario_db.username)

        usuario_existente = UsuarioModel.query.filter_by(
            username=nuevo_username
        ).first()

        if usuario_existente and usuario_existente.id_usuario != usuario_db.id_usuario:
            return jsonify({"mensaje": "Ya existe un usuario con ese username"}), 409
        
        #email
        nuevo_email = datos.get("email", usuario_db.email)

        email_existente = UsuarioModel.query.filter_by(
        email=nuevo_email
         ).first()

        if email_existente and email_existente.id_usuario != usuario_db.id_usuario:
            return jsonify({"mensaje": "Ya existe un usuario con ese email"}), 409

        # paso los datos del modelo a un objeto Usuario para usar la logica de la clase
        usuario_clase = Usuario(
            usuario_db.id_usuario,
            usuario_db.username,
            usuario_db.email,
            usuario_db.password,
            usuario_db.nombre,
            usuario_db.apellido,
            usuario_db.estado,
            usuario_db.rol,
        )

        nombre = datos.get("nombre", usuario_db.nombre)
        apellido = datos.get("apellido", usuario_db.apellido)
        estado = datos.get("estado", usuario_db.estado)

        accion_realizada = admin.modificar_usuario(
            usuario_clase,
            nuevo_username,
            nuevo_email,
            nombre,
            apellido,
            estado
        )

        if not accion_realizada:
            return jsonify({"mensaje": "No se pudo modificar el usuario"}), 400

        # copio los cambios generales al modelo
        usuario_db.username = usuario_clase.username
        usuario_db.email = usuario_clase.email
        usuario_db.nombre = usuario_clase.nombre
        usuario_db.apellido = usuario_clase.apellido
        usuario_db.estado = usuario_clase.estado

        # si viene password y no esta vacio, la valido y la hasheo
        if "password" in datos and datos["password"] != "":
            password_valida, mensaje_error = Usuario.validar_password_registro(
                datos["password"]
            )

            if not password_valida:
                return jsonify({"mensaje": mensaje_error}), 400

            usuario_db.password = bcrypt.generate_password_hash(
                datos["password"]
            ).decode("utf-8")

        # actualizo datos especificos segun el rol actual del usuario
        if usuario_db.rol == "admin":
            administrador = AdministradorModel.query.get(usuario_db.id_usuario)

            if administrador:
                administrador.legajo = datos.get("legajo", administrador.legajo)

        elif usuario_db.rol == "chofer":
            chofer = ChoferModel.query.get(usuario_db.id_usuario)

            if chofer:
                nueva_licencia = datos.get("licencia", chofer.licencia)
                nuevo_vencimiento = datos.get(
                    "vencimientoLicencia",
                    str(chofer.vencimientoLicencia)
                )

                licencia_valida, mensaje_error = Chofer.validar_licencia(
                    nueva_licencia
                )

                if not licencia_valida:
                    return jsonify({"mensaje": mensaje_error}), 400

                vencimiento_valido, mensaje_error = Chofer.validar_vencimiento_licencia(
                    nuevo_vencimiento
                )

                if not vencimiento_valido:
                    return jsonify({"mensaje": mensaje_error}), 400

                chofer.legajo = datos.get("legajo", chofer.legajo)
                chofer.licencia = nueva_licencia
                chofer.vencimientoLicencia = nuevo_vencimiento

        elif usuario_db.rol == "mecanico":
            mecanico = MecanicoModel.query.get(usuario_db.id_usuario)

            if mecanico:
                mecanico.legajo = datos.get("legajo", mecanico.legajo)
                mecanico.especialidad = datos.get(
                    "especialidad",
                    mecanico.especialidad
                )

        elif usuario_db.rol == "operador":
            operador = OperadorModel.query.get(usuario_db.id_usuario)

            if operador:
                operador.legajo = datos.get("legajo", operador.legajo)
                operador.sector = datos.get("sector", operador.sector)

        db.session.commit()

        return jsonify({
            "mensaje": "Usuario modificado correctamente",
            "usuario": usuario_db.to_dict()
        }), 200
        
    @staticmethod
    @jwt_required()
    def registrar_usuario():
        # obtengo el administrador que esta haciendo la accion
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        datos = request.get_json()

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
                return jsonify({"mensaje": f"Falta el campo {campo}"}), 400

        roles_validos = ["admin", "chofer", "mecanico", "operador"]

        if datos["rol"] not in roles_validos:
            return jsonify({"mensaje": "Rol no valido"}), 400

        estados_validos = ["pendiente", "activo", "inactivo"]

        if datos["estado"] not in estados_validos:
            return jsonify({"mensaje": "Estado no valido"}), 400

        usuario_existente = UsuarioModel.query.filter_by(
            username=datos["username"]
        ).first()

        if usuario_existente:
            return jsonify({"mensaje": "Ya existe un usuario con ese username"}), 409

        email_existente = UsuarioModel.query.filter_by(
            email=datos["email"]
        ).first()

        if email_existente:
            return jsonify({"mensaje": "Ya existe un usuario con ese email"}), 409

        password_valida, mensaje_error = Usuario.validar_password_registro(
            datos["password"]
        )

        if not password_valida:
            return jsonify({"mensaje": mensaje_error}), 400

        if datos["rol"] == "chofer":
            if "licencia" not in datos or datos["licencia"] == "":
                return jsonify({"mensaje": "Falta el campo licencia"}), 400

            if "vencimientoLicencia" not in datos or datos["vencimientoLicencia"] == "":
                return jsonify({"mensaje": "Falta el campo vencimientoLicencia"}), 400

            licencia_valida, mensaje_error = Chofer.validar_licencia(
                datos["licencia"]
            )

            if not licencia_valida:
                return jsonify({"mensaje": mensaje_error}), 400

            vencimiento_valido, mensaje_error = Chofer.validar_vencimiento_licencia(
                datos["vencimientoLicencia"]
            )

            if not vencimiento_valido:
                return jsonify({"mensaje": mensaje_error}), 400

        if datos["rol"] == "mecanico":
            if "especialidad" not in datos or datos["especialidad"] == "":
                return jsonify({"mensaje": "Falta el campo especialidad"}), 400

        if datos["rol"] == "operador":
            if "sector" not in datos or datos["sector"] == "":
                return jsonify({"mensaje": "Falta el campo sector"}), 400

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

        accion_realizada = admin.registrar_usuario(usuario_clase)

        if not accion_realizada:
            return jsonify({"mensaje": "No se pudo registrar el usuario"}), 400

        nuevo_usuario = UsuarioModel(
            username=usuario_clase.username,
            email=usuario_clase.email,
            password=usuario_clase.password,
            nombre=usuario_clase.nombre,
            apellido=usuario_clase.apellido,
            estado=usuario_clase.estado,
            rol=usuario_clase.rol,
        )

        db.session.add(nuevo_usuario)
        db.session.flush()

        if datos["rol"] == "admin":
            nuevo_especifico = AdministradorModel(
                Usuario_idUsuario=nuevo_usuario.id_usuario,
                legajo=datos["legajo"],
            )

        elif datos["rol"] == "chofer":
            nuevo_especifico = ChoferModel(
                Usuario_idUsuario=nuevo_usuario.id_usuario,
                licencia=datos["licencia"],
                vencimientoLicencia=datos["vencimientoLicencia"],
                legajo=datos["legajo"],
            )

        elif datos["rol"] == "mecanico":
            nuevo_especifico = MecanicoModel(
                Usuario_idUsuario=nuevo_usuario.id_usuario,
                legajo=datos["legajo"],
                especialidad=datos["especialidad"],
            )

        elif datos["rol"] == "operador":
            nuevo_especifico = OperadorModel(
                Usuario_idUsuario=nuevo_usuario.id_usuario,
                legajo=datos["legajo"],
                sector=datos["sector"],
            )

        db.session.add(nuevo_especifico)
        db.session.commit()

        datos_usuario = nuevo_usuario.to_dict()

        if datos["rol"] == "admin":
            datos_usuario["legajo"] = nuevo_especifico.legajo

        elif datos["rol"] == "chofer":
            datos_usuario["legajo"] = nuevo_especifico.legajo
            datos_usuario["licencia"] = nuevo_especifico.licencia
            datos_usuario["vencimientoLicencia"] = str(
                nuevo_especifico.vencimientoLicencia
            )

        elif datos["rol"] == "mecanico":
            datos_usuario["legajo"] = nuevo_especifico.legajo
            datos_usuario["especialidad"] = nuevo_especifico.especialidad

        elif datos["rol"] == "operador":
            datos_usuario["legajo"] = nuevo_especifico.legajo
            datos_usuario["sector"] = nuevo_especifico.sector

        return jsonify({
            "mensaje": "Usuario registrado correctamente",
            "usuario": datos_usuario
        }), 201 
        
    @staticmethod
    @jwt_required()
    def obtener_resumen_dashboard():
        admin = AdministradorController.obtener_admin_actual()

        if admin is None:
            return jsonify({"mensaje": "No tenes permiso para realizar esta accion"}), 403

        usuarios_activos = UsuarioModel.query.filter_by(
            estado="activo"
        ).count()

        usuarios_pendientes = UsuarioModel.query.filter_by(
            estado="pendiente",
            rol="chofer"
        ).all()

        choferes_pendientes = []

        for usuario in usuarios_pendientes:
            chofer = ChoferModel.query.filter_by(
                Usuario_idUsuario=usuario.id_usuario
            ).first()

            datos_usuario = usuario.to_dict()

            if chofer:
                datos_usuario["licencia"] = chofer.licencia
                datos_usuario["legajo"] = chofer.legajo
                datos_usuario["vencimientoLicencia"] = str(
                    chofer.vencimientoLicencia
                )
            else:
                datos_usuario["licencia"] = "-"

            choferes_pendientes.append(datos_usuario)

        camiones_registrados = CamionModel.query.count()

        camiones_disponibles = CamionModel.query.filter_by(
            estado="disponible"
        ).count()

        porcentaje_flota_disponible = Camion.calcular_porcentaje_disponible(
            camiones_disponibles,
            camiones_registrados
        )

        total_reportes = ReporteModel.query.count()

        reportes_abiertos = ReporteModel.query.filter(
            ReporteModel.estado != "resuelto"
        ).count()

        reportes_resueltos = ReporteModel.query.filter_by(
            estado="resuelto"
        ).count()

        porcentaje_reportes_resueltos = 0

        if total_reportes > 0:
            porcentaje_reportes_resueltos = round(
                (reportes_resueltos / total_reportes) * 100
            )

        reportes_prioridad_alta = 0

        hoy = date.today()

        viajes_del_dia = ViajeModel.query.filter(
            ViajeModel.fecha_salida == hoy
        ).count()

        viajes_en_curso = ViajeModel.query.filter(
            ViajeModel.estado == "en-curso"
        ).count()

        total_viajes = ViajeModel.query.count()

        viajes_finalizados = ViajeModel.query.filter_by(
            estado="finalizado"
        ).count()

        porcentaje_viajes_finalizados = 0

        if total_viajes > 0:
            porcentaje_viajes_finalizados = round(
                (viajes_finalizados / total_viajes) * 100
            )

        actividad_operativa = []

        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)

            cantidad_viajes = ViajeModel.query.filter(
                ViajeModel.fecha_salida == dia
            ).count()

            actividad_operativa.append(cantidad_viajes)

        return jsonify({
            "usuarios_activos": usuarios_activos,
            "camiones_registrados": camiones_registrados,
            "camiones_disponibles": camiones_disponibles,

            "reportes_abiertos": reportes_abiertos,
            "reportes_prioridad_alta": reportes_prioridad_alta,

            "viajes_del_dia": viajes_del_dia,
            "viajes_en_curso": viajes_en_curso,

            "estado_general": {
                "flota_disponible": porcentaje_flota_disponible,
                "reportes_resueltos": porcentaje_reportes_resueltos,
                "viajes_finalizados": porcentaje_viajes_finalizados,
            },

            "actividad_operativa": actividad_operativa,

            "usuarios_pendientes": choferes_pendientes,
        }), 200