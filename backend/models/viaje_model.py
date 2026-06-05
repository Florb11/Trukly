from db_instance import db


class ViajeModel(db.Model):
    __tablename__ = "Viaje"

    id_viaje = db.Column(db.Integer, primary_key=True, autoincrement=True)

    OperadorLogistico_Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("OperadorLogistico.Usuario_idUsuario"),
        nullable=False
    )

    Chofer_Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Chofer.Usuario_idUsuario"),
        nullable=False
    )

    Camion_id_camion = db.Column(
        db.Integer,
        db.ForeignKey("Camion.id_camion"),
        nullable=False
    )

    fecha_salida = db.Column(db.Date, nullable=False)
    fecha_llegada = db.Column(db.Date, nullable=True)

    origen = db.Column(db.String(45), nullable=False)
    destino = db.Column(db.String(45), nullable=False)

    estado = db.Column(db.String(45), nullable=False)
    observaciones = db.Column(db.String(200), nullable=True)

    # En MySQL es DOUBLE, en SQLAlchemy lo usamos como Float
    recorrido = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id_viaje": self.id_viaje,
            "OperadorLogistico_Usuario_idUsuario": self.OperadorLogistico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "Camion_id_camion": self.Camion_id_camion,
            "fecha_salida": self.fecha_salida.isoformat() if self.fecha_salida else None,
            "fecha_llegada": self.fecha_llegada.isoformat() if self.fecha_llegada else None,
            "origen": self.origen,
            "destino": self.destino,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "recorrido": self.recorrido,
        }
