from db_instance import db


class PushDispositivoModel(db.Model):
    __tablename__ = "PushDispositivo"
    id = db.Column(db.Integer, primary_key=True)
    Usuario_idUsuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    token = db.Column(db.Text, nullable=False)
