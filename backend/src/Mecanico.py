from src.Usuario import Usuario


class Mecanico(Usuario):
    def __init__(
        self,
        idUsuario,
        username,
        password,
        email,
        nombre,
        apellido,
        estado,
        legajo,
        especialidad,
    ):
        super().__init__(idUsuario, username, password, nombre, apellido, estado)
        self.legajo = legajo
        self.especialidad = especialidad