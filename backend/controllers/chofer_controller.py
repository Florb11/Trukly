from flask import jsonify, request
from db_instance import db

from models.chofer_model import ChoferModel
from utils.input_sanitizer import InputSanitizer

class ChoferController:

    @staticmethod
    def listar_choferes():
        # funcion para listar todos los choferes guardados en la bd
        choferes = ChoferModel.query.all()
        return jsonify([chofer.to_dict() for chofer in choferes])

    @staticmethod
    def obtener_chofer(id_usuario):
        # Busco chofer por id
        chofer = ChoferModel.query.get(id_usuario)

        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404

        return jsonify(chofer.to_dict())

    @staticmethod
    def crear_chofer():
        # funcion para crear choferes
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=[
                "legajo",
                "vencimientoLicencia",
                "licencia",
            ],
            campos_enteros=["Usuario_idUsuario"],
        )

        nuevo_chofer = ChoferModel(
            Usuario_idUsuario=datos["Usuario_idUsuario"],
            legajo=datos["legajo"],
            vencimientoLicencia=datos["vencimientoLicencia"],
            licencia=datos["licencia"],
        )

        db.session.add(nuevo_chofer)
        db.session.commit()

        # retorna el mensaje , y sino el error en este caso 201
        return jsonify({
            "mensaje": "Chofer creado correctamente", 
            "chofer": nuevo_chofer.to_dict()
        }), 201