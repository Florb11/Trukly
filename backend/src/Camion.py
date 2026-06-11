class Camion:
    ESTADO_DISPONIBLE = "disponible"
    ESTADO_EN_VIAJE = "en viaje"
    ESTADO_EN_MANTENIMIENTO = "en mantenimiento"
    ESTADO_INACTIVO = "inactivo"

    ESTADOS_VALIDOS = [
        ESTADO_DISPONIBLE,
        ESTADO_EN_VIAJE,
        ESTADO_EN_MANTENIMIENTO,
        ESTADO_INACTIVO,
    ]

    def __init__(
        self,
        id_camion,
        matricula,
        marca,
        modelo,
        capacidad_carga,
        estado,
        nroTanque,
        viajes_asignados=None,
        reportes_falla=None,
    ):
        self.id_camion = id_camion
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo
        self.capacidad_carga = capacidad_carga
        self.estado = estado
        self.nroTanque = nroTanque
        self.viajes_asignados = viajes_asignados or []
        self.reportes_falla = reportes_falla or []

    def asignar_viaje(self, viaje):
        if viaje is None:
            return False

        if not self.esta_disponible():
            return False

        if not viaje.asignar_camion(self):
            return False

        self.viajes_asignados.append(viaje)
        return True

    def registrar_reporte(self, reporte):
        if reporte is None:
            return False

        if not reporte.asociar_camion(self):
            return False

        self.reportes_falla.append(reporte)
        return True

    # valida que los datos principales del camion esten completos
    def validar_datos(self):
        if not self.matricula:
            return False

        if not self.marca:
            return False

        if not self.modelo:
            return False

        if self.capacidad_carga is None:
            return False

        if self.capacidad_carga <= 0:
            return False

        if not self.estado:
            return False

        if self.nroTanque is None:
            return False

        return True

    # valida que el estado sea uno de los permitidos
    def validar_estado(self):
        if self.estado not in self.ESTADOS_VALIDOS:
            return False

        return True

    # cambia el estado del camion si es valido
    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return False

        self.estado = nuevo_estado
        return True

    # si el camion esta disponible para asignarlo a un viaje
    def esta_disponible(self):
        return self.estado == self.ESTADO_DISPONIBLE

    def esta_en_mantenimiento(self):
        return self.estado == self.ESTADO_EN_MANTENIMIENTO

    def marcar_disponible(self):
        return self.cambiar_estado(self.ESTADO_DISPONIBLE)

    def puede_entrar_en_mantenimiento(self):
        return self.estado != self.ESTADO_INACTIVO

    def marcar_en_mantenimiento(self):
        if not self.puede_entrar_en_mantenimiento():
            return False

        return self.cambiar_estado(self.ESTADO_EN_MANTENIMIENTO)

    def puede_liberarse_de_mantenimiento(self, reportes_activos):
        return (
            self.esta_en_mantenimiento()
            and len(reportes_activos) == 0
        )

    def liberar_si_no_tiene_reportes_activos(self, reportes_activos):
        if not self.puede_liberarse_de_mantenimiento(reportes_activos):
            return False

        return self.marcar_disponible()

    def ajustar_estado_por_reportes_activos(self, cantidad_reportes_activos):
        if (
            cantidad_reportes_activos > 0
            and self.estado == self.ESTADO_DISPONIBLE
        ):
            self.estado = self.ESTADO_EN_MANTENIMIENTO
            return True

        return False

    def to_dict(self):
        return {
            "id_camion": self.id_camion,
            "matricula": self.matricula,
            "marca": self.marca,
            "modelo": self.modelo,
            "capacidad_carga": self.capacidad_carga,
            "estado": self.estado,
            "nroTanque": self.nroTanque,
        }

