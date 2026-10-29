from db_instance import db


class ReporteModel(db.Model):
    __tablename__ = "ReporteFalla"

    id_reporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(45), nullable=False)
    motivo_cancelacion = db.Column(db.String(255), nullable=True)
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

    camion = db.relationship("CamionModel", lazy="selectin")
    chofer_usuario = db.relationship(
        "UsuarioModel",
        primaryjoin="ReporteModel.Chofer_Usuario_idUsuario == UsuarioModel.id_usuario",
        foreign_keys=[Chofer_Usuario_idUsuario],
        viewonly=True,
        lazy="selectin",
    )
    mecanico_usuario = db.relationship(
        "UsuarioModel",
        primaryjoin="ReporteModel.Mecanico_Usuario_idUsuario == UsuarioModel.id_usuario",
        foreign_keys=[Mecanico_Usuario_idUsuario],
        viewonly=True,
        lazy="selectin",
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
            "motivo_cancelacion": self.motivo_cancelacion,
            "fecha_resolucion": (
                self.fecha_resolucion.strftime("%Y-%m-%d %H:%M:%S")
                if self.fecha_resolucion
                else None
            ),
        }
