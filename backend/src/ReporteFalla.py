from datetime import datetime

from utils.domain_helpers import formatear_fecha, texto_valido


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
        id_camion,
        id_mecanico,
        id_chofer,
        nota_reparacion=None,
        fecha_resolucion=None,
        camion=None,
        mecanico=None,
        chofer=None,
    ):
        self.id_reporte = id_reporte
        self.fecha_hora = fecha_hora
        self.descripcion = descripcion
        self.estado = self.normalizar_estado(estado)
        self.id_camion = id_camion
        self.id_mecanico = id_mecanico
        self.id_chofer = id_chofer
        self.nota_reparacion = nota_reparacion
        self.fecha_resolucion = fecha_resolucion
        self.camion = camion
        self.mecanico = mecanico
        self.chofer = chofer

        self.sincronizar_estado_por_asignacion()

    @classmethod
    def crear_desde_datos(
        cls,
        datos,
        camion=None,
        mecanico=None,
        chofer=None,
    ):
        # crea un reporte de dominio desde un diccionario
        if datos is None:
            return None

        reporte = cls(
            id_reporte=datos.get("id_reporte"),
            fecha_hora=datos.get("fecha_hora") or datetime.now(),
            descripcion=datos.get("descripcion"),
            estado=datos.get("estado") or cls.ESTADO_PENDIENTE,
            id_camion=datos.get("id_camion"),
            id_mecanico=datos.get("id_mecanico"),
            id_chofer=datos.get("id_chofer"),
            nota_reparacion=datos.get("nota_reparacion"),
            fecha_resolucion=datos.get("fecha_resolucion"),
        )

        if camion is not None:
            reporte.asociar_camion(camion)

        if chofer is not None:
            reporte.asociar_chofer(chofer)

        if mecanico is not None:
            reporte.asignar_mecanico(mecanico)

        return reporte

    @staticmethod
    def obtener_id_usuario(usuario):
        # obtiene el id de un usuario de dominio
        if usuario is None:
            return None

        return getattr(usuario, "id_usuario", None)

    @staticmethod
    def obtener_id_camion(camion):
        # obtiene el id de un camion de dominio
        if camion is None:
            return None

        return getattr(camion, "id_camion", None)

    @staticmethod
    def normalizar_estado(estado):
        # normaliza el estado del reporte
        if estado is None:
            return None

        estado_limpio = str(estado).strip().lower()

        if estado_limpio == "en-revision":
            return ReporteFalla.ESTADO_EN_REVISION

        return estado_limpio

    @staticmethod
    def validar_datos_reporte(datos):
        # valida reglas propias del reporte
        if datos is None:
            return False, "Faltan datos del reporte"

        descripcion = datos.get("descripcion")
        estado = datos.get("estado", ReporteFalla.ESTADO_PENDIENTE)

        if not texto_valido(descripcion):
            return False, "La descripcion es obligatoria"

        estado_normalizado = ReporteFalla.normalizar_estado(estado)

        if estado_normalizado not in ReporteFalla.ESTADOS_VALIDOS:
            return False, "Estado invalido"

        return True, None

    def asociar_camion(self, camion):
        # asocia el reporte a un camion
        id_camion = self.obtener_id_camion(camion)

        if not id_camion:
            return False

        self.camion = camion
        self.id_camion = id_camion
        return True

    def asociar_chofer(self, chofer):
        # asocia el reporte a un chofer
        id_chofer = self.obtener_id_usuario(chofer)

        if not id_chofer:
            return False

        self.chofer = chofer
        self.id_chofer = id_chofer
        return True

    def tiene_camion_asociado(self):
        # verifica si tiene camion asociado
        return (
            self.camion is not None
            or texto_valido(self.id_camion)
        )

    def tiene_chofer_asociado(self):
        # verifica si tiene chofer asociado
        return (
            self.chofer is not None
            or texto_valido(self.id_chofer)
        )

    def tiene_mecanico_asignado(self):
        # verifica si tiene mecanico asignado
        return (
            self.mecanico is not None
            or texto_valido(self.id_mecanico)
        )

    def pertenece_a_chofer(self, chofer):
        # verifica si el reporte pertenece al chofer
        id_chofer = self.obtener_id_usuario(chofer) or chofer

        return str(self.id_chofer) == str(id_chofer)

    def pertenece_a_mecanico(self, mecanico):
        # verifica si el reporte pertenece al mecanico
        id_mecanico = self.obtener_id_usuario(mecanico) or mecanico

        return str(self.id_mecanico) == str(id_mecanico)

    def pertenece_a_camion(self, camion):
        # verifica si el reporte pertenece al camion
        id_camion = self.obtener_id_camion(camion) or camion

        return str(self.id_camion) == str(id_camion)

    def validar_datos(self):
        # valida los datos internos del reporte
        datos_validos, _ = ReporteFalla.validar_datos_reporte(
            {
                "descripcion": self.descripcion,
                "estado": self.estado,
            }
        )

        if not datos_validos:
            return False

        if not self.tiene_camion_asociado():
            return False

        if not self.tiene_chofer_asociado():
            return False

        return True

    def validar_estado(self):
        # valida que el estado exista
        self.estado = self.normalizar_estado(self.estado)

        return self.estado in self.ESTADOS_VALIDOS

    def cambiar_estado(self, nuevo_estado):
        # cambia el estado del reporte si es valido
        nuevo_estado = self.normalizar_estado(nuevo_estado)

        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return False

        if (
            nuevo_estado == self.ESTADO_PENDIENTE
            and self.tiene_mecanico_asignado()
        ):
            return False

        self.estado = nuevo_estado
        return True

    def sincronizar_estado_por_asignacion(self):
        # si tiene mecanico, pasa a revision
        if (
            self.estado == self.ESTADO_PENDIENTE
            and self.tiene_mecanico_asignado()
        ):
            self.estado = self.ESTADO_EN_REVISION
            return True

        return False

    def puede_asignar_mecanico(self):
        # solo se asigna si no esta cerrado
        return self.estado not in [
            self.ESTADO_RESUELTO,
            self.ESTADO_CANCELADO,
        ]

    def asignar_mecanico(self, mecanico):
        # asigna un mecanico y pasa el reporte a revision
        if not self.puede_asignar_mecanico():
            return False

        id_mecanico = self.obtener_id_usuario(mecanico) or mecanico

        if not id_mecanico:
            return False

        if self.obtener_id_usuario(mecanico):
            self.mecanico = mecanico

        self.id_mecanico = id_mecanico
        self.estado = self.ESTADO_EN_REVISION
        return True

    def puede_ser_resuelto_por(self, mecanico, nota_reparacion):
        # valida si un mecanico puede resolver el reporte
        id_mecanico = self.obtener_id_usuario(mecanico) or mecanico

        if not id_mecanico:
            return False

        if str(self.id_mecanico) != str(id_mecanico):
            return False

        if self.estado == self.ESTADO_RESUELTO:
            return False

        if nota_reparacion is None:
            return False

        if str(nota_reparacion).strip() == "":
            return False

        return True

    def resolver_por_mecanico(self, mecanico, nota_reparacion):
        # resuelve el reporte con nota y fecha
        if not self.puede_ser_resuelto_por(mecanico, nota_reparacion):
            return False

        if self.obtener_id_usuario(mecanico):
            self.mecanico = mecanico

        self.estado = self.ESTADO_RESUELTO
        self.nota_reparacion = str(nota_reparacion).strip()
        self.fecha_resolucion = datetime.now()

        return True
    

    def to_dict(self):
        # convierte el reporte a diccionario
        return {
            "id_reporte": self.id_reporte,
            "fecha_hora": formatear_fecha(
                self.fecha_hora,
                incluir_hora=True
            ),
            "descripcion": self.descripcion,
            "estado": self.estado,
            "id_camion": self.id_camion,
            "id_mecanico": self.id_mecanico,
            "id_chofer": self.id_chofer,
            "nota_reparacion": self.nota_reparacion,
            "fecha_resolucion": formatear_fecha(
                self.fecha_resolucion,
                incluir_hora=True
            ),
        }
    
  