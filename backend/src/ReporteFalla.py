class ReporteFalla:
    def __init__(
        self,
        id_reporte,
        fecha_hora,
        descripcion,
        estado,
        Camion_id_camion,
        Mecanico_Usuario_idUsuario,
        Chofer_Usuario_idUsuario,
    ):
        self.id_reporte = id_reporte
        self.fecha_hora = fecha_hora
        self.descripcion = descripcion
        self.estado = estado
        self.Camion_id_camion = Camion_id_camion
        self.Mecanico_Usuario_idUsuario = Mecanico_Usuario_idUsuario
        self.Chofer_Usuario_idUsuario = Chofer_Usuario_idUsuario

    # valida que el reporte tenga los datos principales
    def validar_datos(self):
        if not self.descripcion:
            return False

        if not self.Camion_id_camion:
            return False

        if not self.Chofer_Usuario_idUsuario:
            return False

        return True

    # valida que el estado sea uno de los permitidos
    def validar_estado(self):
        estados_validos = ["pendiente", "en revision", "resuelto", "cancelado"]

        if self.estado not in estados_validos:
            return False

        return True

    # cambia el estado del reporte si es valido
    def cambiar_estado(self, nuevo_estado):
        estados_validos = ["pendiente", "en revision", "resuelto", "cancelado"]

        if nuevo_estado not in estados_validos:
            return False

        self.estado = nuevo_estado
        return True

    # asigna un mecanico al reporte
    def asignar_mecanico(self, id_mecanico):
        if not id_mecanico:
            return False

        self.Mecanico_Usuario_idUsuario = id_mecanico
        return True

    def to_dict(self):
        return {
            "id_reporte": self.id_reporte,
            "fecha_hora": self.fecha_hora,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "Camion_id_camion": self.Camion_id_camion,
            "Mecanico_Usuario_idUsuario": self.Mecanico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
        }