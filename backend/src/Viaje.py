from datetime import date, datetime

from src.Usuario import Usuario


class Viaje:
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ACEPTADO = "aceptado"
    ESTADO_EN_CURSO = "en curso"
    ESTADO_EN_CURSO_ALTERNATIVO = "en-curso"
    ESTADO_FINALIZADO = "finalizado"
    ESTADO_CANCELADO = "cancelado"

    ESTADOS_VALIDOS = [
        ESTADO_PENDIENTE,
        ESTADO_ACEPTADO,
        ESTADO_EN_CURSO,
        ESTADO_FINALIZADO,
        ESTADO_CANCELADO,
    ]
    ESTADOS_EN_CURSO = [
        ESTADO_EN_CURSO,
        ESTADO_EN_CURSO_ALTERNATIVO,
    ]

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
        Camion_id_camion,
        operador=None,
        chofer=None,
        camion=None,
        cargas=None,
        registros=None,
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
        self.operador = operador
        self.chofer = chofer
        self.camion = camion
        self.cargas = cargas or []
        self.registros = registros or []

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

    def asignar_operador(self, operador):
        id_operador = self.obtener_id_usuario(operador)

        if not id_operador:
            return False

        self.operador = operador
        self.OperadorLogistico_Usuario_idUsuario = id_operador
        return True

    def asignar_chofer(self, chofer):
        id_chofer = self.obtener_id_usuario(chofer)

        if not id_chofer:
            return False

        self.chofer = chofer
        self.Chofer_Usuario_idUsuario = id_chofer
        return True

    def asignar_camion(self, camion):
        id_camion = self.obtener_id_camion(camion)

        if not id_camion:
            return False

        self.camion = camion
        self.Camion_id_camion = id_camion
        return True

    def tiene_operador_asignado(self):
        return (
            self.operador is not None
            or self.texto_valido(self.OperadorLogistico_Usuario_idUsuario)
        )

    def tiene_chofer_asignado(self):
        return (
            self.chofer is not None
            or self.texto_valido(self.Chofer_Usuario_idUsuario)
        )

    def tiene_camion_asignado(self):
        return (
            self.camion is not None
            or self.texto_valido(self.Camion_id_camion)
        )

    def agregar_carga(self, carga):
        if carga is None:
            return False

        if not carga.asociar_viaje(self):
            return False

        self.cargas.append(carga)
        return True

    def agregar_registro(self, registro):
        if registro is None:
            return False

        if not registro.asociar_viaje(self):
            return False

        self.registros.append(registro)
        return True

    @staticmethod
    def convertir_fecha(fecha):
        if fecha is None or fecha == "":
            return None

        if isinstance(fecha, date):
            return fecha

        fecha_texto = str(fecha).strip()

        try:
            return datetime.strptime(fecha_texto[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def formatear_fecha(fecha):
        if fecha is None:
            return None
        if hasattr(fecha, "isoformat"):
            return fecha.isoformat()
        return fecha

    @staticmethod
    def texto_valido(valor):
        return valor is not None and str(valor).strip() != ""

    @staticmethod
    def numero_no_negativo(valor):
        try:
            return float(valor) >= 0
        except (TypeError, ValueError):
            return False

    def validar_datos(self):
        if self.convertir_fecha(self.fecha_salida) is None:
            return False
        if not self.texto_valido(self.origen):
            return False
        if not self.texto_valido(self.destino):
            return False
        if not self.validar_estado():
            return False
        if not self.numero_no_negativo(self.recorrido):
            return False
        if not self.tiene_operador_asignado():
            return False
        if not self.tiene_chofer_asignado():
            return False
        if not self.tiene_camion_asignado():
            return False
        return True

    def validar_estado(self):
        if not self.estado:
            return False
        return str(self.estado).strip().lower() in self.ESTADOS_VALIDOS

    def normalizar_datos(self):
        self.fecha_salida = self.convertir_fecha(self.fecha_salida)
        self.fecha_llegada = self.convertir_fecha(self.fecha_llegada)
        self.origen = str(self.origen).strip()
        self.destino = str(self.destino).strip()
        self.estado = str(self.estado).strip().lower()
        self.recorrido = float(self.recorrido)

        if self.observaciones is not None:
            self.observaciones = str(self.observaciones).strip()

    def pertenece_a_chofer(self, chofer):
        id_chofer = self.obtener_id_usuario(chofer) or chofer

        return str(self.Chofer_Usuario_idUsuario) == str(id_chofer)

    def pertenece_a_operador(self, operador):
        id_operador = self.obtener_id_usuario(operador) or operador

        return str(self.OperadorLogistico_Usuario_idUsuario) == str(id_operador)

    def puede_ser_visto_por(self, rol, id_usuario):
        if rol == Usuario.ROL_ADMIN:
            return True
        if rol == Usuario.ROL_CHOFER:
            return self.pertenece_a_chofer(id_usuario)
        if rol == Usuario.ROL_OPERADOR:
            return self.pertenece_a_operador(id_usuario)
        return False

    def se_puede_cancelar(self):
        if not self.estado:
            return False

        estados_no_cancelables = [
            self.ESTADO_CANCELADO,
            self.ESTADO_FINALIZADO,
        ]

        if str(self.estado).strip().lower() in estados_no_cancelables:
            return False

        return True

    def cancelar(self, motivo):
        if not motivo or motivo.strip() == "":
            return False

        if not self.se_puede_cancelar():
            return False

        self.estado = self.ESTADO_CANCELADO
        self.observaciones = f"Cancelado por admin. Motivo: {motivo.strip()}"

        return True

    def to_dict(self):
        return {
            "id_viaje": self.id_viaje,
            "fecha_salida": self.formatear_fecha(self.fecha_salida),
            "fecha_llegada": self.formatear_fecha(self.fecha_llegada),
            "origen": self.origen,
            "destino": self.destino,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "recorrido": self.recorrido,
            "OperadorLogistico_Usuario_idUsuario": self.OperadorLogistico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "Camion_id_camion": self.Camion_id_camion
        }