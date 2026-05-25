from flask import jsonify, request
from db import db
from models.reporte_model import ReporteModel

def listar_reportes():

    reportes = ReporteModel.query.all()

    return jsonify ([reporte.to_dict() for reporte in reportes])

def obtener_reporte(id_reporte):


    reporte = ReporteModel.query.get(id_reporte)

    if reporte is None:
        return jsonify({"mensaje": "Reporte no encontrado"}),404
    
    return jsonify(reporte.to_dict())

def crear_reporte():
    
    datos = request.get_json()

    nuevo_reporte = ReporteModel(
        fecha_hora=datos["fecha_hora"],
        descripcion=datos["descripcion"],
        estado=datos["estado"],
        Camion_id_camion=datos["Camion_id_camion"],
        Mecanico_Usuario_idUsuario=datos["Mecanico_Usuario_idUsuario"],
        Chofer_Usuario_idUsuario=datos["Chofer_Usuario_idUsuario"]
    )

    db.session.add(nuevo_reporte)
    db.session.commit()

    return jsonify({
        "mensaje": "Reporte creado correctamente",
        "reporte": nuevo_reporte.to_dict()
    })