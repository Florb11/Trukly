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
        # Lee el id del usuario que viene guardado en el token
        identidad = get_jwt_identity()

        try:
            # Lo convierte a int porque en el token se guarda como string
            return int(identidad)

        except (TypeError, ValueError):
            # Si el token no trae un id valido, devuelve None
            return None

    @staticmethod
    def obtener_rol_actual():
        # Lee el rol que viene del token
        return get_jwt().get("rol")

    @staticmethod
    def obtener_usuario_model_actual():
        # Obtiene el id del usuario logueado desde el token
        id_usuario = AuthService.obtener_id_usuario_actual()

        # Si no hay id valido, no hay usuario actual
        if id_usuario is None:
            return None

        # Busca el usuario en la base de datos
        usuario = UsuarioModel.query.get(id_usuario)

        # Si no existe en BD, corta
        if usuario is None:
            return None

        # Valida que el usuario este activo
        if usuario.estado != Usuario.ESTADO_ACTIVO:
            return None

        # Devuelve el modelo SQLAlchemy del usuario
        return usuario

    @staticmethod
    def obtener_admin_actual_desde_token():
        # Busca el usuario actual en BD y valida que este activo
        usuario = AuthService.obtener_usuario_model_actual()

        # Si no hay usuario valido, no puede continuar
        if usuario is None:
            return None

        # Valida que el rol del token y el rol de la BD sean admin
        if (
            AuthService.obtener_rol_actual() != Usuario.ROL_ADMIN
            or usuario.rol != Usuario.ROL_ADMIN
        ):
            return None

        # Busca los datos especificos del administrador
        administrador = AdministradorModel.query.get(
            usuario.id_usuario
        )

        # Si no existe como administrador, corta
        if administrador is None:
            return None

        # Arma el objeto Administrador
        return Administrador(
            usuario.id_usuario,
            usuario.username,
            usuario.email,
            usuario.password,
            usuario.nombre,
            usuario.apellido,
            usuario.estado,
            usuario.rol,
            administrador.legajo,
            foto_perfil=usuario.foto_perfil,
        )

    @staticmethod
    def obtener_mecanico_actual_desde_token():
        # Busca el usuario actual en BD y valida que este activo
        usuario = AuthService.obtener_usuario_model_actual()

        # Si no hay usuario valido, no puede continuar
        if usuario is None:
            return None

        # Valida que el rol del token y el rol de la BD sean mecanico
        if (
            AuthService.obtener_rol_actual() != Usuario.ROL_MECANICO
            or usuario.rol != Usuario.ROL_MECANICO #Esto evita que un token viejo siga funcionando si el rol cambio
        ):
            return None

        # Busca los datos especificos del mecanico
        mecanico = MecanicoModel.query.get(usuario.id_usuario)

        # Si no existe como mecanico, corta
        if mecanico is None:
            return None

        # Arma el objeto Mecanico
        return Mecanico(
            id_usuario=usuario.id_usuario,
            username=usuario.username,
            email=usuario.email,
            password=usuario.password,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            estado=usuario.estado,
            rol=usuario.rol,
            legajo=mecanico.legajo,
            especialidad=mecanico.especialidad,
            foto_perfil=usuario.foto_perfil,
        )