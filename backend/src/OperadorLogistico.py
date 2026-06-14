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
    
    def puede_gestionar_viaje(self, viaje):
        if viaje is None:
            return False
        return True

    def crear_viaje(self, viaje):
        if viaje is None:
            return False
        return self.gestionar_viaje(viaje)

    def asignar_chofer_a_viaje(self, chofer, viaje):
        if chofer is None or viaje is None:
            return False
        return viaje.asignar_chofer(chofer)

    def agregar_carga_a_viaje(self, carga, viaje):
        if carga is None or viaje is None:
            return False
        return viaje.agregar_carga(carga)

    def cancelar_viaje(self, viaje, motivo):
        if viaje is None:
            return False
        return viaje.cancelar(motivo)

    def asignar_mecanico_a_reporte(self, mecanico, reporte):
        if mecanico is None or reporte is None:
            return False
        return reporte.asignar_mecanico(mecanico)
    
    def editar_viaje(self, viaje, datos):
        if viaje is None:
            return False, "Viaje no encontrado"

        if not viaje.pertenece_a_operador(self):
            return False, "No tenés permiso para editar este viaje"

        if not viaje.puede_editarse():
            return False, "No se puede editar un viaje cancelado o finalizado"

        if datos.get("origen"):
            viaje.origen = datos["origen"]
        if datos.get("destino"):
            viaje.destino = datos["destino"]
        if datos.get("fecha_salida"):
            viaje.fecha_salida = datos["fecha_salida"]
        if datos.get("fecha_llegada"):
            viaje.fecha_llegada = datos["fecha_llegada"]
        if datos.get("recorrido") is not None:
            viaje.recorrido = datos["recorrido"]
        if datos.get("observaciones") is not None:
            viaje.observaciones = datos["observaciones"]
        if datos.get("Chofer_Usuario_idUsuario"):
            viaje.id_chofer = datos["Chofer_Usuario_idUsuario"]
        if datos.get("Camion_id_camion"):
            viaje.id_camion = datos["Camion_id_camion"]

        return True, None