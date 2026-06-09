from datetime import datetime


class ReporteFalla:
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_EN_REVISION = "en revision"
    ESTADO_RESUELTO = "resuelto"
    ESTADO_CANCELADO = "cancelado"

    ESTADOS_VALIDOS = [
        ESTADO_PENDIENTE,
        ESTADO_EN_REVISION,
        ESTADO_RESUELTO,
        ESTADO_CANCELADO,
    ]
    ESTADOS_ACTIVOS = [
        ESTADO_PENDIENTE,
        ESTADO_EN_REVISION,
    ]

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
        camion=None,
        mecanico=None,
        chofer=None,
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
        self.camion = camion
        self.mecanico = mecanico
        self.chofer = chofer

    @staticmethod
    def obtener_id_usuario(usuario):
        if usuario is None:
            return None

        return getattr(usuario, "id_usuario", None)

    @staticmethod
    def obtener_id_camion(camion):
        if camion is None:
            return None

        return getattr(camion, "id_camion", None)

    def asociar_camion(self, camion):
        id_camion = self.obtener_id_camion(camion)

        if not id_camion:
            return False

        self.camion = camion
        self.Camion_id_camion = id_camion
        return True

    def asociar_chofer(self, chofer):
        id_chofer = self.obtener_id_usuario(chofer)

        if not id_chofer:
            return False

        self.chofer = chofer
        self.Chofer_Usuario_idUsuario = id_chofer
        return True

    def tiene_camion_asociado(self):
        return (
            self.camion is not None
            or self.Camion_id_camion is not None
            and str(self.Camion_id_camion).strip() != ""
        )

    def tiene_chofer_asociado(self):
        return (
            self.chofer is not None
            or self.Chofer_Usuario_idUsuario is not None
            and str(self.Chofer_Usuario_idUsuario).strip() != ""
        )

    def tiene_mecanico_asignado(self):
        return (
            self.mecanico is not None
            or self.Mecanico_Usuario_idUsuario is not None
            and str(self.Mecanico_Usuario_idUsuario).strip() != ""
        )

    def pertenece_a_chofer(self, chofer):
        id_chofer = self.obtener_id_usuario(chofer) or chofer

        return str(self.Chofer_Usuario_idUsuario) == str(id_chofer)

    def pertenece_a_mecanico(self, mecanico):
        id_mecanico = self.obtener_id_usuario(mecanico) or mecanico

        return str(self.Mecanico_Usuario_idUsuario) == str(id_mecanico)

    def pertenece_a_camion(self, camion):
        id_camion = self.obtener_id_camion(camion) or camion

        return str(self.Camion_id_camion) == str(id_camion)

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

        if not self.tiene_camion_asociado():
            return False

        if not self.tiene_chofer_asociado():
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
    def asignar_mecanico(self, mecanico):
        id_mecanico = self.obtener_id_usuario(mecanico) or mecanico

        if not id_mecanico:
            return False

        if self.obtener_id_usuario(mecanico):
            self.mecanico = mecanico

        self.Mecanico_Usuario_idUsuario = id_mecanico
        self.estado = self.ESTADO_EN_REVISION
        return True

    # valida si un mecanico puede resolver este reporte
    def puede_ser_resuelto_por(self, mecanico, nota_reparacion):
        id_mecanico = self.obtener_id_usuario(mecanico) or mecanico

        return (
            str(self.Mecanico_Usuario_idUsuario) == str(id_mecanico)
            and self.estado != self.ESTADO_RESUELTO
            and nota_reparacion is not None
            and nota_reparacion.strip() != ""
        )

    # resuelve el reporte guardando nota y fecha de resolucion
    def resolver_por_mecanico(self, mecanico, nota_reparacion):
        if not self.puede_ser_resuelto_por(mecanico, nota_reparacion):
            return False

        if self.obtener_id_usuario(mecanico):
            self.mecanico = mecanico

        self.estado = self.ESTADO_RESUELTO
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