import re
from sqlalchemy import func
from models.usuario_model import UsuarioModel
from services.firebase_service import FirebaseAuthService


class ErrorCorreo(ValueError):
    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.codigo = codigo


def validar_disponibilidad(email, id_usuario):
    if not isinstance(email, str):
        raise ErrorCorreo("Ingresá un correo válido.")
    email = email.strip().lower()
    if len(email) > 150 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ErrorCorreo("Ingresá un correo válido de hasta 150 caracteres.")
    existente = UsuarioModel.query.filter(func.lower(UsuarioModel.email) == email,
                                         UsuarioModel.id_usuario != id_usuario).first()
    if existente:
        raise ErrorCorreo("Ese correo ya está registrado en Trukly.", 409)
    return email


def sincronizar_verificado(usuario, identidad):
    if not usuario.firebase_uid or identidad.get("uid") != usuario.firebase_uid:
        raise ErrorCorreo("La identidad confirmada no corresponde a tu cuenta.", 403)
    email = identidad.get("email")
    if isinstance(email, str) and email.lower() == (usuario.email or "").lower():
        return False
    if identidad.get("email_verified") is not True:
        raise ErrorCorreo("Primero verificá tu correo nuevo desde el enlace recibido.", 403)
    email = validar_disponibilidad(email, usuario.id_usuario)
    # El token debe reflejar el correo vigente, no uno anterior aún almacenado en caché.
    actual = FirebaseAuthService.obtener_usuario_por_uid(usuario.firebase_uid)
    if actual.disabled or not actual.email_verified or (actual.email or "").lower() != email:
        raise ErrorCorreo("Volvé a iniciar sesión con tu correo verificado para actualizarlo.", 403)
    usuario.email = email
    return True
