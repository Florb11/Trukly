from src.Usuario import Usuario


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
            or self.id_usuario is not None
            and str(self.id_usuario).strip() != ""
        )

    @staticmethod
    def formatear_fecha(fecha):
        if fecha is None:
            return None

        if hasattr(fecha, "strftime"):
            return fecha.strftime("%Y-%m-%d %H:%M:%S")

        return fecha

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
            "fecha_hora": self.formatear_fecha(self.fecha_hora),
            "tipo": self.tipo,
        }