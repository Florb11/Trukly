class RegistroIngresoSalida:
    def __init__(
        self,
        id_registro,
        fecha_hora,
        tipo_registro,
        observacion,
        Viaje_id_viaje,
        viaje=None,
    ):
        self.id_registro = id_registro
        self.fecha_hora = fecha_hora
        self.tipo_registro = tipo_registro
        self.observacion = observacion
        self.Viaje_id_viaje = Viaje_id_viaje
        self.viaje = viaje

    @staticmethod
    def obtener_id_viaje(viaje):
        if viaje is None:
            return None

        return getattr(viaje, "id_viaje", None)

    @staticmethod
    def texto_valido(valor):
        return valor is not None and str(valor).strip() != ""

    def asociar_viaje(self, viaje):
        id_viaje = self.obtener_id_viaje(viaje)

        if not id_viaje:
            return False

        self.viaje = viaje
        self.Viaje_id_viaje = id_viaje
        return True

    def tiene_viaje_asociado(self):
        return (
            self.viaje is not None
            or self.texto_valido(self.Viaje_id_viaje)
        )

    def validar_datos(self):
        if self.fecha_hora is None:
            return False

        if not self.texto_valido(self.tipo_registro):
            return False

        if not self.tiene_viaje_asociado():
            return False

        return True

    def to_dict(self):
        return {
            "id_registro": self.id_registro,
            "fecha_hora": self.fecha_hora,
            "tipo_registro": self.tipo_registro,
            "observacion": self.observacion,
            "Viaje_id_viaje": self.Viaje_id_viaje,
        }