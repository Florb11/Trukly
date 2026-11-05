from db_instance import db
from models.usuario_model import UsuarioModel
from models.viaje_cambio_model import ViajeCambioModel


CAMPOS = ("origen", "destino", "fecha_salida", "fecha_llegada", "recorrido", "estado",
          "Chofer_Usuario_idUsuario", "Camion_id_camion", "observaciones",
          "origen_lat", "origen_lon", "destino_lat", "destino_lon")


def snapshot(viaje):
    return {campo: valor.isoformat() if hasattr(valor, "isoformat") else valor
            for campo in CAMPOS for valor in [getattr(viaje, campo)]}


def registrar(viaje, id_usuario, accion, antes=None, detalle=None):
    anterior = antes or {}
    cambios = {campo: {"antes": anterior.get(campo), "despues": valor}
               for campo, valor in snapshot(viaje).items() if anterior.get(campo) != valor}
    usuario = db.session.get(UsuarioModel, id_usuario)
    nombre = f"{usuario.nombre} {usuario.apellido}".strip() if usuario else "Usuario"
    db.session.add(ViajeCambioModel(id_viaje=viaje.id_viaje, id_usuario=id_usuario,
        actor_nombre=nombre, accion=accion, datos={"cambios": cambios, **(detalle or {})}))
