from src.Usuario import Usuario


class Administrador(Usuario):
    def __init__(
        self,
        id_usuario,
        username,
        email,
        password,
        nombre,
        apellido,
        estado,
        rol,
        legajo,
    ):
        super().__init__(
            id_usuario,
            username,
            email,
            password,
            nombre,
            apellido,
            estado,
            rol,
        )

        self.legajo = legajo

    # activa un usuario si esta pendiente o inactivo
    def activar_usuario(self, usuario):
        if usuario.estado not in ["pendiente", "inactivo"]:
            return False

        usuario.estado = "activo"
        return True

    # desactiva un usuario pasandolo a inactivo
    # no eliminamos usuarios, los desactivamos
    def desactivar_usuario(self, usuario):
        if usuario.id_usuario == self.id_usuario:
            return False

        if usuario.estado != "activo":
            return False

        usuario.estado = "inactivo"
        return True

    # modifica los datos generales de un usuario
    # no modificamos el rol desde aca
    def modificar_usuario(self, usuario, username, email, nombre, apellido, estado):
        if usuario is None:
            return False

        usuario.username = username
        usuario.email = email
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.estado = estado
        return True

    # registra un usuario, queda para mas adelante
    def registrar_usuario(self, usuario):
        if usuario is None:
            return False

        return True

    # uso el diccionario del padre y agrego el legajo del admin
    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "legajo": self.legajo,
            }
        )

        return datos_usuario