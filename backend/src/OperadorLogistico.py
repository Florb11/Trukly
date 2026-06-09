from src.Usuario import Usuario


class OperadorLogistico(Usuario):
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
        sector,
        foto_perfil=None,
        viajes_gestionados=None,
        camiones_asignados=None,
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
            foto_perfil,
        )

        self.legajo = legajo
        self.sector = sector
        self.viajes_gestionados = viajes_gestionados or []
        self.camiones_asignados = camiones_asignados or []

    def gestionar_viaje(self, viaje):
        if viaje is None:
            return False

        if not viaje.asignar_operador(self):
            return False

        self.viajes_gestionados.append(viaje)
        return True

    def asignar_camion_a_viaje(self, camion, viaje):
        if camion is None or viaje is None:
            return False

        if not viaje.asignar_camion(camion):
            return False

        if not camion.asignar_viaje(viaje):
            return False

        self.camiones_asignados.append(camion)
        return True

    def puede_ver_viaje(self, viaje):
        if viaje is None:
            return False

        return viaje.pertenece_a_operador(self)

    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "legajo": self.legajo,
                "sector": self.sector,
            }
        )

        return datos_usuario