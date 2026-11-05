from models.camion_model import CamionModel
from models.reporte_model import ReporteModel
from models.viaje_model import ViajeModel
from src.Camion import Camion
from src.ReporteFalla import ReporteFalla
from src.Viaje import Viaje


def marcar_camion_tras_reporte(id_camion):
    camion = CamionModel.query.filter_by(id_camion=id_camion).populate_existing().with_for_update().first()
    if camion is None or camion.estado == Camion.ESTADO_INACTIVO:
        return False
    # Reportar o asignar una reparación no equivale a registrar el regreso.
    en_curso = ViajeModel.query.filter_by(
        Camion_id_camion=id_camion, estado=Viaje.ESTADO_EN_CURSO
    ).first()
    if en_curso is not None:
        return False
    camion.estado = Camion.ESTADO_EN_MANTENIMIENTO
    return True


def actualizar_camion_tras_cierre_reporte(id_camion, id_reporte):
    camion = CamionModel.query.filter_by(id_camion=id_camion).populate_existing().with_for_update().first()
    if camion is None or camion.estado != Camion.ESTADO_EN_MANTENIMIENTO:
        return False
    otro_reporte = ReporteModel.query.filter(
        ReporteModel.Camion_id_camion == id_camion,
        ReporteModel.id_reporte != id_reporte,
        ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
    ).first()
    if otro_reporte is not None:
        return False
    viaje_activo = ViajeModel.query.filter(
        ViajeModel.Camion_id_camion == id_camion,
        ViajeModel.estado.in_((Viaje.ESTADO_PENDIENTE, Viaje.ESTADO_ACEPTADO, Viaje.ESTADO_EN_CURSO)),
    ).first()
    camion.estado = Camion.ESTADO_EN_VIAJE if viaje_activo else Camion.ESTADO_DISPONIBLE
    return True


def actualizar_camion_tras_cancelacion(viaje_model):
    camion = CamionModel.query.get(viaje_model.Camion_id_camion)
    if camion is None or camion.estado != Camion.ESTADO_EN_VIAJE:
        return

    otro_viaje_activo = ViajeModel.query.filter(
        ViajeModel.Camion_id_camion == camion.id_camion,
        ViajeModel.id_viaje != viaje_model.id_viaje,
        ViajeModel.estado.in_((
            Viaje.ESTADO_PENDIENTE,
            Viaje.ESTADO_ACEPTADO,
            Viaje.ESTADO_EN_CURSO,
        )),
    ).first()
    if otro_viaje_activo is not None:
        return

    reporte_activo = ReporteModel.query.filter(
        ReporteModel.Camion_id_camion == camion.id_camion,
        ReporteModel.estado.in_(ReporteFalla.ESTADOS_ACTIVOS),
    ).first()
    camion.estado = (
        Camion.ESTADO_EN_MANTENIMIENTO
        if reporte_activo is not None
        else Camion.ESTADO_DISPONIBLE
    )
