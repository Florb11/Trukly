from flask import jsonify, request
from db_instance import db

from models.reporte_model import ReporteModel
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from utils.input_sanitizer import InputSanitizer
from utils.auth_decorators import chofer_required, obtener_chofer_actual_desde_token

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
    
    @staticmethod
    @chofer_required
    def crear_reporte():
        # 1. Recuperamos el chofer actual como objeto POO (gracias al decorador)
        chofer = g.chofer_actual 

        # 2. Sanitizamos los datos de entrada
        datos = InputSanitizer.sanitizar_campos(
            request.get_json(silent=True) or {},
            campos_texto=["descripcion", "gravedad"],
            campos_enteros=["id_camion"]
        )

        id_camion = datos.get("id_camion")
        if not id_camion:
            return jsonify({"mensaje": "El id_camion es obligatorio"}), 400

        # 3. Buscamos el camión en la Base de Datos
        camion_model = CamionModel.query.get(id_camion)
        if not camion_model:
            return jsonify({"mensaje": "Camión no encontrado"}), 404

        # 4. Instanciamos la clase POO del camión para usar nuestra lógica de negocio
        camion = Camion.crear_desde_datos(camion_model.to_dict())

        # Validamos si el camión puede entrar en mantenimiento (ej: no está inactivo)
        if not camion.puede_entrar_en_mantenimiento():
            return jsonify({"mensaje": "El camión no puede reportar fallas en su estado actual"}), 400

        # 5. Intentamos guardar en BD con try/except y logger
        try:
            # Creamos el reporte (nace pendiente y asociado al chofer actual)
            nuevo_reporte = ReporteFallaModel(
                descripcion=datos.get("descripcion"),
                gravedad=datos.get("gravedad"),
                estado="pendiente", 
                Chofer_Usuario_idUsuario=chofer.id_usuario,
                Camion_id_camion=id_camion
            )

            # Usamos la lógica de la clase para cambiar el estado
            camion.marcar_en_mantenimiento()
            
            # Pasamos el nuevo estado de vuelta al modelo de la BD
            camion_model.estado = camion.estado 

            db.session.add(nuevo_reporte)
            db.session.commit()

            return jsonify({
                "mensaje": "Reporte creado exitosamente. El camión pasó a mantenimiento.",
            }), 201

        except Exception:
            db.session.rollback()
            logger.exception(f"Error al crear reporte de falla para el camión {id_camion} por el chofer {chofer.id_usuario}")
            return jsonify({"mensaje": "Error interno del servidor al crear el reporte"}), 500