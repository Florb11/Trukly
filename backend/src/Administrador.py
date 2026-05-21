from src.Usuario import Usuario


class Administrador(Usuario):
    def __init__(
        self,
        id_usuario,
        username,
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
            password,
            nombre,
            apellido,
            estado,
            rol,
        )

        self.legajo = legajo

    # activa un usuario si esta pendiente
    #junte estos dos metodos porque me parecia innecesario mantenerlos separados 
    def activar_usuario(self, usuario):
     if usuario.estado not in ["pendiente", "inactivo"]: #agregue inactivo
        return False

     usuario.estado = "activo"
     return True
 
    # desactiva un usuario pasandolo a inactivo (NO ELIMINAMOS LOS USUARIOS LOS DESACTIVAMOS)
    def desactivar_usuario(self, usuario):
     if usuario.id_usuario == self.id_usuario:
        return False

     if usuario.estado != "activo":
        return False

     usuario.estado = "inactivo"
     return True
 

    # modifica los datos de un usuario
    def modificar_usuario(self, usuario, username, nombre, apellido, rol):
        if usuario is None:
            return False

        usuario.username = username
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.rol = rol
        return True


    # registra un usuario (sin terminar)
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