from db import db 


class ReporteModel(db.Model):
    __tablename__ = "ReporteIngresoSalida"

    id_reporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), nullable = False)
#    Claves Foraneas, esto lo voy a revisar despues con postman para ver si funciona
    Camion_id_camion = db.Column(db.Integer, db.ForeignKey('Camion.id_camion'), nullable=False)
    Mecanico_Usuario_idUsuario = db.Column(db.Integer, db.ForeignKey('Mecanico.Usuario_idUsuario'), nullable=False)
    Chofer_Usuario_idUsuario = db.Column(db.Integer, db.ForeignKey('Chofer.Usuario_idUsuario'), nullable=False)
     

    def to_dict(self):
        return {
            "id_reporte": self.id_reporte,
            "fecha_hora": self.fecha_hora,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "Camion_id_camion": self.Camion_id_camion,
            "Mecanico_Usuario_idUsuario": self.Mecanico_Usuario_idUsuario,
            "Chofer_Usuario_idUsuario": self.Chofer_Usuario_idUsuario
        }