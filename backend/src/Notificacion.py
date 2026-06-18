from src.Usuario import Usuario
from utils.domain_helpers import formatear_fecha, texto_valido


class Notificacion:
    def __init__(
        self,
        id_notificacion,
        id_usuario,
        titulo,
        mensaje,
        leida,
        fecha_hora,
        tipo=None,
        usuario=None,
    ):
        self.id_notificacion = id_notificacion
        self.id_usuario = id_usuario
        self.titulo = titulo
        self.mensaje = mensaje
        self.leida = leida
        self.fecha_hora = fecha_hora
        self.tipo = tipo
        self.usuario = usuario

    @classmethod
    def crear_desde_datos(cls, datos, usuario=None):
        if datos is None:
            return None

        notificacion = cls(
            id_notificacion=datos.get("id_notificacion"),
            id_usuario=datos.get("id_usuario"),
            titulo=datos.get("titulo"),
            mensaje=datos.get("mensaje"),
            leida=datos.get("leida", False),
            fecha_hora=datos.get("fecha_hora"),
            tipo=datos.get("tipo"),
        )

        if usuario is not None:
            notificacion.asignar_usuario(usuario)

        return notificacion

    @staticmethod
    def obtener_id_usuario(usuario):
        # obtiene el id del usuario recibido
        if usuario is None:
            return None

        return getattr(usuario, "id_usuario", None)

    def asignar_usuario(self, usuario):
        # asigna el usuario destino de la notificacion
        id_usuario = self.obtener_id_usuario(usuario)

        if id_usuario is None:
            return False

        self.usuario = usuario
        self.id_usuario = id_usuario
        return True

    def tiene_usuario_destino(self):
        # valida que exista un usuario destino
        return (
            self.usuario is not None
            or self.id_usuario is not None
        )

    def validar_datos(self):
        # valida datos minimos de la notificacion
        if not self.tiene_usuario_destino():
            return False

        if not texto_valido(self.titulo):
            return False

        if not texto_valido(self.mensaje):
            return False

        if self.fecha_hora is None:
            return False

        return True

    def pertenece_a_usuario(self, usuario):
        # valida si la notificacion pertenece al usuario
        id_usuario = self.obtener_id_usuario(usuario)

        if id_usuario is None:
            return False

        return str(self.id_usuario) == str(id_usuario)

    def usuario_es_admin(self, usuario):
        # valida si el usuario tiene rol admin
        if usuario is None:
            return False

        return getattr(usuario, "rol", None) == Usuario.ROL_ADMIN

    def puede_ser_modificada_por_usuario(self, usuario):
        # valida permisos para modificar la notificacion
        if usuario is None:
            return False

        if self.usuario_es_admin(usuario):
            return True

        return self.pertenece_a_usuario(usuario)

    def marcar_como_leida_por(self, usuario):
        # marca como leida si el usuario tiene permiso
        if not self.puede_ser_modificada_por_usuario(usuario):
            return False

        self.leida = True
        return True

    def to_dict(self):
        return {
            "id_notificacion": self.id_notificacion,
            "id_usuario": self.id_usuario,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "leida": self.leida,
            "fecha_hora": formatear_fecha(
                self.fecha_hora,
                incluir_hora=True
            ),
            "tipo": self.tipo,
        }