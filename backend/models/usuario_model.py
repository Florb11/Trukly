from db import db


class UsuarioModel(db.Model):
    __tablename__ = "Usuario"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    estado = db.Column(db.String(45), nullable=False)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "estado": self.estado,
        }
