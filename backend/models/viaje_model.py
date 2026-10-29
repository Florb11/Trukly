from db_instance import db
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from services.horas_viaje_service import tiempo_viaje


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

    origen = db.Column(db.String(255), nullable=False)
    destino = db.Column(db.String(255), nullable=False)
    origen_lat = db.Column(db.Float, nullable=True)
    origen_lon = db.Column(db.Float, nullable=True)
    destino_lat = db.Column(db.Float, nullable=True)
    destino_lon = db.Column(db.Float, nullable=True)

    estado = db.Column(db.String(45), nullable=False)
    observaciones = db.Column(db.String(200), nullable=True)

    # En MySQL es DOUBLE, en SQLAlchemy lo usamos como Float
    recorrido = db.Column(db.Float, nullable=False)

    registros_horarios = db.relationship(RegistroIngresoSalidaModel, lazy="selectin", viewonly=True)
    camion = db.relationship("CamionModel", lazy="selectin", viewonly=True)
    chofer_usuario = db.relationship(
        "UsuarioModel",
        primaryjoin="ViajeModel.Chofer_Usuario_idUsuario == UsuarioModel.id_usuario",
        foreign_keys=[Chofer_Usuario_idUsuario],
        viewonly=True,
        lazy="selectin",
    )
    operador_usuario = db.relationship(
        "UsuarioModel",
        primaryjoin="ViajeModel.OperadorLogistico_Usuario_idUsuario == UsuarioModel.id_usuario",
        foreign_keys=[OperadorLogistico_Usuario_idUsuario],
        viewonly=True,
        lazy="selectin",
    )

    def to_dict(self):
        return {
            "id_viaje": self.id_viaje,
            "chofer_nombre": (
                f"{self.chofer_usuario.nombre} {self.chofer_usuario.apellido}".strip()
                if self.chofer_usuario else None
            ),
            "operador_nombre": (
                f"{self.operador_usuario.nombre} {self.operador_usuario.apellido}".strip()
                if self.operador_usuario else None
            ),
            "camion_nombre": (
                f"{self.camion.marca} {self.camion.modelo} ({self.camion.matricula})"
                if self.camion else None
            ),
            "tiempo_viaje": tiempo_viaje(self),
            "OperadorLogistico_Usuario_idUsuario": self.OperadorLogistico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "Camion_id_camion": self.Camion_id_camion,
            "fecha_salida": self.fecha_salida.isoformat() if self.fecha_salida else None,
            "fecha_llegada": self.fecha_llegada.isoformat() if self.fecha_llegada else None,
            "origen": self.origen,
            "destino": self.destino,
            "origen_lat": self.origen_lat,
            "origen_lon": self.origen_lon,
            "destino_lat": self.destino_lat,
            "destino_lon": self.destino_lon,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "recorrido": self.recorrido,
        }
