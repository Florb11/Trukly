import json
import os
import time

import firebase_admin
from firebase_admin import auth, credentials


class FirebaseConfigError(RuntimeError):
    pass


class FirebaseMigrationConflict(RuntimeError):
    pass


class FirebaseAuthService:
    _inicializado = False

    @staticmethod
    def migrar_usuario_local(usuario, password, token=None):
        """Se llama únicamente después de validar contraseña local y estado activo."""
        if not usuario.email:
            raise FirebaseMigrationConflict("La cuenta necesita un correo para migrar su acceso.")
        existente = FirebaseAuthService.obtener_usuario_por_email(usuario.email)
        if existente is None:
            FirebaseAuthService.inicializar()
            return auth.create_user(
                email=usuario.email, password=password,
                display_name=f"{usuario.nombre} {usuario.apellido}",
                email_verified=False, disabled=False,
            )
        if existente.disabled:
            raise FirebaseMigrationConflict("El acceso de Firebase está desactivado.")
        if usuario.firebase_uid and existente.uid != usuario.firebase_uid:
            raise FirebaseMigrationConflict("El correo no coincide con la cuenta de Firebase vinculada.")
        # Cuenta vacía previamente preparada desde Trukly: configurar su primer acceso.
        if (existente.uid == usuario.firebase_uid and not existente.provider_data
                and not existente.email_verified):
            return auth.update_user(existente.uid, password=password)
        # Nunca sobrescribir la contraseña de una cuenta Firebase ya utilizada.
        if not token:
            raise FirebaseMigrationConflict("Ingresá con tu correo y contraseña de Firebase para vincular la cuenta.")
        identidad = FirebaseAuthService.verificar_token(token, check_revoked=True)
        antiguedad = time.time() - float(identidad.get("auth_time", 0))
        if (identidad.get("uid") != existente.uid or not 0 <= antiguedad <= 300
                or identidad.get("email", "").lower() != usuario.email.lower()):
            raise FirebaseMigrationConflict("No se pudo confirmar la cuenta de Firebase existente.")
        return existente

    @staticmethod
    def inicializar():
        if FirebaseAuthService._inicializado or firebase_admin._apps:
            FirebaseAuthService._inicializado = True
            return

        credenciales_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        credenciales_path = (
            os.getenv("FIREBASE_CREDENTIALS_PATH")
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )

        if credenciales_json:
            credencial = credentials.Certificate(json.loads(credenciales_json))
        elif credenciales_path:
            credencial = credentials.Certificate(credenciales_path)
        else:
            raise FirebaseConfigError(
                "Falta configurar FIREBASE_CREDENTIALS_PATH o "
                "FIREBASE_SERVICE_ACCOUNT_JSON"
            )

        firebase_admin.initialize_app(credencial)
        FirebaseAuthService._inicializado = True

    @staticmethod
    def verificar_token(id_token, check_revoked=False):
        FirebaseAuthService.inicializar()
        return auth.verify_id_token(id_token, check_revoked=check_revoked)

    @staticmethod
    def cambiar_password(uid, password):
        FirebaseAuthService.inicializar()
        return auth.update_user(uid, password=password)

    @staticmethod
    def obtener_usuario_por_email(email):
        FirebaseAuthService.inicializar()

        try:
            return auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            return None

    @staticmethod
    def crear_o_obtener_usuario(email, display_name=None):
        usuario = FirebaseAuthService.obtener_usuario_por_email(email)

        if usuario:
            return usuario

        return auth.create_user(
            email=email,
            display_name=display_name,
            email_verified=False,
            disabled=False,
        )
