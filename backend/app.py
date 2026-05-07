from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"mensaje": "Backend de Trukly funcionando"})

@app.route("/api/test")
def test():
    return jsonify({"mensaje": "Conexión frontend-backend OK"})

if __name__ == "__main__":
    app.run(debug=True)