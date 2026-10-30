from extensions import bcrypt


def permite_password_local(usuario):
    """Conserva el acceso de administradores locales vinculados posteriormente."""
    if not usuario.firebase_uid:
        return True
    if usuario.rol != "admin":
        return False
    # El vínculo con Firebase no convierte una contraseña interna en credencial.
    try:
        return not bcrypt.check_password_hash(
            usuario.password, f"firebase:{usuario.firebase_uid}"
        )
    except (TypeError, ValueError):
        return False
