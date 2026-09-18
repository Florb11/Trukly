from models.camion_model import CamionModel
from models.reporte_model import ReporteModel
from models.viaje_model import ViajeModel
from src.Camion import Camion
from src.ReporteFalla import ReporteFalla
from src.Viaje import Viaje


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
