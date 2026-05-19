from db import db


class ChoferModel(db.Model):
    __tablename__ = "Chofer"

    Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        primary_key=True
    )

    licencia = db.Column(db.String(50), nullable=False)
    vencimientoLicencia = db.Column(db.Date, nullable=False)
    legajo = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "Usuario_idUsuario": self.Usuario_idUsuario,
            "licencia": self.licencia,
            "vencimientoLicencia": self.vencimientoLicencia,
            "legajo": self.legajo,
        }