from db import db


class ChoferModel(db.Model):
    __tablename__ = "Chofer"

    Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        primary_key=True
    )

    licencia = db.Column(db.String(45), nullable = False)
    vencimientoLicencia = db.Column(db.Date, nullable = False)
    legajo = db.Column(db.String(30), nullable = False)

    def to_dict(self):
        return {
            "Usuario_idUsuario": self.Usuario_idUsuario,
            "Licencia": self.licencia,
            "VencimientoLicencia": self.vencimientoLicencia,
            "Legajo": self.legajo
        }