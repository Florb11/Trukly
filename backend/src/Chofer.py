from src.Usuario import Usuario


class Chofer(Usuario):
    def __init__(
        self,
        idUsuario,
        username,
        password,
        nombre,
        apellido,
        estado,
        legajo,
        licencia,
        vencimientoLicencia,
        viajesAsignados=None,
    ):
        super().__init__(idUsuario, username, password, nombre, apellido, estado)
        self.legajo = legajo
        self.licencia = licencia
        self.vencimientoLicencia = vencimientoLicencia
        self.viajesAsignados = viajesAsignados or []