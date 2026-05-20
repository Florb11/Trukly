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

    # revisa si puede activar al usuario
    def puede_activar_usuario(self, usuario):
        return usuario.estado == "pendiente"

    # cambia el estado del usuario recibido
    # no guarda en la base, eso lo hace el controller
    def activar_usuario(self, usuario):
        usuario.estado = "activo"
        return usuario

    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "legajo": self.legajo,
            }
        )

        return datos_usuario