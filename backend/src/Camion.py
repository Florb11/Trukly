import math


class Camion:
    ESTADO_DISPONIBLE = "disponible"
    ESTADO_EN_VIAJE = "en viaje"
    ESTADO_EN_MANTENIMIENTO = "en mantenimiento"
    ESTADO_INACTIVO = "inactivo"

    ESTADOS_VALIDOS = [
        ESTADO_DISPONIBLE,
        ESTADO_EN_VIAJE,
        ESTADO_EN_MANTENIMIENTO,
        ESTADO_INACTIVO,
    ]

    def __init__(
        self,
        id_camion,
        matricula,
        marca,
        modelo,
        capacidad_carga,
        estado,
        nroTanque,
        viajes_asignados=None,
        reportes_falla=None,
    ):
        self.id_camion = id_camion
        self.matricula = self.normalizar_matricula(matricula)
        self.marca = marca
        self.modelo = modelo
        self.capacidad_carga = capacidad_carga
        self.estado = estado
        self.nroTanque = nroTanque
        self.viajes_asignados = viajes_asignados or []
        self.reportes_falla = reportes_falla or []

    @classmethod
    def crear_desde_datos(cls, datos, id_camion=None):
        # crea un camion desde un diccionario
        if datos is None:
            return None

        camion = cls(
            id_camion=id_camion or datos.get("id_camion"),
            matricula=datos.get("matricula"),
            marca=datos.get("marca"),
            modelo=datos.get("modelo"),
            capacidad_carga=datos.get("capacidad_carga"),
            estado=datos.get("estado"),
            nroTanque=datos.get("nroTanque"),
        )

        if not camion.validar_datos():
            return None

        if not camion.validar_estado():
            return None

        return camion

    @staticmethod
    def normalizar_matricula(valor):
        if valor is None:
            return None
        return "".join(str(valor).upper().split()).replace("-", "")

    @staticmethod
    def convertir_capacidad(valor):
        if valor is None or isinstance(valor, bool):
            return None
        try:
            capacidad = float(valor)
        except (TypeError, ValueError, OverflowError):
            return None
        return capacidad if math.isfinite(capacidad) and capacidad > 0 else None

    @staticmethod
    def convertir_numero_tanque(valor):
        if isinstance(valor, bool):
            return None
        if isinstance(valor, str):
            texto = valor.strip()
            if not texto.isascii() or not texto.isdigit() or len(texto) > 10:
                return None
            valor = int(texto)
        elif isinstance(valor, float):
            if not math.isfinite(valor) or not valor.is_integer():
                return None
            valor = int(valor)
        if not isinstance(valor, int) or not 1 <= valor <= 2147483647:
            return None
        return valor

    @staticmethod
    def validar_datos_camion(datos):
        # valida datos antes de crear o modificar
        if datos is None:
            return False, "Faltan datos del camion"

        matricula = Camion.normalizar_matricula(datos.get("matricula"))
        marca = datos.get("marca")
        modelo = datos.get("modelo")
        capacidad_carga = datos.get("capacidad_carga")
        estado = datos.get("estado")
        nro_tanque = datos.get("nroTanque")

        if not Camion._texto_valido(matricula):
            return False, "La matricula es obligatoria"

        if not Camion._texto_valido(marca):
            return False, "La marca es obligatoria"

        if not Camion._texto_valido(modelo):
            return False, "El modelo es obligatorio"

        for campo, etiqueta, limite in [("matricula", "matrícula", 15), ("marca", "marca", 20), ("modelo", "modelo", 20)]:
            valor = matricula if campo == "matricula" else datos[campo]
            if len(str(valor).strip()) > limite:
                return False, f"El campo {etiqueta} admite hasta {limite} caracteres"

        if capacidad_carga is None:
            return False, "La capacidad de carga es obligatoria"

        if Camion.convertir_capacidad(capacidad_carga) is None:
            return False, "La capacidad de carga debe ser un número finito mayor a 0"

        if not Camion._texto_valido(estado):
            return False, "El estado es obligatorio"

        if estado not in Camion.ESTADOS_VALIDOS:
            return False, "Estado invalido"

        if nro_tanque is None:
            return False, "El numero de tanque es obligatorio"

        if Camion.convertir_numero_tanque(nro_tanque) is None:
            return False, "El número de tanque debe ser un entero entre 1 y 2147483647"

        return True, None

    @staticmethod
    def _texto_valido(texto):
        # valida texto no vacio
        return texto is not None and str(texto).strip() != ""

    def asignar_viaje(self, viaje):
        # asigna un viaje solo si el camion esta disponible
        if viaje is None:
            return False

        if not self.esta_disponible():
            return False

        if not viaje.asignar_camion(self):
            return False

        self.viajes_asignados.append(viaje)
        self.cambiar_estado(self.ESTADO_EN_VIAJE)
        return True

    def registrar_reporte(self, reporte):
        # asocia un reporte de falla al camion
        if reporte is None:
            return False

        if not reporte.asociar_camion(self):
            return False

        self.reportes_falla.append(reporte)
        return True

    def validar_datos(self):
        # valida los datos internos del camion
        datos_validos, _ = Camion.validar_datos_camion(
            {
                "matricula": self.matricula,
                "marca": self.marca,
                "modelo": self.modelo,
                "capacidad_carga": self.capacidad_carga,
                "estado": self.estado,
                "nroTanque": self.nroTanque,
            }
        )

        return datos_validos

    def validar_estado(self):
        # valida que el estado exista en la lista permitida
        return self.estado in self.ESTADOS_VALIDOS

    def cambiar_estado(self, nuevo_estado):
        # cambia el estado si es valido
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return False

        self.estado = nuevo_estado
        return True

    def esta_disponible(self):
        # indica si puede usarse para un viaje
        return self.estado == self.ESTADO_DISPONIBLE

    def esta_en_mantenimiento(self):
        # indica si esta en mantenimiento
        return self.estado == self.ESTADO_EN_MANTENIMIENTO

    def marcar_disponible(self):
        # cambia el camion a disponible
        return self.cambiar_estado(self.ESTADO_DISPONIBLE)

    def puede_entrar_en_mantenimiento(self):
        # un camion inactivo no deberia pasar a mantenimiento
        return self.estado != self.ESTADO_INACTIVO

    def marcar_en_mantenimiento(self):
        # cambia a mantenimiento si se puede
        if not self.puede_entrar_en_mantenimiento():
            return False

        return self.cambiar_estado(self.ESTADO_EN_MANTENIMIENTO)

    def puede_liberarse_de_mantenimiento(self, reportes_activos):
        # solo se libera si no tiene reportes activos
        return (
            self.esta_en_mantenimiento()
            and len(reportes_activos) == 0
        )

    def liberar_si_no_tiene_reportes_activos(self, reportes_activos):
        # vuelve a disponible si ya no tiene reportes activos
        if not self.puede_liberarse_de_mantenimiento(reportes_activos):
            return False

        return self.marcar_disponible()

    def ajustar_estado_por_reportes_activos(self, reportes_activos):
        # si tiene reportes activos, se muestra como mantenimiento
        if (
            len(reportes_activos) > 0
            and self.estado == self.ESTADO_DISPONIBLE
        ):
            self.estado = self.ESTADO_EN_MANTENIMIENTO
            return True

        return False

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

