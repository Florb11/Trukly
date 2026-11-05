from utils.fecha_operativa import hoy_operativo


def licencia_vigente(chofer):
    return bool(
        chofer
        and chofer.licencia
        and chofer.licencia.strip()
        and chofer.vencimientoLicencia
        and chofer.vencimientoLicencia >= hoy_operativo()
    )


MENSAJE_LICENCIA = "El chofer no tiene una licencia vigente. Actualizá sus datos antes de asignar o iniciar un viaje."
