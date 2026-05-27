from db_instance import db


class RegistroModel(db.Model):
    __tablename__ = "RegistroIngresoSalida"

    id_registro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    tipo_registro = db.Column(db.String(45), nullable=False)
    observacion = db.Column(db.String(45))
    
    # Clave foránea
    Viaje_id_viaje = db.Column(db.Integer, db.ForeignKey('Viaje.id_viaje'), nullable=False)

    def to_dict(self):
        return {
            "id_registro": self.id_registro,
            "fecha_hora": self.fecha_hora,
            "tipo_registro": self.tipo_registro,
            "observacion": self.observacion,
            "Viaje_id_viaje": self.Viaje_id_viaje
        }