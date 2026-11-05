def convertir_ids_asignacion(cuerpo, campos):
    if not isinstance(cuerpo, dict):
        raise ValueError("Los datos de la asignación no son válidos.")
    resultado = {}
    for campo in campos:
        if campo not in cuerpo:
            continue
        valor = cuerpo[campo]
        texto = str(valor).strip()
        if (isinstance(valor, bool) or not isinstance(valor, (str, int))
                or not texto or len(texto) > 10 or not texto.isascii() or not texto.isdigit()
                or not 0 < int(texto) <= 2147483647):
            raise ValueError("Los identificadores de la asignación deben ser enteros positivos válidos.")
        resultado[campo] = int(texto)
    return resultado
