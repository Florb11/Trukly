from db import db


class CamionModel(db.Model):
    ()
__tablename__ = "Camion"


id_camion = db.Column(db.Integer, primary_key=True, autoincrement=True)
matricula = db.Column(db.String(15), nullable = False, unique = True)
marca = db.Column(db.String(20), nullable = False)
modelo = db.Column(db.String(20), nullable  = False)
capacidad_carga = db.Column(db.Float, nullable = False)
estado = db.Column(db.String(20), nullable = False)
nroTanque = db.Column(db.Integer, nullable = False)

def to_dict(self):
    return {
        "id_camion": self.id_camion,
        "matricula": self.matricula,
        "marca": self.marca,
        "modelo": self.modelo,
        "capacidad_carga": self.capacidad_carga,
        "estado": self.estado,
        "nroTanque": self.nroTanque
    }
