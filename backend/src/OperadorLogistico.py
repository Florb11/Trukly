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

    @classmethod
    def crear_desde_datos(cls, datos):
        if datos is None:
            return None

        return cls(
            id_usuario=datos.get("id_usuario"),
            username=datos.get("username"),
            email=datos.get("email"),
            password=datos.get("password"),
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido"),
            estado=datos.get("estado"),
            rol=datos.get("rol"),
            legajo=datos.get("legajo"),
            sector=datos.get("sector"),
            foto_perfil=datos.get("foto_perfil"),
        )

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