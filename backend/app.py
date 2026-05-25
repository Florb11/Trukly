import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from extensions import bcrypt, jwt
from db import db
from routes.usuario_routes import usuario_routes
from routes.chofer_routes import chofer_routes
from routes.auth_routes import auth_routes
from routes.administrador_routes import administrador_routes
from routes.operador_routes import operador_routes
from routes.mecanico_routes import mecanico_routes
from routes.camion_routes import camion_routes
from routes.viaje_routes import viaje_routes
from routes.registro_routes import registro_routes
from routes.reporte_routes import reporte_routes

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
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")

# inicializo sqlalchemy con la app de flask
db.init_app(app)
#bcrypt y jwt token
bcrypt.init_app(app)
jwt.init_app(app)

# registro las rutas de usuarios
app.register_blueprint(usuario_routes)
app.register_blueprint(chofer_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(administrador_routes)
app.register_blueprint(operador_routes)
app.register_blueprint(mecanico_routes)
app.register_blueprint(camion_routes)
app.register_blueprint(viaje_routes)
app.register_blueprint(registro_routes)
app.register_blueprint(reporte_routes)


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