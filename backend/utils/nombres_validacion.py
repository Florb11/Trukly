import unicodedata


def validar_nombres(datos, obligatorios=False):
    if not isinstance(datos, dict):
        return "Los datos personales no son válidos."
    for campo, etiqueta in [("nombre", "El nombre"), ("apellido", "El apellido")]:
        if campo not in datos and not obligatorios:
            continue
        valor = datos.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            return f"{etiqueta} es obligatorio."
        texto = unicodedata.normalize("NFC", valor.strip())
        if len(texto) > 100:
            return f"{etiqueta} admite hasta 100 caracteres."
        if not all(c.isalpha() or c == " " for c in texto):
            return f"{etiqueta} solo admite letras y espacios, incluidas tildes y ñ. No se permiten números ni símbolos."
    return None
