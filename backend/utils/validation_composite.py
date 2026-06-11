class Validacion:

    def validar(self, datos):
        raise NotImplementedError("La validacion debe implementar validar()")


class ValidadorCompuesto(Validacion):

    def __init__(self, validaciones=None):
        self.validaciones = validaciones or []

    def agregar(self, validacion):
        self.validaciones.append(validacion)
        return self

    def validar(self, datos):
        for validacion in self.validaciones:
            valido, mensaje_error = validacion.validar(datos)

            if not valido:
                return False, mensaje_error

        return True, None


class CampoObligatorio(Validacion):

    def __init__(self, campo, mensaje_error=None):
        self.campo = campo
        self.mensaje_error = mensaje_error or f"Falta el campo {campo}"

    @staticmethod
    def texto_valido(valor):
        return valor is not None and str(valor).strip() != ""

    def validar(self, datos):
        if self.campo not in datos:
            return False, self.mensaje_error

        if not self.texto_valido(datos[self.campo]):
            return False, self.mensaje_error

        return True, None


class ValorPermitido(Validacion):

    def __init__(self, campo, valores_permitidos, nombre_campo=None):
        self.campo = campo
        self.valores_permitidos = valores_permitidos
        self.nombre_campo = nombre_campo or campo

    def validar(self, datos):
        if datos.get(self.campo) not in self.valores_permitidos:
            return False, f"{self.nombre_campo} no valido"

        return True, None


class ValidacionFuncion(Validacion):

    def __init__(self, campo, funcion_validacion):
        self.campo = campo
        self.funcion_validacion = funcion_validacion

    def validar(self, datos):
        return self.funcion_validacion(datos.get(self.campo))


class ValidacionDatos(Validacion):

    def __init__(self, funcion_validacion):
        self.funcion_validacion = funcion_validacion

    def validar(self, datos):
        return self.funcion_validacion(datos)


class ValidacionCondicional(Validacion):

    def __init__(self, condicion, validacion):
        self.condicion = condicion
        self.validacion = validacion

    def validar(self, datos):
        if not self.condicion(datos):
            return True, None

        return self.validacion.validar(datos)
