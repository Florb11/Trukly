from html import unescape

from db_instance import db


class CamionModel(db.Model):
    __tablename__ = "Camion"
    __table_args__ = (db.UniqueConstraint("nroTanque", name="uq_camion_nro_tanque"),)

    id_camion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matricula = db.Column(db.String(15), nullable=False, unique=True)
    marca = db.Column(db.String(20), nullable=False)
    modelo = db.Column(db.String(20), nullable=False)
    capacidad_carga = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    nroTanque = db.Column(db.Integer, nullable=False)

    @property
    def nombre_visible(self):
        return unescape(f"{self.marca} {self.modelo} ({self.matricula})")

    def to_dict(self):
        return {
            "id_camion": self.id_camion,
            "matricula": self.matricula,
            "marca": self.marca,
            "modelo": self.modelo,
            "capacidad_carga": self.capacidad_carga,
            "estado": self.estado,
            "nroTanque": self.nroTanque,
        }
