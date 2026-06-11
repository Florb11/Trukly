class Carga:
    def __init__(
        self,
        id_carga,
        descripcion,
        tipo,
        peso,
        estado,
        id_viaje,
        viaje=None,
    ):
        self.id_carga = id_carga
        self.descripcion = descripcion
        self.tipo = tipo
        self.peso = peso
        self.estado = estado
        self.id_viaje = id_viaje
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
        self.id_viaje = id_viaje
        return True

    def tiene_viaje_asociado(self):
        return (
            self.viaje is not None
            or self.texto_valido(self.id_viaje)
        )

    def validar_datos(self):
        if not self.texto_valido(self.descripcion):
            return False

        if not self.texto_valido(self.tipo):
            return False

        if not self.texto_valido(self.peso):
            return False

        if not self.texto_valido(self.estado):
            return False

        if not self.tiene_viaje_asociado():
            return False

        return True

    def to_dict(self):
        return {
            "id_carga": self.id_carga,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "peso": self.peso,
            "estado": self.estado,
            "id_viaje": self.id_viaje,
        }
