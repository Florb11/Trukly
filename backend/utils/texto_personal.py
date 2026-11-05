from html import unescape


def texto_personal(valor):
    """Decodificar una sola vez los nombres guardados con html.escape."""
    return unescape(valor) if valor is not None else None


def nombre_completo(usuario):
    return f"{texto_personal(usuario.nombre) or ''} {texto_personal(usuario.apellido) or ''}".strip()
