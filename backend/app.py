import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from db import db
from models.usuario import Usuario

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return jsonify({"mensaje": "Backend de Trukly funcionando"})


@app.route("/api/test")
def test():
    return jsonify({"mensaje": "Conexión frontend-backend OK"})


@app.route("/api/db-test")
def db_test():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"mensaje": "Conexión con MySQL OK"})
    except Exception as error:
        return jsonify({
            "mensaje": "Error al conectar con MySQL",
            "error": str(error)
        }), 500
        
@app.route("/api/usuarios")
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([usuario.to_dict() for usuario in usuarios])        


if __name__ == "__main__":
    app.run(debug=True)