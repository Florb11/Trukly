from utils.fecha_operativa import hoy_operativo


def licencia_vigente(chofer, fecha_salida=None):
    fecha_requerida = max(hoy_operativo(), fecha_salida) if fecha_salida else hoy_operativo()
    return bool(
        chofer
        and chofer.licencia
        and chofer.licencia.strip()
        and chofer.vencimientoLicencia
        and chofer.vencimientoLicencia >= fecha_requerida
    )


MENSAJE_LICENCIA = "El chofer no tiene una licencia vigente. Actualizá sus datos antes de asignar o iniciar un viaje."
MENSAJE_LICENCIA_FECHA = "La licencia del chofer debe estar vigente hoy y en la fecha de salida programada. Actualizá la licencia o elegí otro chofer."
