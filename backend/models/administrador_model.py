from db_instance import db



class AdministradorModel(db.Model):
    __tablename__ = "Administrador"

    Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        primary_key=True
    )

    legajo = db.Column(db.String(45), nullable=False)

    def to_dict(self):
        return {
            "Usuario_idUsuario": self.Usuario_idUsuario,
            "legajo": self.legajo
        }