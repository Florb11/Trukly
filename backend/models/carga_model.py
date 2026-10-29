from db_instance import db


class CargaModel(db.Model):
    __tablename__ = "Carga"

    id_carga = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(45), nullable=False)
    peso = db.Column(db.Numeric(12, 3), nullable=False)
    bultos = db.Column(db.Integer, nullable=True)
    remito = db.Column(db.String(80), nullable=True)
    estado = db.Column(db.String(45), nullable=False)

    Viaje_id_viaje = db.Column(
        db.Integer,
        db.ForeignKey("Viaje.id_viaje"),
        nullable=False
    )

    def to_dict(self):
        return {
            "id_carga": self.id_carga,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "peso": float(self.peso),
            "bultos": self.bultos,
            "remito": self.remito,
            "estado": self.estado,
            "Viaje_id_viaje": self.Viaje_id_viaje,
        }