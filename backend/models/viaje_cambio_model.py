from datetime import datetime, timezone
from db_instance import db
from utils.texto_personal import texto_personal


class ViajeCambioModel(db.Model):
    __tablename__ = "ViajeCambio"

    id_cambio = db.Column(db.Integer, primary_key=True)
    id_viaje = db.Column(db.Integer, db.ForeignKey("Viaje.id_viaje"), nullable=False, index=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False)
    actor_nombre = db.Column(db.String(201), nullable=False)
    accion = db.Column(db.String(45), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    datos = db.Column(db.JSON, nullable=False)

    def to_dict(self):
        return {"id_cambio": self.id_cambio, "id_viaje": self.id_viaje,
                "id_usuario": self.id_usuario, "actor_nombre": texto_personal(self.actor_nombre),
                "accion": self.accion, "fecha_hora": self.fecha_hora.isoformat() + "Z",
                "datos": self.datos}
