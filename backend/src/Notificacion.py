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
        if usuario is None:
            return None

        return getattr(usuario, "id_usuario", None)

    def asignar_usuario(self, usuario):
        id_usuario = self.obtener_id_usuario(usuario)

        if not id_usuario:
            return False

        self.usuario = usuario
        self.id_usuario = id_usuario
        return True

    def tiene_usuario_destino(self):
        return (
            self.usuario is not None
            or texto_valido(self.id_usuario)
        )

    def validar_datos(self):
        if not self.tiene_usuario_destino():
            return False

        if not self.titulo or self.titulo.strip() == "":
            return False

        if not self.mensaje or self.mensaje.strip() == "":
            return False

        if self.fecha_hora is None:
            return False

        return True

    def pertenece_a_usuario(self, usuario):
        id_usuario = self.obtener_id_usuario(usuario)

        if not id_usuario:
            return False

        return str(self.id_usuario) == str(id_usuario)

    def puede_ser_modificada_por_usuario(self, usuario):
        if usuario is None:
            return False

        if getattr(usuario, "rol", None) == Usuario.ROL_ADMIN:
            return True

        return self.pertenece_a_usuario(usuario)

    def marcar_como_leida_por(self, usuario):
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