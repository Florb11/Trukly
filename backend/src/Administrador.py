from src.Usuario import Usuario #Python necesita saber que es Usuario entonces lo importo


class Administrador(Usuario):
    def __init__(
        self,
        id_usuario,
        username,
        password,
        nombre,
        apellido,
        estado,
        legajo,
        usuarios_gestionados=None,
        reportes_falla=None,
        camiones_gestionados=None,
    ):
        #El or [] se usa para que, si no te pasan una lista, se cree una lista vacia
        super().__init__(id_usuario, username, password, nombre, apellido, estado)
        self.legajo = legajo
        self.usuarios_gestionados = usuarios_gestionados or []
        self.reportes_falla = reportes_falla or []
        self.camiones_gestionados = camiones_gestionados or []