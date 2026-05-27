from db_instance import db



class MecanicoModel(db.Model):
    __tablename__ = "Mecanico"

    Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        primary_key=True
    )

    legajo = db.Column(db.String(20), nullable=False)
    especialidad = db.Column(db.String(30), nullable=False)

    def to_dict(self):
        return {
            "Usuario_idUsuario": self.Usuario_idUsuario,
            "Legajo": self.legajo,
            "Especialidad": self.especialidad
        }