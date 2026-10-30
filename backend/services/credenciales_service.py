from extensions import bcrypt
import secrets


def crear_password_interna_firebase():
    return "!firebase!" + bcrypt.generate_password_hash(secrets.token_urlsafe(48)).decode("utf-8")


def permite_password_local(usuario):
    """Conserva el acceso de administradores locales vinculados posteriormente."""
    if not usuario.firebase_uid:
        return True
    if usuario.password.startswith("!firebase!"):
        return False
    if usuario.rol != "admin":
        return False
    # El vínculo con Firebase no convierte una contraseña interna en credencial.
    try:
        return not bcrypt.check_password_hash(
            usuario.password, f"firebase:{usuario.firebase_uid}"
        )
    except (TypeError, ValueError):
        return False
