from utils.domain_helpers import texto_valido


class RegistroIngresoSalida:
    def __init__(
        self,
        id_registro,
        fecha_hora,
        tipo_registro,
        observacion,
        id_viaje,
        viaje=None,
    ):
        self.id_registro = id_registro
        self.fecha_hora = fecha_hora
        self.tipo_registro = tipo_registro
        self.observacion = observacion
        self.id_viaje = id_viaje
        self.viaje = viaje

    @staticmethod
    def obtener_id_viaje(viaje):
        if viaje is None:
            return None

        return getattr(viaje, "id_viaje", None)

    def asociar_viaje(self, viaje):
        id_viaje = self.obtener_id_viaje(viaje)

        if not id_viaje:
            return False

        self.viaje = viaje
        self.id_viaje = id_viaje
        return True

    def tiene_viaje_asociado(self):
        return (
            self.viaje is not None
            or texto_valido(self.id_viaje)
        )

    def validar_datos(self):
        if self.fecha_hora is None:
            return False

        if not texto_valido(self.tipo_registro):
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
            "id_viaje": self.id_viaje,
        }