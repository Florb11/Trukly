from html import escape


class InputSanitizer:

    @staticmethod
    def texto(valor):
        if valor is None:
            return None

        return escape(str(valor).strip(), quote=True)

    @staticmethod
    def email(valor):
        if valor is None:
            return None

        return escape(str(valor).strip().lower(), quote=True)

    @staticmethod
    def password(valor):
        if valor is None:
            return None

        return str(valor)

    @staticmethod
    def entero(valor):
        if valor is None or valor == "":
            return None

        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def decimal(valor):
        if valor is None or valor == "":
            return None

        try:
            return float(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def sanitizar_campos(
        datos,
        campos_texto=None,
        campos_email=None,
        campos_enteros=None,
        campos_decimales=None,
        campos_password=None,
    ):
        datos_limpios = dict(datos)

        for campo in campos_texto or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.texto(
                    datos_limpios.get(campo)
                )

        for campo in campos_email or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.email(
                    datos_limpios.get(campo)
                )

        for campo in campos_enteros or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.entero(
                    datos_limpios.get(campo)
                )

        for campo in campos_decimales or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.decimal(
                    datos_limpios.get(campo)
                )

        for campo in campos_password or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.password(
                    datos_limpios.get(campo)
                )

        return datos_limpios
