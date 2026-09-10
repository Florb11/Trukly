import json
import os

import firebase_admin
from firebase_admin import auth, credentials


class FirebaseConfigError(RuntimeError):
    pass


class FirebaseAuthService:
    _inicializado = False

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
    def verificar_token(id_token):
        FirebaseAuthService.inicializar()
        return auth.verify_id_token(id_token)
