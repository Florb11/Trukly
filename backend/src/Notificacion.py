from src.Usuario import Usuario


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
        usuario=None,
    ):
        self.id_notificacion = id_notificacion
        self.Usuario_idUsuario = Usuario_idUsuario
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
        self.Usuario_idUsuario = id_usuario
        return True

    def tiene_usuario_destino(self):
        return (
            self.usuario is not None
            or self.Usuario_idUsuario is not None
            and str(self.Usuario_idUsuario).strip() != ""
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

    def puede_ser_modificada_por(self, id_usuario, rol):
        if rol == Usuario.ROL_ADMIN:
            return True

        return str(self.Usuario_idUsuario) == str(id_usuario)

    def pertenece_a_usuario(self, usuario):
        id_usuario = self.obtener_id_usuario(usuario)

        if not id_usuario:
            return False

        return str(self.Usuario_idUsuario) == str(id_usuario)

    def puede_ser_modificada_por_usuario(self, usuario):
        if usuario is None:
            return False

        if getattr(usuario, "rol", None) == Usuario.ROL_ADMIN:
            return True

        return self.pertenece_a_usuario(usuario)

    def marcar_como_leida(self, id_usuario, rol):
        if not self.puede_ser_modificada_por(id_usuario, rol):
            return False

        self.leida = True
        return True

    def marcar_como_leida_por(self, usuario):
        if not self.puede_ser_modificada_por_usuario(usuario):
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