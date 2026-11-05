from utils.texto_personal import nombre_completo
"""Datos públicos mínimos de los participantes de un viaje ya autorizado."""
from db_instance import db
from models.usuario_model import UsuarioModel
from models.camion_model import CamionModel


def obtener_asignaciones(viaje):
    chofer = db.session.get(UsuarioModel, viaje.Chofer_Usuario_idUsuario)
    operador = db.session.get(UsuarioModel, viaje.OperadorLogistico_Usuario_idUsuario)
    camion = db.session.get(CamionModel, viaje.Camion_id_camion)
    return {
        "chofer_nombre": nombre_completo(chofer) if chofer else None,
        "operador_nombre": nombre_completo(operador) if operador else None,
        "camion_nombre": f"{camion.marca} {camion.modelo} ({camion.matricula})" if camion else None,
    }
