"""Tiempo entre controles; no representa tiempo efectivo de conducción.

Los registros existentes son DATETIME sin zona: se conserva el reloj del servidor
que usa el registro QR. No se reinterpretan fechas históricas como UTC.
"""
from datetime import datetime


def limites_mes(mes):
    if not isinstance(mes, str) or len(mes) != 7:
        raise ValueError("El mes debe tener el formato AAAA-MM")
    try:
        inicio = datetime.strptime(mes, "%Y-%m")
        if inicio.strftime("%Y-%m") != mes:
            raise ValueError()
        fin = datetime(inicio.year + 1, 1, 1) if inicio.month == 12 else datetime(inicio.year, inicio.month + 1, 1)
    except ValueError as error:
        raise ValueError("El mes debe tener el formato AAAA-MM y estar dentro de rango") from error
    return inicio, fin


def formato_duracion(segundos):
    if segundos is None:
        return None
    minutos = int(segundos) // 60
    return f"{minutos // 60} h {minutos % 60:02d} min"


def tiempo_viaje(viaje, ahora=None):
    ahora = ahora or datetime.now()
    registros = list(viaje.registros_horarios)
    tipos = {r.tipo_registro.strip().lower() for r in registros}
    # El esquema histórico registra salida de empresa y entrada al regresar.
    # El QR actual usa ingreso al viaje y salida del viaje. No mezclar esquemas.
    historico = "entrada" in tipos and "ingreso" not in tipos
    tipo_inicio, tipo_fin = ("salida", "entrada") if historico else ("ingreso", "salida")
    inicios = [r.fecha_hora for r in registros if r.tipo_registro.strip().lower() == tipo_inicio]
    finales = [r.fecha_hora for r in registros if r.tipo_registro.strip().lower() == tipo_fin]
    inicio = inicios[0] if len(inicios) == 1 else None
    fin = finales[0] if len(finales) == 1 else None
    estado = "aceptado" if viaje.estado == "aceptado" and not registros else "sin_registro"
    segundos = transcurridos = None
    if registros:
        estado = "incompleto"
        if len(inicios) > 1 or len(finales) > 1 or len(inicios) + len(finales) != len(registros):
            estado = "inconsistente"
        elif (inicio and inicio > ahora) or (fin and fin > ahora) or (inicio and fin and fin <= inicio):
            estado = "inconsistente"
        elif inicio and fin and viaje.estado == "finalizado":
            estado = "confirmado"
            segundos = int((fin - inicio).total_seconds())
        elif inicio and not fin and viaje.estado == "en curso":
            estado = "en_curso"
            transcurridos = int((ahora - inicio).total_seconds())
        elif inicio and fin:
            estado = "inconsistente"
    return {
        "estado": estado,
        "inicio": inicio.isoformat() if inicio else None,
        "regreso": fin.isoformat() if fin else None,
        "segundos_confirmados": segundos,
        "duracion": formato_duracion(segundos),
        "segundos_en_curso": transcurridos,
        "transcurrido": formato_duracion(transcurridos),
    }


def resumen_horas(viajes, mes, ahora=None):
    inicio_mes, fin_mes = limites_mes(mes)
    ahora = ahora or datetime.now()
    intervalos = []
    historial = []
    conteos = {"confirmado": 0, "en_curso": 0, "sin_registro": 0, "incompleto": 0, "inconsistente": 0, "aceptado": 0}
    for viaje in viajes:
        tiempo = tiempo_viaje(viaje, ahora)
        inicio = datetime.fromisoformat(tiempo["inicio"]) if tiempo["inicio"] else None
        fin = datetime.fromisoformat(tiempo["regreso"]) if tiempo["regreso"] else None
        segundos_mes = None
        if tiempo["estado"] == "confirmado":
            desde, hasta = max(inicio, inicio_mes), min(fin, fin_mes)
            if hasta <= desde:
                continue
            intervalos.append((desde, hasta))
            segundos_mes = int((hasta - desde).total_seconds())
        elif tiempo["estado"] == "en_curso":
            if inicio >= fin_mes or ahora < inicio_mes:
                continue
        else:
            # Sin un par válido, ubicar la incidencia por fecha de salida.
            if not inicio_mes.date() <= viaje.fecha_salida < fin_mes.date():
                continue
        conteos[tiempo["estado"]] += 1
        historial.append({"id_viaje": viaje.id_viaje, "origen": viaje.origen, "destino": viaje.destino,
                          **tiempo, "duracion_mes": formato_duracion(segundos_mes)})
    # Un chofer no acumula dos veces el mismo tiempo si hay viajes superpuestos.
    fusionados = []
    for desde, hasta in sorted(intervalos):
        if fusionados and desde < fusionados[-1][1]:
            fusionados[-1] = (fusionados[-1][0], max(hasta, fusionados[-1][1]))
        else:
            fusionados.append((desde, hasta))
    total = sum(int((hasta - desde).total_seconds()) for desde, hasta in fusionados)
    bruto = sum(int((hasta - desde).total_seconds()) for desde, hasta in intervalos)
    promedio = total // conteos["confirmado"] if conteos["confirmado"] else None
    return {"mes": mes, "segundos_confirmados": total, "duracion": formato_duracion(total),
            "promedio": formato_duracion(promedio), "viajes_confirmados": conteos["confirmado"],
            "viajes_en_curso": conteos["en_curso"], "viajes_aceptados": conteos["aceptado"], "viajes_sin_registro": conteos["sin_registro"],
            "viajes_incompletos": conteos["incompleto"], "viajes_inconsistentes": conteos["inconsistente"],
            "segundos_superpuestos": bruto - total,
            "historial": sorted(historial, key=lambda fila: fila["id_viaje"], reverse=True)}


def horas_chofer(id_chofer, mes=None):
    from models.viaje_model import ViajeModel
    mes = mes or datetime.now().strftime("%Y-%m")
    limites_mes(mes)
    viajes = ViajeModel.query.filter_by(Chofer_Usuario_idUsuario=id_chofer).all()
    return resumen_horas(viajes, mes)


def horas_por_chofer(mes):
    from models.viaje_model import ViajeModel
    from models.usuario_model import UsuarioModel
    from models.chofer_model import ChoferModel
    from collections import defaultdict
    limites_mes(mes)
    viajes = defaultdict(list)
    for viaje in ViajeModel.query.all():
        viajes[viaje.Chofer_Usuario_idUsuario].append(viaje)
    usuarios = UsuarioModel.query.join(ChoferModel, ChoferModel.Usuario_idUsuario == UsuarioModel.id_usuario).all()
    filas = []
    for usuario in usuarios:
        resumen = resumen_horas(viajes[usuario.id_usuario], mes)
        filas.append({"id_usuario": usuario.id_usuario, "nombre": usuario.nombre, "apellido": usuario.apellido, **resumen})
    return sorted(filas, key=lambda fila: (-fila["segundos_confirmados"], fila["apellido"], fila["nombre"]))
