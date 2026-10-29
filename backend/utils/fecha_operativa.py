from datetime import datetime, timedelta, timezone

# Operación en Argentina (UTC-3); no depende de que Railway use UTC.
ZONA_OPERATIVA = timezone(timedelta(hours=-3))


def hoy_operativo(ahora=None):
    return (ahora or datetime.now(timezone.utc)).astimezone(ZONA_OPERATIVA).date()
