from db_instance import db


class NotificacionModel(db.Model):
    __tablename__ = "Notificacion"

    id_notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)

    Usuario_idUsuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        nullable=False
    )

    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            "id_notificacion": self.id_notificacion,
            "Usuario_idUsuario": self.Usuario_idUsuario,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "leida": self.leida,
            "fecha_hora": self.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": self.tipo,
        }