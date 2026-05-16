from flask import jsonify, request
from db import db
from models.chofer_model import ChoferModel



# funcion para listar todos los choferes guardados en la bd
def listar_choferes():

    choferes = ChoferModel.query.all()

    return jsonify([chofer.to_dict() for chofer in choferes])

def obtener_chofer(id_usuario):
# Busco chofer por id 
    chofer = ChoferModel.query.get(id_usuario)

    if chofer is None:
        return jsonify({"mensaje": "Chofer no encontrado"}), 404
    

    return jsonify(chofer.to_dict())

# funcion para crear choferes

def crear_chofer():

    datos = request.get_json()

    nuevo_chofer = ChoferModel(
        Usuario_idUsuario=datos["Usuario_idUsuario"],
        legajo=datos["legajo"],
        vencimientoLicencia=datos["vencimientoLicencia"],
        licencia=datos["licencia"]
    )

    db.session.add(nuevo_chofer)
    db.session.commit()

# retorna el mensaje , y sino el error en este caso 201
    return jsonify({
        "mensaje": "Chofer creado correctamente",
        "chofer": nuevo_chofer.to_dict()
    }), 201
