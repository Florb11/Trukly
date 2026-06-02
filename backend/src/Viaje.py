
class Viaje:
    def __init__(
        self,
        id_viaje,
        fecha_salida,
        fecha_llegada,
        origen,
        destino,
        estado,
        observaciones,
        recorrido,
        OperadorLogistico_Usuario_idUsuario,
        Chofer_Usuario_idUsuario,
        Camion_id_camion
    ):
        self.id_viaje = id_viaje
        self.fecha_salida = fecha_salida
        self.fecha_llegada = fecha_llegada
        self.origen = origen
        self.destino = destino
        self.estado = estado
        self.observaciones = observaciones
        self.recorrido = recorrido
        self.OperadorLogistico_Usuario_idUsuario = OperadorLogistico_Usuario_idUsuario
        self.Chofer_Usuario_idUsuario = Chofer_Usuario_idUsuario
        self.Camion_id_camion = Camion_id_camion

    def to_dict(self):
        return {
            "id_viaje": self.id_viaje,
            "fecha_salida": self.fecha_salida,
            "fecha_llegada": self.fecha_llegada,
            "origen": self.origen,
            "destino": self.destino,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "recorrido": self.recorrido,
            "OperadorLogistico_Usuario_idUsuario": self.OperadorLogistico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "Camion_id_camion": self.Camion_id_camion
        }