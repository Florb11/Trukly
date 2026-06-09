class Notificacion:
    def __init__(
        self,
        id_notificacion,
        Usuario_idUsuario,
        titulo,
        mensaje,
        leida,
        fecha_hora,
        tipo=None,
    ):
        self.id_notificacion = id_notificacion
        self.Usuario_idUsuario = Usuario_idUsuario
        self.titulo = titulo
        self.mensaje = mensaje
        self.leida = leida
        self.fecha_hora = fecha_hora
        self.tipo = tipo

    @staticmethod
    def formatear_fecha(fecha):
        if fecha is None:
            return None

        if hasattr(fecha, "strftime"):
            return fecha.strftime("%Y-%m-%d %H:%M:%S")

        return fecha

    def validar_datos(self):
        if not self.Usuario_idUsuario:
            return False

        if not self.titulo or self.titulo.strip() == "":
            return False

        if not self.mensaje or self.mensaje.strip() == "":
            return False

        if self.fecha_hora is None:
            return False

        return True

    def puede_ser_modificada_por(self, id_usuario, rol):
        if rol == "admin":
            return True

        return str(self.Usuario_idUsuario) == str(id_usuario)

    def marcar_como_leida(self, id_usuario, rol):
        if not self.puede_ser_modificada_por(id_usuario, rol):
            return False

        self.leida = True
        return True

    def to_dict(self):
        return {
            "id_notificacion": self.id_notificacion,
            "Usuario_idUsuario": self.Usuario_idUsuario,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "leida": self.leida,
            "fecha_hora": self.formatear_fecha(self.fecha_hora),
            "tipo": self.tipo,
        }