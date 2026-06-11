def texto_valido(valor):
    return valor is not None and str(valor).strip() != ""


def formatear_fecha(fecha, incluir_hora=False):
    if fecha is None:
        return None

    if not hasattr(fecha, "strftime"):
        return fecha

    if incluir_hora:
        return fecha.strftime("%Y-%m-%d %H:%M:%S")

    return fecha.isoformat()
