from src.Usuario import Usuario 


class OperadorLogistico(Usuario):
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
        sector,
        viajesGestionados=None,
        camionesAsignados=None,
    ):
        super().__init__(idUsuario, username, password, nombre, apellido, estado)
        self.legajo = legajo
        self.sector = sector
        self.viajesGestionados = viajesGestionados or []
        self.camionesAsignados = camionesAsignados or []