from src.Usuario import Usuario


class Chofer(Usuario):
    def __init__(
        self,
        id_usuario,
        username,
        password,
        nombre,
        apellido,
        estado,
        rol,
        licencia,
        vencimientoLicencia,
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

        self.licencia = licencia
        self.vencimientoLicencia = vencimientoLicencia
        self.legajo = legajo

    
    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "licencia": self.licencia,
                "vencimientoLicencia": self.vencimientoLicencia,
                "legajo": self.legajo,
            }
        )

        return datos_usuario