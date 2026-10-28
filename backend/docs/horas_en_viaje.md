# Horas en viaje

El servicio `services/horas_viaje_service.py` es la fuente común para estadísticas,
perfil y serialización de viajes. No necesita columnas nuevas ni migración.
Requiere desplegar/reiniciar el backend junto con los frontends web y móvil.

## Reglas

- `ingreso` (o el valor histórico `entrada`) inicia el viaje: salida de la empresa.
- `salida` cierra el viaje: regreso a la empresa.
- Se confirma un viaje finalizado con exactamente un inicio y un regreso posterior,
  sin fechas futuras ni otros controles. Los duplicados se marcan para revisión.
- Un viaje en curso con inicio válido muestra tiempo transcurrido al consultar;
  no se agrega al total confirmado. No hay temporizador que siga sumando al cerrar.
- Los viajes sin controles, incompletos, cancelados o inconsistentes no suman.
- Cada mes recibe la intersección del intervalo confirmado con su rango calendario.
  El historial muestra la duración total y la porción del mes. Por eso el número
  de viajes con horas del mes puede diferir de los viajes con fecha de salida en él.
- Por chofer se fusionan intervalos superpuestos antes de sumar. Se informa el
  tiempo superpuesto; el promedio es el total del período dividido por los viajes
  confirmados que aportan horas a ese período.
- Las incidencias sin intervalo válido se ubican por fecha de salida del viaje.
- Los segundos se conservan para sumar; se muestran horas y minutos truncados.
- El endpoint de escaneo bloquea la fila del viaje durante la transacción y valida
  estado y controles previos para rechazar dobles escaneos. Los tests SQLite
  comprueban reintentos secuenciales; el bloqueo concurrente corresponde a MySQL.

## Fechas

Los controles existentes usan DATETIME sin zona y `datetime.now()` del servidor.
Se conserva esa convención en los límites mensuales y el reloj del cálculo para
no reinterpretar el historial. El servidor debe mantener una zona horaria estable.
Una migración a UTC requiere conocer primero la zona original de esos registros.
Las fechas programadas del viaje no se usan para inventar duración.

## Verificación

Desde backend: `python -m unittest discover -s tests -p test_horas_viaje.py`.
Cubre intervalos, cruces de mes/año, incompletos, duplicados, futuros, cancelados,
superposiciones, persistencia, aislamiento por chofer y el ciclo de doble escaneo.
