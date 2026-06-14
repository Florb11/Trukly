from datetime import date, datetime
from src.Usuario import Usuario


class Chofer(Usuario):
    def __init__(
        self,
        id_usuario,
        username,
        email,
        password,
        nombre,
        apellido,
        estado,
        rol,
        licencia,
        vencimientoLicencia,
        legajo,
        foto_perfil=None,
        viajes_asignados=None,
        reportes_creados=None,
    ):
        super().__init__(
            id_usuario,
            username,
            email,
            password,
            nombre,
            apellido,
            estado,
            rol,
            foto_perfil,
        )

        self.licencia = licencia
        self.vencimientoLicencia = vencimientoLicencia
        self.legajo = legajo
        self.viajes_asignados = viajes_asignados or []
        self.reportes_creados = reportes_creados or []

    @classmethod
    def crear_desde_datos(cls, datos):
        if datos is None:
            return None

        return cls(
            id_usuario=datos.get("id_usuario"),
            username=datos.get("username"),
            email=datos.get("email"),
            password=datos.get("password"),
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido"),
            estado=datos.get("estado"),
            rol=datos.get("rol"),
            licencia=datos.get("licencia"),
            vencimientoLicencia=datos.get("vencimientoLicencia"),
            legajo=datos.get("legajo"),
            foto_perfil=datos.get("foto_perfil"),
        )

    def asignar_viaje(self, viaje):
        if viaje is None:
            return False

        if not viaje.asignar_chofer(self):
            return False

        self.viajes_asignados.append(viaje)
        return True

    def registrar_reporte(self, reporte):
        if reporte is None:
            return False

        if not reporte.asociar_chofer(self):
            return False

        self.reportes_creados.append(reporte)
        return True

    def puede_ver_viaje(self, viaje):
        if viaje is None:
            return False

        return viaje.pertenece_a_chofer(self)

    def puede_ver_reporte(self, reporte):
        if reporte is None:
            return False

        return reporte.pertenece_a_chofer(self)

    @staticmethod
    def validar_licencia(licencia):
        if not licencia:
            return False, "La licencia es obligatoria"

        licencia_limpia = licencia.replace("-", "").replace(" ", "")

        if len(licencia_limpia) < 6:
            return False, "La licencia debe tener al menos 6 caracteres"

        if not licencia_limpia.isalnum():
            return False, "La licencia solo puede contener letras, numeros, espacios o guiones"

        return True, None

    @staticmethod
    def validar_vencimiento_licencia(vencimientoLicencia):
        if not vencimientoLicencia:
            return False, "La fecha de vencimiento de la licencia es obligatoria"

        try:
            fecha_vencimiento = Chofer.convertir_vencimiento_licencia(
                vencimientoLicencia
            )
        except ValueError:
            return False, "La fecha de vencimiento debe tener formato YYYY-MM-DD"

        if fecha_vencimiento < date.today():
            return False, "La licencia no puede estar vencida"

        return True, None

    @staticmethod
    def convertir_vencimiento_licencia(vencimientoLicencia):
        if isinstance(vencimientoLicencia, date):
            return vencimientoLicencia

        return datetime.strptime(
            vencimientoLicencia,
            "%Y-%m-%d"
        ).date()

    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "licencia": self.licencia,
                "vencimientoLicencia": self.vencimientoLicencia,
                "legajo": self.legajo,
            }
        )

        return datos_usuario
    
    def obtener_mis_reportes(self, reporte_model_query):
        return reporte_model_query.filter_by(
            Chofer_Usuario_idUsuario=self.id_usuario
        ).all()
    
    def obtener_mis_viajes(self, viaje_model_query):
        return viaje_model_query.filter_by(
            Chofer_Usuario_idUsuario=self.id_usuario
        ).all()