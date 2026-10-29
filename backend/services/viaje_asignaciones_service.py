"""Datos públicos mínimos de los participantes de un viaje ya autorizado."""
from db_instance import db
from models.usuario_model import UsuarioModel
from models.camion_model import CamionModel


def obtener_asignaciones(viaje):
    chofer = db.session.get(UsuarioModel, viaje.Chofer_Usuario_idUsuario)
    operador = db.session.get(UsuarioModel, viaje.OperadorLogistico_Usuario_idUsuario)
    camion = db.session.get(CamionModel, viaje.Camion_id_camion)
    return {
        "chofer_nombre": f"{chofer.nombre} {chofer.apellido}".strip() if chofer else None,
        "operador_nombre": f"{operador.nombre} {operador.apellido}".strip() if operador else None,
        "camion_nombre": f"{camion.marca} {camion.modelo} ({camion.matricula})" if camion else None,
    }
