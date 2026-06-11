from datetime import date, datetime

from src.Usuario import Usuario
from utils.domain_helpers import formatear_fecha, texto_valido


class Viaje:
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ACEPTADO = "aceptado"
    ESTADO_EN_CURSO = "en curso"
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
        id_operador,
        id_chofer,
        id_camion,
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
        self.id_operador = id_operador
        self.id_chofer = id_chofer
        self.id_camion = id_camion
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

    @classmethod
    def crear_desde_datos(
        cls,
        datos,
        id_viaje=None,
        operador=None,
        chofer=None,
        camion=None,
    ):
        viaje = cls(
            id_viaje=id_viaje,
            fecha_salida=datos.get("fecha_salida"),
            fecha_llegada=datos.get("fecha_llegada"),
            origen=datos.get("origen"),
            destino=datos.get("destino"),
            estado=datos.get("estado", cls.ESTADO_PENDIENTE),
            observaciones=datos.get("observaciones"),
            recorrido=datos.get("recorrido", 0),
            id_operador=datos.get("id_operador"),
            id_chofer=datos.get("id_chofer"),
            id_camion=datos.get("id_camion"),
        )

        if operador is not None:
            if viaje.tiene_operador_asignado():
                viaje.operador = operador
            else:
                operador.gestionar_viaje(viaje)

        if chofer is not None:
            if viaje.tiene_chofer_asignado():
                viaje.chofer = chofer
            else:
                chofer.asignar_viaje(viaje)

        if camion is not None:
            if viaje.tiene_camion_asignado():
                viaje.camion = camion
            else:
                viaje.asignar_camion(camion)

        return viaje

    def asignar_operador(self, operador):
        id_operador = self.obtener_id_usuario(operador)

        if not id_operador:
            return False

        self.operador = operador
        self.id_operador = id_operador
        return True

    def asignar_chofer(self, chofer):
        id_chofer = self.obtener_id_usuario(chofer)

        if not id_chofer:
            return False

        self.chofer = chofer
        self.id_chofer = id_chofer
        return True

    def asignar_camion(self, camion):
        id_camion = self.obtener_id_camion(camion)

        if not id_camion:
            return False

        self.camion = camion
        self.id_camion = id_camion
        return True

    def tiene_operador_asignado(self):
        return (
            self.operador is not None
            or texto_valido(self.id_operador)
        )

    def tiene_chofer_asignado(self):
        return (
            self.chofer is not None
            or texto_valido(self.id_chofer)
        )

    def tiene_camion_asignado(self):
        return (
            self.camion is not None
            or texto_valido(self.id_camion)
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
    def numero_no_negativo(valor):
        try:
            return float(valor) >= 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def normalizar_estado(estado):
        if estado is None:
            return None

        estado_limpio = str(estado).strip().lower()

        if estado_limpio == "en-curso":
            return Viaje.ESTADO_EN_CURSO

        return estado_limpio

    def validar_datos(self):
        if self.convertir_fecha(self.fecha_salida) is None:
            return False
        if not texto_valido(self.origen):
            return False
        if not texto_valido(self.destino):
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

        self.estado = self.normalizar_estado(self.estado)

        return self.estado in self.ESTADOS_VALIDOS

    def pertenece_a_chofer(self, chofer):
        id_chofer = self.obtener_id_usuario(chofer) or chofer

        return str(self.id_chofer) == str(id_chofer)

    def pertenece_a_operador(self, operador):
        id_operador = self.obtener_id_usuario(operador) or operador

        return str(self.id_operador) == str(id_operador)

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
            "fecha_salida": formatear_fecha(self.fecha_salida),
            "fecha_llegada": formatear_fecha(self.fecha_llegada),
            "origen": self.origen,
            "destino": self.destino,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "recorrido": self.recorrido,
            "id_operador": self.id_operador,
            "id_chofer": self.id_chofer,
            "id_camion": self.id_camion,
        }
