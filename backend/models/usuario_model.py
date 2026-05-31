from db_instance import db


class UsuarioModel(db.Model):
    __tablename__ = "Usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(150), nullable=True, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default="pendiente")
    rol = db.Column(db.String(50), nullable=False, default="chofer")

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "estado": self.estado,
            "rol": self.rol,
        }
