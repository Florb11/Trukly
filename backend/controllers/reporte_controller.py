from datetime import datetime

from flask import jsonify, request

from db_instance import db
from models.reporte_model import ReporteModel
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.usuario_model import UsuarioModel
from src.Camion import Camion
from src.Chofer import Chofer
from src.Mecanico import Mecanico
from src.ReporteFalla import ReporteFalla
from src.Usuario import Usuario
from services.auth_service import AuthService
from utils.auth_decorators import obtener_admin_actual_desde_token
from utils.auth_decorators import roles_required


class ReporteController:

    @staticmethod
    def crear_objeto_camion(camion_model):
        if camion_model is None:
            return None

        return Camion(
            id_camion=camion_model.id_camion,
            matricula=camion_model.matricula,
            marca=camion_model.marca,
            modelo=camion_model.modelo,
            capacidad_carga=camion_model.capacidad_carga,
            estado=camion_model.estado,
            nroTanque=camion_model.nroTanque,
        )

    @staticmethod
    def crear_objeto_chofer(usuario_model, chofer_model):
        if usuario_model is None or chofer_model is None:
            return None

        return Chofer(
            id_usuario=usuario_model.id_usuario,
            username=usuario_model.username,
            email=usuario_model.email,
            password=usuario_model.password,
            nombre=usuario_model.nombre,
            apellido=usuario_model.apellido,
            estado=usuario_model.estado,
            rol=usuario_model.rol,
            licencia=chofer_model.licencia,
            vencimientoLicencia=chofer_model.vencimientoLicencia,
            legajo=chofer_model.legajo,
            foto_perfil=usuario_model.foto_perfil,
        )

    @staticmethod
    def crear_objeto_mecanico(usuario_model, mecanico_model):
        if usuario_model is None or mecanico_model is None:
            return None

        return Mecanico(
            id_usuario=usuario_model.id_usuario,
            username=usuario_model.username,
            email=usuario_model.email,
            password=usuario_model.password,
            nombre=usuario_model.nombre,
            apellido=usuario_model.apellido,
            estado=usuario_model.estado,
            rol=usuario_model.rol,
            legajo=mecanico_model.legajo,
            especialidad=mecanico_model.especialidad,
            foto_perfil=usuario_model.foto_perfil,
        )

    @staticmethod
    def obtener_chofer_clase(id_chofer):
        if not id_chofer:
            return None

        usuario = UsuarioModel.query.get(id_chofer)
        chofer = ChoferModel.query.get(id_chofer)

        return ReporteController.crear_objeto_chofer(usuario, chofer)

    @staticmethod
    def obtener_mecanico_clase(id_mecanico):
        if not id_mecanico:
            return None

        usuario = UsuarioModel.query.get(id_mecanico)
        mecanico = MecanicoModel.query.get(id_mecanico)

        return ReporteController.crear_objeto_mecanico(usuario, mecanico)

    @staticmethod
    def obtener_camion_clase(id_camion):
        if not id_camion:
            return None

        camion = CamionModel.query.get(id_camion)

        return ReporteController.crear_objeto_camion(camion)

    @staticmethod
    def crear_objeto_reporte(reporte_model, cargar_relaciones=True):
        camion = None
        mecanico = None
        chofer = None

        if cargar_relaciones:
            camion = ReporteController.obtener_camion_clase(
                reporte_model.Camion_id_camion
            )
            chofer = ReporteController.obtener_chofer_clase(
                reporte_model.Chofer_Usuario_idUsuario
            )

            if reporte_model.Mecanico_Usuario_idUsuario:
                mecanico = ReporteController.obtener_mecanico_clase(
                    reporte_model.Mecanico_Usuario_idUsuario
                )

        return ReporteFalla(
            id_reporte=reporte_model.id_reporte,
            fecha_hora=reporte_model.fecha_hora,
            descripcion=reporte_model.descripcion,
            estado=reporte_model.estado,
            Camion_id_camion=reporte_model.Camion_id_camion,
            Mecanico_Usuario_idUsuario=(
                reporte_model.Mecanico_Usuario_idUsuario
            ),
            Chofer_Usuario_idUsuario=(
                reporte_model.Chofer_Usuario_idUsuario
            ),
            nota_reparacion=reporte_model.nota_reparacion,
            fecha_resolucion=reporte_model.fecha_resolucion,
            camion=camion,
            mecanico=mecanico,
            chofer=chofer,
        )

    @staticmethod
    def actualizar_modelo_reporte(reporte_model, reporte_clase):
        reporte_model.estado = reporte_clase.estado
        reporte_model.Mecanico_Usuario_idUsuario = (
            reporte_clase.Mecanico_Usuario_idUsuario
        )
        reporte_model.nota_reparacion = reporte_clase.nota_reparacion
        reporte_model.fecha_resolucion = reporte_clase.fecha_resolucion

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def listar_reportes():
        reportes = ReporteModel.query.all()

        return jsonify({
            "reportes": [reporte.to_dict() for reporte in reportes]
        }), 200

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
        Usuario.ROL_CHOFER,
    )
    def obtener_reporte(id_reporte):
        reporte = ReporteModel.query.get(id_reporte)

        if reporte is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        rol = AuthService.obtener_rol_actual()
        id_usuario = AuthService.obtener_id_usuario_actual()

        if (
            rol == Usuario.ROL_CHOFER
            and reporte.Chofer_Usuario_idUsuario != id_usuario
        ):
            return jsonify({"mensaje": "No tenes permiso para ver este reporte"}), 403

        return jsonify({
            "reporte": reporte.to_dict()
        }), 200

    @staticmethod
    @roles_required(Usuario.ROL_CHOFER)
    def crear_reporte():
        datos = request.get_json(silent=True) or {}
        id_chofer = AuthService.obtener_id_usuario_actual()

        camion_id = datos.get("Camion_id_camion")
        descripcion = datos.get("descripcion")

        chofer = ReporteController.obtener_chofer_clase(id_chofer)
        camion = ReporteController.obtener_camion_clase(camion_id)

        if camion is None:
            return jsonify({"mensaje": "Camion no encontrado"}), 404

        if chofer is None:
            return jsonify({"mensaje": "Chofer no encontrado"}), 404

        reporte_clase = ReporteFalla(
            None,
            datetime.now(),
            descripcion,
            ReporteFalla.ESTADO_PENDIENTE,
            None,
            None,
            None,
        )

        camion.registrar_reporte(reporte_clase)
        chofer.registrar_reporte(reporte_clase)

        if not reporte_clase.validar_datos():
            return jsonify({"mensaje": "Faltan datos obligatorios"}), 400

        if not reporte_clase.validar_estado():
            return jsonify({"mensaje": "Estado invalido"}), 400

        nuevo_reporte = ReporteModel(
            fecha_hora=reporte_clase.fecha_hora,
            descripcion=reporte_clase.descripcion,
            estado=reporte_clase.estado,
            Camion_id_camion=reporte_clase.Camion_id_camion,
            Mecanico_Usuario_idUsuario=reporte_clase.Mecanico_Usuario_idUsuario,
            Chofer_Usuario_idUsuario=reporte_clase.Chofer_Usuario_idUsuario,
        )

        try:
            db.session.add(nuevo_reporte)
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo crear el reporte"
            }), 500

        return jsonify({
            "mensaje": "Reporte creado correctamente",
            "reporte": nuevo_reporte.to_dict(),
        }), 201

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def cambiar_estado_reporte(id_reporte):
        reporte_db = ReporteModel.query.get(id_reporte)

        if reporte_db is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos = request.get_json(silent=True) or {}
        nuevo_estado = datos.get("estado")

        reporte_clase = ReporteController.crear_objeto_reporte(reporte_db)
        rol = AuthService.obtener_rol_actual()

        if rol == Usuario.ROL_ADMIN:
            admin = obtener_admin_actual_desde_token()
            estado_cambiado = admin.cambiar_estado_reporte(
                reporte_clase,
                nuevo_estado
            ) if admin else False
        else:
            estado_cambiado = reporte_clase.cambiar_estado(nuevo_estado)

        if not estado_cambiado:
            return jsonify({"mensaje": "Estado invalido"}), 400

        ReporteController.actualizar_modelo_reporte(
            reporte_db,
            reporte_clase
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo modificar el estado del reporte"
            }), 500

        return jsonify({
            "mensaje": "Estado del reporte modificado correctamente",
            "reporte": reporte_db.to_dict(),
        }), 200

    @staticmethod
    @roles_required(
        Usuario.ROL_ADMIN,
        Usuario.ROL_OPERADOR,
    )
    def asignar_mecanico(id_reporte):
        reporte_db = ReporteModel.query.get(id_reporte)

        if reporte_db is None:
            return jsonify({"mensaje": "Reporte no encontrado"}), 404

        datos = request.get_json(silent=True) or {}
        id_mecanico = datos.get("Mecanico_Usuario_idUsuario")

        mecanico = ReporteController.obtener_mecanico_clase(id_mecanico)

        if mecanico is None:
            return jsonify({"mensaje": "Mecanico no encontrado"}), 404

        reporte_clase = ReporteController.crear_objeto_reporte(reporte_db)

        if not mecanico.asignar_reporte(reporte_clase):
            return jsonify({"mensaje": "No se pudo asignar el mecanico"}), 400

        ReporteController.actualizar_modelo_reporte(
            reporte_db,
            reporte_clase
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            return jsonify({
                "mensaje": "No se pudo asignar el mecanico"
            }), 500

        return jsonify({
            "mensaje": "Mecanico asignado correctamente",
            "reporte": reporte_db.to_dict(),
        }), 200