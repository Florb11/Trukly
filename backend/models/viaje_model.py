from db import db

class ViajeModel(db.Model):
    __tablename__ = "Viaje"

    id_viaje = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_salida = db.Column(db.Date)
    fecha_llegada = db.Column(db.Date)
    origen = db.Column(db.String(45))
    destino = db.Column(db.String(45))
    estado = db.Column(db.String(45))
    observaciones = db.Column(db.String(200))
    #    El double de Mysql se mapea en float aca en sqlalchemy por las dudas
    recorrido = db.Column(db.Float)
#    mas claves foraneas para controlar con postman
    OperadorLogistico_Usuario_idUsuario = db.Column(db.Integer, db.ForeignKey("OperadorLogistico.Usuario_idUsuario"), nullable=False)
    Chofer_Usuario_idUsuario = db.Column(db.Integer, db.ForeignKey("Chofer.Usuario_idUsuario"), nullable=False)
    Camion_id_camion = db.Column(db.Integer, db.ForeignKey("Camion.id_camion"), nullable=False)

    def to_dict(self):
        return {
            "id_viaje": self.id_viaje,
            "OperadorLogistico_Usuario_idUsuario": self.OperadorLogistico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario,
            "Camion_id_camion": self.Camion_id_camion,
            "fecha_salida": self.fecha_salida,
            "fecha_llegada": self.fecha_llegada,
            "origen": self.origen,
            "destino": self.destino,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "recorrido": self.recorrido,
        }
