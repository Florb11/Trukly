from utils.domain_helpers import texto_valido


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

    @classmethod
    def crear_desde_datos(cls, datos, viaje=None):
        if datos is None:
            return None

        carga = cls(
            id_carga=datos.get("id_carga"),
            descripcion=datos.get("descripcion"),
            tipo=datos.get("tipo"),
            peso=datos.get("peso"),
            estado=datos.get("estado"),
            id_viaje=datos.get("id_viaje"),
            viaje=viaje,
        )

        if viaje is not None:
            carga.asociar_viaje(viaje)

        return carga

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
        if not texto_valido(self.descripcion):
            return False

        if not texto_valido(self.tipo):
            return False

        if not texto_valido(self.peso):
            return False

        if not texto_valido(self.estado):
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
