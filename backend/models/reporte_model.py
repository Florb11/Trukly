from db_instance import db


class ReporteModel(db.Model):
    __tablename__ = "ReporteFalla"

    id_reporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(45), nullable=False)
    nota_reparacion = db.Column(db.String(255), nullable=True)
    fecha_resolucion = db.Column(db.DateTime, nullable=True)

    Camion_id_camion = db.Column(
        db.Integer,
        db.ForeignKey("Camion.id_camion"),
        nullable=False
    )

    Mecanico_Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Mecanico.Usuario_idUsuario"),
        nullable=True
    )

    Chofer_Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Chofer.Usuario_idUsuario"),
        nullable=False
    )

    def to_dict(self):
        return {
            "id_reporte": self.id_reporte,
            "fecha_hora": self.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            "descripcion": self.descripcion,
            "estado": self.estado,
            "Camion_id_camion": self.Camion_id_camion,
            "Mecanico_Usuario_idUsuario": self.Mecanico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "nota_reparacion": self.nota_reparacion,
            "fecha_resolucion": (
                self.fecha_resolucion.strftime("%Y-%m-%d %H:%M:%S")
                if self.fecha_resolucion
                else None
            ),
        }