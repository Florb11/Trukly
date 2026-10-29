from decimal import Decimal, InvalidOperation
from db_instance import db
from models.carga_model import CargaModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel

ESTADOS_EDITABLES = {"pendiente", "aceptado"}
MAX_PESO = Decimal("999999999.999")


class ErrorCarga(ValueError):
    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.codigo = codigo


def peso_decimal(valor):
    if isinstance(valor, bool) or valor is None:
        raise ErrorCarga("El peso debe ser un número mayor que cero, expresado en kg")
    try:
        peso = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ErrorCarga("El peso debe ser un número válido en kg")
    if not peso.is_finite() or peso <= 0 or peso > MAX_PESO:
        raise ErrorCarga("El peso debe ser mayor que cero y no superar 999999999.999 kg")
    if peso != peso.quantize(Decimal("0.001")):
        raise ErrorCarga("El peso admite hasta tres decimales en kg")
    return peso


def validar_datos(datos):
    if not isinstance(datos, dict):
        raise ErrorCarga("Los datos de la carga no son válidos")
    resultado = {}
    for campo, limite in [("descripcion", 255), ("tipo", 45)]:
        valor = datos.get(campo)
        if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:
            raise ErrorCarga(f"El campo {campo} es obligatorio y admite hasta {limite} caracteres")
        resultado[campo] = valor.strip()
    resultado["peso"] = peso_decimal(datos.get("peso"))
    bultos = datos.get("bultos")
    if bultos is not None and bultos != "":
        if isinstance(bultos, bool) or not str(bultos).isdigit() or not 1 <= int(bultos) <= 2147483647:
            raise ErrorCarga("La cantidad de bultos debe ser un número entero mayor que cero")
        bultos = int(bultos)
    else:
        bultos = None
    resultado["bultos"] = bultos
    remito = datos.get("remito")
    if remito is not None and (not isinstance(remito, str) or len(remito.strip()) > 80):
        raise ErrorCarga("El remito admite hasta 80 caracteres")
    resultado["remito"] = remito.strip() or None if isinstance(remito, str) else None
    return resultado


def cargas_viaje(id_viaje):
    return CargaModel.query.filter_by(Viaje_id_viaje=id_viaje).order_by(CargaModel.id_carga).all()


def peso_total(id_viaje):
    return sum((Decimal(str(carga.peso)) for carga in cargas_viaje(id_viaje)), Decimal(0))


def resumen(viaje):
    camion = db.session.get(CamionModel, viaje.Camion_id_camion)
    if camion is None:
        raise ErrorCarga("El camión del viaje no está disponible", 409)
    filas = cargas_viaje(viaje.id_viaje)
    total = sum((Decimal(str(carga.peso)) for carga in filas), Decimal(0))
    capacidad = Decimal(str(camion.capacidad_carga))
    return {"id_viaje": viaje.id_viaje, "estado_viaje": viaje.estado,
            "editable": viaje.estado in ESTADOS_EDITABLES,
            "camion": f"{camion.marca} {camion.modelo} ({camion.matricula})",
            "capacidad_kg": float(capacidad), "peso_total_kg": float(total),
            "disponible_kg": float(capacidad - total),
            "cargas": [carga.to_dict() for carga in filas]}


def comprobar_capacidad(id_viaje, camion, nuevo_total=None):
    total = peso_total(id_viaje) if nuevo_total is None else nuevo_total
    if total > Decimal(str(camion.capacidad_carga)):
        raise ErrorCarga("La carga total supera la capacidad del camión. Reducí la carga o elegí otro camión.", 409)


def guardar(viaje, datos, id_carga=None):
    if viaje.estado not in ESTADOS_EDITABLES:
        raise ErrorCarga("Solo se pueden modificar cargas de viajes pendientes o aceptados", 409)
    camion = CamionModel.query.filter_by(id_camion=viaje.Camion_id_camion).populate_existing().with_for_update().one_or_none()
    if camion is None:
        raise ErrorCarga("Camión no encontrado", 404)
    valores = validar_datos(datos)
    carga = None
    if id_carga is not None:
        carga = CargaModel.query.filter_by(id_carga=id_carga, Viaje_id_viaje=viaje.id_viaje).one_or_none()
        if carga is None:
            raise ErrorCarga("Carga no encontrada en este viaje", 404)
    total = peso_total(viaje.id_viaje) - (Decimal(str(carga.peso)) if carga else 0) + valores["peso"]
    comprobar_capacidad(viaje.id_viaje, camion, total)
    if carga is None:
        carga = CargaModel(Viaje_id_viaje=viaje.id_viaje, estado="registrada")
        db.session.add(carga)
    for campo, valor in valores.items():
        setattr(carga, campo, valor)
    db.session.flush()
    return resumen(viaje)


def eliminar(viaje, id_carga):
    if viaje.estado not in ESTADOS_EDITABLES:
        raise ErrorCarga("Solo se pueden quitar cargas antes de iniciar el viaje", 409)
    CamionModel.query.filter_by(id_camion=viaje.Camion_id_camion).populate_existing().with_for_update().one_or_none()
    carga = CargaModel.query.filter_by(id_carga=id_carga, Viaje_id_viaje=viaje.id_viaje).one_or_none()
    if carga is None:
        raise ErrorCarga("Carga no encontrada en este viaje", 404)
    db.session.delete(carga)
    db.session.flush()
    return resumen(viaje)


def comprobar_reduccion_capacidad(id_camion, nueva_capacidad):
    # Bloquear el camión serializa esta modificación con altas y ediciones de carga.
    camion = CamionModel.query.filter_by(id_camion=id_camion).populate_existing().with_for_update().one()
    limite = Decimal(str(nueva_capacidad))
    viajes = db.session.query(ViajeModel.id_viaje).filter(
        ViajeModel.Camion_id_camion == id_camion,
        ViajeModel.estado.in_(["pendiente", "aceptado", "en curso"]))
    filas = CargaModel.query.filter(CargaModel.Viaje_id_viaje.in_(viajes)).with_for_update().all()
    totales = {}
    for carga in filas:
        totales[carga.Viaje_id_viaje] = totales.get(carga.Viaje_id_viaje, Decimal(0)) + Decimal(str(carga.peso))
    if any(total > limite for total in totales.values()):
        raise ErrorCarga("La nueva capacidad es menor que la carga asignada a un viaje activo", 409)
