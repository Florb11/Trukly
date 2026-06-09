from flask import jsonify, request
from db_instance import db

from models.registro_model import RegistroModel
from models.viaje_model import ViajeModel
from src.RegistroIngresoSalida import RegistroIngresoSalida
from src.Viaje import Viaje


def crear_objeto_viaje(viaje_model):
    if viaje_model is None:
        return None

    return Viaje(
        id_viaje=viaje_model.id_viaje,
        fecha_salida=viaje_model.fecha_salida,
        fecha_llegada=viaje_model.fecha_llegada,
        origen=viaje_model.origen,
        destino=viaje_model.destino,
        estado=viaje_model.estado,
        observaciones=viaje_model.observaciones,
        recorrido=viaje_model.recorrido,
        OperadorLogistico_Usuario_idUsuario=(
            viaje_model.OperadorLogistico_Usuario_idUsuario
        ),
        Chofer_Usuario_idUsuario=viaje_model.Chofer_Usuario_idUsuario,
        Camion_id_camion=viaje_model.Camion_id_camion,
    )


def crear_objeto_registro(registro_model, viaje=None):
    return RegistroIngresoSalida(
        id_registro=registro_model.id_registro,
        fecha_hora=registro_model.fecha_hora,
        tipo_registro=registro_model.tipo_registro,
        observacion=registro_model.observacion,
        Viaje_id_viaje=registro_model.Viaje_id_viaje,
        viaje=viaje,
    )


def listar_registros():
    
    registros = RegistroModel.query.all()

    return jsonify([registro.to_dict() for registro in registros])


def obtener_registro(id_registro):

    registro = RegistroModel.query.get(id_registro)

    if registro is None:
        return jsonify({"mensaje": "Registro no encontrado"}), 404

    return jsonify(registro.to_dict())


def crear_registro():
    datos = request.get_json()
    viaje_model = ViajeModel.query.get(datos["Viaje_id_viaje"])
    viaje = crear_objeto_viaje(viaje_model)

    if viaje is None:
        return jsonify({"mensaje": "Viaje no encontrado"}), 404

    registro = RegistroIngresoSalida(
        id_registro=None,
        fecha_hora=datos["fecha_hora"],
        tipo_registro=datos["tipo_registro"],
        observacion=datos.get("observacion"),
        Viaje_id_viaje=None,
    )

    if not viaje.agregar_registro(registro):
        return jsonify({"mensaje": "No se pudo asociar el registro"}), 400

    if not registro.validar_datos():
        return jsonify({"mensaje": "Faltan datos obligatorios"}), 400

    nuevo_registro = RegistroModel(
        fecha_hora=registro.fecha_hora,
        tipo_registro=registro.tipo_registro,
        observacion=registro.observacion,
        Viaje_id_viaje=registro.Viaje_id_viaje,
    )

    db.session.add(nuevo_registro)
    db.session.commit()

    return jsonify(
        {
            "mensaje": "Registro creado correctamente",
            "registro": nuevo_registro.to_dict(),
        }
    )