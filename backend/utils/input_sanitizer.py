from html import escape


class InputSanitizer:

    @staticmethod
    def texto(valor):
        # Si no viene valor, devuelve None
        if valor is None:
            return None

        # Limpia espacios y protege caracteres HTML
        return escape(str(valor).strip(), quote=True)

    @staticmethod
    def email(valor):
        # Si no viene valor, devuelve None
        if valor is None:
            return None

        # Limpia espacios, pasa a minuscula y protege caracteres HTML
        return escape(str(valor).strip().lower(), quote=True)

    @staticmethod
    def password(valor):
        # Si no viene valor, devuelve None
        if valor is None:
            return None

        # No modifica la contrasena para no cambiar lo que escribio el usuario
        return str(valor)

    @staticmethod
    def entero(valor):
        # Si no viene valor o viene vacio, devuelve None
        if valor is None or valor == "":
            return None

        try:
            # Intenta convertir el valor a entero
            return int(valor)

        except (TypeError, ValueError):
            # Si no se puede convertir, devuelve None
            return None

    @staticmethod
    def decimal(valor):
        # Si no viene valor o viene vacio, devuelve None
        if valor is None or valor == "":
            return None

        try:
            # Intenta convertir el valor a decimal
            return float(valor)

        except (TypeError, ValueError):
            # Si no se puede convertir, devuelve None
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
        # Crea una copia para no modificar los datos originales
        datos_limpios = dict(datos)

        # Limpia los campos de texto
        for campo in campos_texto or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.texto(
                    datos_limpios.get(campo)
                )

        # Limpia los campos de email
        for campo in campos_email or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.email(
                    datos_limpios.get(campo)
                )

        # Convierte los campos enteros
        for campo in campos_enteros or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.entero(
                    datos_limpios.get(campo)
                )

        # Convierte los campos decimales
        for campo in campos_decimales or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.decimal(
                    datos_limpios.get(campo)
                )

        # Procesa contrasenas sin limpiar ni modificar el texto
        for campo in campos_password or []:
            if campo in datos_limpios:
                datos_limpios[campo] = InputSanitizer.password(
                    datos_limpios.get(campo)
                )

        # Devuelve los datos preparados para usar
        return datos_limpios
