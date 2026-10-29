"""Avisos operativos para administradores; se confirman con la operación original."""
from db_instance import db
from models.usuario_model import UsuarioModel
from models.notificacion_model import NotificacionModel
from models.camion_model import CamionModel
from services.notificacion_service import NotificacionService
from services.horas_viaje_service import tiempo_viaje


class AdminNotificacionService:
    @staticmethod
    def _crear(evento, id_entidad, titulo, mensaje):
        tipo = f"admin_{evento}:{id_entidad}"
        # Serializar por destinatario para evitar duplicados concurrentes en MySQL.
        admins = UsuarioModel.query.filter_by(rol="admin", estado="activo").order_by(UsuarioModel.id_usuario).with_for_update().all()
        for admin in admins:
            existe = NotificacionModel.query.filter_by(Usuario_idUsuario=admin.id_usuario, tipo=tipo).with_for_update().first()
            if existe is None:
                NotificacionService.crear(admin.id_usuario, titulo, mensaje, tipo)

    @staticmethod
    def _nombre_chofer(id_usuario):
        usuario = db.session.get(UsuarioModel, id_usuario)
        return f"{usuario.nombre} {usuario.apellido}" if usuario else "Chofer sin datos"

    @staticmethod
    def nueva_falla(reporte):
        camion = db.session.get(CamionModel, reporte.Camion_id_camion)
        matricula = camion.matricula if camion else "sin matrícula"
        nombre = AdminNotificacionService._nombre_chofer(reporte.Chofer_Usuario_idUsuario)
        AdminNotificacionService._crear("falla", reporte.id_reporte, "Nuevo reporte de falla",
            f"Reporte #{reporte.id_reporte} · {nombre} · Camión {matricula}. {reporte.descripcion}")

    @staticmethod
    def viaje_cancelado(viaje, motivo):
        nombre = AdminNotificacionService._nombre_chofer(viaje.Chofer_Usuario_idUsuario)
        AdminNotificacionService._crear("cancelacion", viaje.id_viaje, "Viaje cancelado",
            f"Viaje #{viaje.id_viaje} · {nombre}. Motivo: {motivo}")

    @staticmethod
    def revisar_controles(viaje):
        db.session.flush()
        db.session.expire(viaje, ["registros_horarios"])
        estado = tiempo_viaje(viaje)["estado"]
        if estado == "inconsistente" or (viaje.estado == "finalizado" and estado != "confirmado"):
            nombre = AdminNotificacionService._nombre_chofer(viaje.Chofer_Usuario_idUsuario)
            AdminNotificacionService._crear("control", viaje.id_viaje, "Revisar controles del viaje",
                f"Viaje #{viaje.id_viaje} · {nombre}. Los controles están incompletos o son inconsistentes; no se pueden confirmar sus horas.")

    @staticmethod
    def enlace(tipo):
        evento, separador, identificador = (tipo or "").partition(":")
        if not separador or not identificador.isdecimal():
            return None
        if evento == "admin_falla":
            return f"/dashboardAdmin/reportes?reporte={identificador}"
        if evento in {"admin_cancelacion", "admin_control"}:
            return f"/dashboardAdmin/viajes?viaje={identificador}"
        return None
