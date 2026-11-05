from db_instance import db
from models.chofer_model import ChoferModel
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel
from services.notificacion_service import NotificacionService
from utils.fecha_operativa import hoy_operativo


def etapa_aviso(dias):
    for limite in (0, 7, 30, 90):
        if dias <= limite:
            return limite
    return None


def generar_aviso_licencia(id_usuario, hoy=None):
    """Revisar únicamente al chofer que consulta sus notificaciones."""
    hoy = hoy or hoy_operativo()
    try:
        # El bloqueo serializa consultas simultáneas del mismo chofer en MySQL.
        chofer = (ChoferModel.query.join(
            UsuarioModel, UsuarioModel.id_usuario == ChoferModel.Usuario_idUsuario
        ).filter(
            ChoferModel.Usuario_idUsuario == id_usuario,
            UsuarioModel.rol == "chofer", UsuarioModel.estado == "activo",
        ).populate_existing().with_for_update().first())
        if not chofer or not chofer.vencimientoLicencia:
            return 0
        vencimiento = chofer.vencimientoLicencia
        dias = (vencimiento - hoy).days
        etapa = etapa_aviso(dias)
        if etapa is None:
            return 0
        tipo = f"licencia:{vencimiento:%Y%m%d}:{etapa}"
        existe = NotificacionModel.query.filter_by(
            Usuario_idUsuario=id_usuario, tipo=tipo
        ).with_for_update().first()
        if existe:
            return 0
        fecha = vencimiento.strftime("%d/%m/%Y")
        if dias < 0:
            titulo = "Licencia vencida"
            mensaje = f"Tu licencia venció el {fecha}. Renovala y actualizá tus datos en Perfil para poder iniciar viajes."
        elif dias == 0:
            titulo = "Tu licencia vence hoy"
            mensaje = f"Tu licencia vence hoy, {fecha}. Gestioná la renovación y actualizá tus datos en Perfil."
        else:
            titulo = "Tu licencia está por vencer"
            mensaje = f"Tu licencia vence el {fecha}: faltan {dias} días. Gestioná la renovación y actualizá tus datos en Perfil."
        NotificacionService.crear(id_usuario, titulo, mensaje, tipo)
        db.session.commit()
        NotificacionService.enviar_push_pendientes()
        return 1
    except Exception:
        db.session.rollback()
        db.session.info.pop("push_pendientes", None)
        raise
