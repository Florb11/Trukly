from datetime import datetime


class ReporteFalla:
    ESTADOS_VALIDOS = ["pendiente", "en revision", "resuelto", "cancelado"]

    def __init__(
        self,
        id_reporte,
        fecha_hora,
        descripcion,
        estado,
        Camion_id_camion,
        Mecanico_Usuario_idUsuario,
        Chofer_Usuario_idUsuario,
        nota_reparacion=None,
        fecha_resolucion=None,
    ):
        self.id_reporte = id_reporte
        self.fecha_hora = fecha_hora
        self.descripcion = descripcion
        self.estado = estado
        self.Camion_id_camion = Camion_id_camion
        self.Mecanico_Usuario_idUsuario = Mecanico_Usuario_idUsuario
        self.Chofer_Usuario_idUsuario = Chofer_Usuario_idUsuario
        self.nota_reparacion = nota_reparacion
        self.fecha_resolucion = fecha_resolucion

    @staticmethod
    def formatear_fecha(fecha):
        if fecha is None:
            return None

        if hasattr(fecha, "strftime"):
            return fecha.strftime("%Y-%m-%d %H:%M:%S")

        return fecha

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
        if self.estado not in self.ESTADOS_VALIDOS:
            return False

        return True

    # cambia el estado del reporte si es valido
    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return False

        self.estado = nuevo_estado
        return True

    # asigna un mecanico al reporte y lo pasa a revision
    def asignar_mecanico(self, id_mecanico):
        if not id_mecanico:
            return False

        self.Mecanico_Usuario_idUsuario = id_mecanico
        self.estado = "en revision"
        return True

    # valida si un mecanico puede resolver este reporte
    def puede_ser_resuelto_por(self, id_mecanico, nota_reparacion):
        return (
            self.Mecanico_Usuario_idUsuario == id_mecanico
            and self.estado != "resuelto"
            and nota_reparacion is not None
            and nota_reparacion.strip() != ""
        )

    # resuelve el reporte guardando nota y fecha de resolucion
    def resolver_por_mecanico(self, id_mecanico, nota_reparacion):
        if not self.puede_ser_resuelto_por(id_mecanico, nota_reparacion):
            return False

        self.estado = "resuelto"
        self.nota_reparacion = nota_reparacion
        self.fecha_resolucion = datetime.now()

        return True

    def to_dict(self):
        return {
            "id_reporte": self.id_reporte,
            "fecha_hora": self.formatear_fecha(self.fecha_hora),
            "descripcion": self.descripcion,
            "estado": self.estado,
            "Camion_id_camion": self.Camion_id_camion,
            "Mecanico_Usuario_idUsuario": self.Mecanico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "nota_reparacion": self.nota_reparacion,
            "fecha_resolucion": self.formatear_fecha(self.fecha_resolucion),
        }