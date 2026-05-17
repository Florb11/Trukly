import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from db import db
from routes.usuario_routes import usuario_routes
from routes.chofer_routes import chofer_routes
from routes.administrador_routes import administrador_routes

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

# inicializo sqlalchemy con la app de flask
db.init_app(app)

# registro las rutas de usuarios
app.register_blueprint(usuario_routes)
app.register_blueprint(chofer_routes)
app.register_blueprint(administrador_routes)

@app.route("/")
def home():
    # ruta simple para probar que el backend esta funcionando
    return jsonify({"mensaje": "Backend de Trukly funcionando"})


@app.route("/api/test")
def test():
    # ruta simple para probar la conexion frontend-backend
    return jsonify({"mensaje": "Conexion frontend-backend OK"})


@app.route("/api/db-test")
def db_test():
    # pruebo si flask puede conectarse con mysql
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"mensaje": "Conexion con MySQL OK"})
    except Exception as error:
        return jsonify({
            "mensaje": "Error al conectar con MySQL",
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)