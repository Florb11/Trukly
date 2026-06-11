from flask_jwt_extended import get_jwt, get_jwt_identity

from models.administrador_model import AdministradorModel
from models.mecanico_model import MecanicoModel
from models.usuario_model import UsuarioModel

from src.Administrador import Administrador
from src.Mecanico import Mecanico
from src.Usuario import Usuario


class AuthService:

    @staticmethod
    def obtener_id_usuario_actual():
        identidad = get_jwt_identity()

        try:
            return int(identidad)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def obtener_rol_actual():
        return get_jwt().get("rol")

    @staticmethod
    def obtener_usuario_model_actual():
        id_usuario = AuthService.obtener_id_usuario_actual()

        if id_usuario is None:
            return None

        usuario = UsuarioModel.query.get(id_usuario)

        if usuario is None:
            return None

        if usuario.estado != Usuario.ESTADO_ACTIVO:
            return None

        return usuario

    @staticmethod
    def obtener_admin_actual_desde_token():
        usuario = AuthService.obtener_usuario_model_actual()

        if usuario is None:
            return None

        if (
            AuthService.obtener_rol_actual() != Usuario.ROL_ADMIN
            or usuario.rol != Usuario.ROL_ADMIN
        ):
            return None

        administrador = AdministradorModel.query.get(
            usuario.id_usuario
        )

        if administrador is None:
            return None

        return Administrador.crear_desde_datos(
            {
                "id_usuario": usuario.id_usuario,
                "username": usuario.username,
                "email": usuario.email,
                "password": usuario.password,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "estado": usuario.estado,
                "rol": usuario.rol,
                "legajo": administrador.legajo,
                "foto_perfil": usuario.foto_perfil,
            }
        )

    @staticmethod
    def obtener_mecanico_actual_desde_token():
        usuario = AuthService.obtener_usuario_model_actual()

        if usuario is None:
            return None

        if (
            AuthService.obtener_rol_actual() != Usuario.ROL_MECANICO
            or usuario.rol != Usuario.ROL_MECANICO
        ):
            return None

        mecanico = MecanicoModel.query.get(usuario.id_usuario)

        if mecanico is None:
            return None

        return Mecanico.crear_desde_datos(
            {
                "id_usuario": usuario.id_usuario,
                "username": usuario.username,
                "email": usuario.email,
                "password": usuario.password,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "estado": usuario.estado,
                "rol": usuario.rol,
                "legajo": mecanico.legajo,
                "especialidad": mecanico.especialidad,
                "foto_perfil": usuario.foto_perfil,
            }
        )