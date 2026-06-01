class Camion:
    def __init__(
        self,
        id_camion,
        matricula,
        marca,
        modelo,
        capacidad_carga,
        estado,
        nroTanque,
    ):
        self.id_camion = id_camion
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo
        self.capacidad_carga = capacidad_carga
        self.estado = estado
        self.nroTanque = nroTanque

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
        estados_validos = ["disponible", "en viaje", "en mantenimiento", "inactivo"]

        if self.estado not in estados_validos:
            return False

        return True

    # cambia el estado del camion si es valido
    def cambiar_estado(self, nuevo_estado):
        estados_validos = ["disponible", "en viaje", "en mantenimiento", "inactivo"]

        if nuevo_estado not in estados_validos:
            return False

        self.estado = nuevo_estado
        return True

    # si el camion esta disponible para asignarlo a un viaje
    def esta_disponible(self):
        return self.estado == "disponible"
    # porcentaje d camiones disponible para el dash
    @staticmethod
    def calcular_porcentaje_disponible(camiones_disponibles, camiones_totales):
        if camiones_totales == 0:
            return 0

        return round((camiones_disponibles / camiones_totales) * 100) # round redondear un numero a una cantidad especifica de decimales

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