from datetime import date, datetime
from src.Usuario import Usuario


class Chofer(Usuario):
    def __init__(
        self,
        id_usuario,
        username,
        password,
        nombre,
        apellido,
        estado,
        rol,
        licencia,
        vencimientoLicencia,
        legajo,
    ):
        super().__init__(
            id_usuario,
            username,
            password,
            nombre,
            apellido,
            estado,
            rol,
        )

        self.licencia = licencia
        self.vencimientoLicencia = vencimientoLicencia
        self.legajo = legajo

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
            fecha_vencimiento = datetime.strptime(
                vencimientoLicencia,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return False, "La fecha de vencimiento debe tener formato YYYY-MM-DD"

        if fecha_vencimiento < date.today():
            return False, "La licencia no puede estar vencida"

        return True, None

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