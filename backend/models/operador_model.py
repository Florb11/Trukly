from db import db

class OperadorModel(db.Model):
    __tablename__ = "OperadorLogistico"

    Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        primary_key=True
    )

    legajo = db.Column(db.String(45), nullable=False)
    sector = db.Column(db.String(45), nullable=False)

    def to_dict(self):
        return {
             "Usuario_idUsuario": self.Usuario_idUsuario,
             "Legajo": self.legajo,
             "Sector": self.sector
        }
            
        