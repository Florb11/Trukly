import importlib.util
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import create_engine, text

from db_instance import db
from models.usuario_model import UsuarioModel
from routes.auth_routes import auth_routes
from routes.perfil_routes import perfil_routes
from services.credenciales_service import crear_password_interna_firebase
from services.firebase_service import FirebaseAuthService


class MetodosAccesoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest

        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config["JWT_SECRET_KEY"] = "test-only-signing-key-for-login-methods"
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(auth_routes)
        cls.fixture.app.register_blueprint(perfil_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        self.usuario = db.session.get(UsuarioModel, 3)
        self.usuario.estado = "activo"
        self.usuario.email = "perfil@example.invalid"
        self.usuario.firebase_uid = "mecanico-firebase"
        self.usuario.google_autorizado = False
        self.usuario.password = crear_password_interna_firebase()
        db.session.commit()
        self.cliente = self.fixture.app.test_client()
        self.headers = {"Authorization": "Bearer " + create_access_token(identity="3")}
        self.firebase = SimpleNamespace(disabled=False, email=self.usuario.email, email_verified=True, provider_data=[])

    def tearDown(self):
        db.session.rollback()
        db.session.remove()

    def activar_google(self):
        self.usuario.google_autorizado = True
        db.session.commit()

    def configurar_proveedores(self, *nombres, email_google=None):
        self.firebase.provider_data = [
            SimpleNamespace(provider_id=nombre, email=(email_google or self.firebase.email) if nombre == "google.com" else self.firebase.email)
            for nombre in nombres
        ]

    def identidad(self, token, **_):
        return {
            "uid": "mecanico-firebase",
            "email": self.firebase.email,
            "email_verified": True,
            "auth_time": int(time.time()) - (600 if token == "antiguo" else 1),
            "firebase": {"sign_in_provider": "google.com" if token == "google" else "password"},
        }

    def solicitar(self, metodo, ruta, datos=None):
        with patch.object(FirebaseAuthService, "verificar_token", side_effect=self.identidad), patch.object(
            FirebaseAuthService, "obtener_usuario_por_uid", return_value=self.firebase
        ):
            return self.cliente.open(ruta, method=metodo, json=datos, headers=self.headers)

    def ingresar(self, token):
        return self.solicitar("POST", "/api/auth/firebase-login", {"token": token})

    def vincular(self, password="password", google="google"):
        return self.solicitar("POST", "/api/perfil/acceso/google", {
            "firebaseTokenPassword": password, "firebaseTokenGoogle": google,
        })

    def test_google_solo_ingresa_despues_de_autorizarlo_en_el_mismo_perfil(self):
        self.configurar_proveedores("password", "google.com")
        self.assertEqual(self.ingresar("google").status_code, 403)
        self.assertEqual(self.ingresar("password").status_code, 200)
        respuesta = self.vincular()
        self.assertEqual(respuesta.status_code, 200, respuesta.get_json())
        respuesta = self.ingresar("google")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["usuario"]["id_usuario"], 3)

    def test_vinculacion_exige_ambas_confirmaciones_y_el_mismo_correo(self):
        self.configurar_proveedores("password", "google.com")
        self.assertEqual(self.vincular(password="antiguo").status_code, 403)
        self.assertEqual(self.vincular(google="password").status_code, 403)
        self.configurar_proveedores("password", "google.com", email_google="otro@example.invalid")
        self.assertEqual(self.vincular().status_code, 403)
        self.assertFalse(db.session.get(UsuarioModel, 3).google_autorizado)

    def test_google_bloquea_cambios_desde_perfil_y_sincronizacion_al_ingresar(self):
        self.activar_google()
        self.configurar_proveedores("password", "google.com")
        self.firebase.email = "nuevo@example.invalid"
        self.assertEqual(self.solicitar("POST", "/api/perfil/correo/disponibilidad", {
            "email": self.firebase.email,
        }).status_code, 403)
        self.assertEqual(self.solicitar("POST", "/api/perfil/correo/sincronizar", {
            "firebaseToken": "password",
        }).status_code, 403)
        self.assertEqual(self.solicitar("PUT", "/api/perfil/password", {
            "firebaseToken": "password",
        }).status_code, 403)
        for token in ("google", "password"):
            respuesta = self.ingresar(token)
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.get_json()["usuario"]["email"], "perfil@example.invalid")

    def test_puede_configurar_primera_password_en_la_misma_cuenta(self):
        self.activar_google()
        self.configurar_proveedores("google.com")
        ruta = "/api/perfil/acceso/password"
        datos = {"firebaseToken": "google", "password_nueva": "Nueva123", "confirmar_password": "Nueva123"}
        with patch.object(FirebaseAuthService, "cambiar_password") as guardar:
            self.assertEqual(self.solicitar("POST", ruta, {**datos, "firebaseToken": "password"}).status_code, 403)
            guardar.assert_not_called()
            respuesta = self.solicitar("POST", ruta, datos)
            self.assertEqual(respuesta.status_code, 200, respuesta.get_json())
            guardar.assert_called_once_with("mecanico-firebase", "Nueva123")
            self.configurar_proveedores("google.com", "password")
            self.assertEqual(self.solicitar("POST", ruta, datos).status_code, 409)
            self.assertEqual(guardar.call_count, 1)

    def test_desvincular_requiere_password_y_conserva_el_acceso_por_correo(self):
        self.activar_google()
        self.configurar_proveedores("google.com", "password")
        ruta = "/api/perfil/acceso/google"
        with patch.object(FirebaseAuthService, "desvincular_google") as desvincular:
            self.assertEqual(self.solicitar("DELETE", ruta, {"firebaseToken": "google"}).status_code, 403)
            desvincular.assert_not_called()
            respuesta = self.solicitar("DELETE", ruta, {"firebaseToken": "password"})
            self.assertEqual(respuesta.status_code, 200, respuesta.get_json())
            desvincular.assert_called_once_with("mecanico-firebase")
        self.assertEqual(self.ingresar("google").status_code, 403)
        self.assertEqual(self.ingresar("password").get_json()["usuario"]["id_usuario"], 3)
        self.assertEqual(self.solicitar("POST", "/api/perfil/correo/disponibilidad", {
            "email": "nuevo@example.invalid",
        }).status_code, 200)

    def test_si_falla_firebase_puede_completar_la_desvinculacion_al_reintentar(self):
        self.activar_google()
        self.configurar_proveedores("google.com", "password")
        ruta = "/api/perfil/acceso/google"
        with patch.object(FirebaseAuthService, "desvincular_google", side_effect=RuntimeError), patch(
            "controllers.acceso_perfil_controller.logger"
        ):
            self.assertEqual(self.solicitar("DELETE", ruta, {"firebaseToken": "password"}).status_code, 503)
        self.assertEqual(self.ingresar("google").status_code, 403)
        self.assertEqual(self.solicitar("GET", "/api/perfil/acceso").get_json()["acceso"], {
            "google_vinculado": False, "google_en_firebase": True, "tiene_password": True,
        })
        with patch.object(FirebaseAuthService, "desvincular_google") as desvincular:
            self.assertEqual(self.solicitar("DELETE", ruta, {"firebaseToken": "password"}).status_code, 200)
            desvincular.assert_called_once_with("mecanico-firebase")


class MigracionMetodosAccesoTest(unittest.TestCase):
    def test_conserva_vinculos_existentes_y_no_reautoriza_una_cuenta_al_reintentar(self):
        ruta = Path(__file__).resolve().parents[1] / "database/migrations/2026_11_28_metodos_acceso.py"
        spec = importlib.util.spec_from_file_location("migracion_metodos_acceso", ruta)
        migracion = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migracion)
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)

        with engine.begin() as conexion:
            conexion.execute(text("CREATE TABLE Usuario (id_usuario INTEGER, firebase_uid TEXT)"))
            conexion.execute(text("INSERT INTO Usuario VALUES (1, 'google'), (2, 'password'), (3, NULL)"))
        with patch.object(migracion, "vinculos_google", return_value={"google"}):
            migracion.migrar(engine, aplicar=True)
            with engine.begin() as conexion:
                permisos = conexion.execute(text("SELECT google_autorizado FROM Usuario ORDER BY id_usuario")).scalars().all()
                self.assertEqual(permisos, [1, 0, 0])
                conexion.execute(text("UPDATE Usuario SET google_autorizado = 0 WHERE id_usuario = 1"))
            migracion.migrar(engine, aplicar=True)
        with engine.connect() as conexion:
            permisos = conexion.execute(text("SELECT google_autorizado FROM Usuario ORDER BY id_usuario")).scalars().all()
            self.assertEqual(permisos, [0, 0, 0])
