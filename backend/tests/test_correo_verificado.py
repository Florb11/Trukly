import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token

from routes.perfil_routes import perfil_routes
from routes.auth_routes import auth_routes
from routes.administrador_routes import administrador_routes
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from services.credenciales_service import crear_password_interna_firebase


class CorreoVerificadoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-verified-email-secret-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(perfil_routes)
        cls.fixture.app.register_blueprint(auth_routes)
        cls.fixture.app.register_blueprint(administrador_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        usuario = db.session.get(UsuarioModel, 3)
        usuario.email = 'anterior@example.invalid'
        usuario.firebase_uid = 'uid-mecanico'
        usuario.estado = 'activo'
        usuario.password = crear_password_interna_firebase()
        db.session.add(UsuarioModel(id_usuario=100, username='adminqa', email='admin@example.invalid',
            password='x', nombre='QA', apellido='Admin', rol='admin', estado='activo'))
        db.session.add(AdministradorModel(Usuario_idUsuario=100, legajo='A100'))
        db.session.get(UsuarioModel, 1).email = 'ocupado@example.invalid'
        db.session.commit()
        self.usuario = usuario
        self.identidad = {'uid':'uid-mecanico', 'email':'nuevo@example.invalid', 'email_verified':True}
        self.firebase = SimpleNamespace(email='nuevo@example.invalid', email_verified=True, disabled=False)
        self.headers = {'Authorization':'Bearer '+create_access_token(identity='3', additional_claims={'rol':'mecanico'})}
        self.cliente = self.fixture.app.test_client()

    def tearDown(self):
        db.session.rollback()
        AdministradorModel.query.filter_by(Usuario_idUsuario=100).delete()
        UsuarioModel.query.filter_by(id_usuario=100).delete()
        db.session.commit()
        db.session.remove()

    def sincronizar(self, identidad=None, firebase=None):
        with patch('services.firebase_service.FirebaseAuthService.verificar_token', return_value=identidad or self.identidad), patch(
            'services.firebase_service.FirebaseAuthService.obtener_usuario_por_uid', return_value=firebase or self.firebase
        ):
            return self.cliente.post('/api/perfil/correo/sincronizar', json={'firebaseToken':'mock'}, headers=self.headers)

    def test_perfil_no_guarda_correo_no_verificado_ni_otros_datos_parciales(self):
        r = self.cliente.put('/api/perfil', json={'email':'nuevo@example.invalid', 'nombre':'No guardar'}, headers=self.headers)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')
        self.assertEqual(self.usuario.nombre, 'Sol')

    def test_admin_tampoco_puede_cambiar_directamente_correo_vinculado(self):
        headers = {'Authorization':'Bearer '+create_access_token(identity='100', additional_claims={'rol':'admin'})}
        r = self.cliente.put('/api/admin/usuarios/3', json={'email':'nuevo@example.invalid'}, headers=headers)
        self.assertEqual(r.status_code, 409, r.get_json())
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_disponibilidad_rechaza_correo_ocupado_o_invalido(self):
        for email, esperado in [('ocupado@example.invalid',409), ('incorrecto',400), ('nuevo@example.invalid',200)]:
            r = self.cliente.post('/api/perfil/correo/disponibilidad', json={'email':email}, headers=self.headers)
            self.assertEqual(r.status_code, esperado)
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_correo_verificado_actualiza_perfil_sin_cambiar_uid(self):
        r = self.sincronizar()
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['perfil']['email'], 'nuevo@example.invalid')
        self.assertEqual(self.usuario.firebase_uid, 'uid-mecanico')
        self.assertEqual(self.sincronizar().status_code, 200)

    def test_uid_ajeno_y_correo_no_verificado_se_rechazan(self):
        for cambio in [{'uid':'ajeno'}, {'email_verified':False}]:
            identidad = {**self.identidad, **cambio}
            self.assertEqual(self.sincronizar(identidad).status_code, 403)
            self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_token_antiguo_o_cuenta_firebase_deshabilitada_no_actualizan_correo(self):
        for firebase in [SimpleNamespace(email='otro@example.invalid', email_verified=True, disabled=False),
                         SimpleNamespace(email='nuevo@example.invalid', email_verified=False, disabled=False),
                         SimpleNamespace(email='nuevo@example.invalid', email_verified=True, disabled=True)]:
            self.assertEqual(self.sincronizar(firebase=firebase).status_code, 403)
            self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_correo_en_uso_no_reemplaza_otra_cuenta(self):
        r = self.sincronizar({**self.identidad, 'email':'ocupado@example.invalid'})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')
        self.assertEqual(db.session.get(UsuarioModel, 1).email, 'ocupado@example.invalid')

    def test_login_con_correo_nuevo_sincroniza_por_uid(self):
        with patch('services.firebase_service.FirebaseAuthService.verificar_token', return_value=self.identidad), patch(
            'services.firebase_service.FirebaseAuthService.obtener_usuario_por_uid', return_value=self.firebase
        ):
            r = self.cliente.post('/api/auth/firebase-login', json={'token':'mock'})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['usuario']['email'], 'nuevo@example.invalid')
        self.assertEqual(r.get_json()['usuario']['id_usuario'], 3)

    def test_login_no_confunde_uid_propio_con_correo_ocupado_por_otro(self):
        identidad = {**self.identidad, 'email':'ocupado@example.invalid'}
        with patch('services.firebase_service.FirebaseAuthService.verificar_token', return_value=identidad):
            r = self.cliente.post('/api/auth/firebase-login', json={'token':'mock'})
        self.assertEqual(r.status_code, 409, r.get_json())
        self.assertNotIn('token', r.get_json())
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_fallo_firebase_conserva_correo_anterior(self):
        with patch('services.firebase_service.FirebaseAuthService.verificar_token', return_value=self.identidad), patch(
            'services.firebase_service.FirebaseAuthService.obtener_usuario_por_uid', side_effect=RuntimeError('Sin conexión')
        ), patch('controllers.perfil_controller.logger'):
            r = self.cliente.post('/api/perfil/correo/sincronizar', json={'firebaseToken':'mock'}, headers=self.headers)
        self.assertEqual(r.status_code, 503)
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_token_invalido_o_ausente_no_modifica_correo(self):
        r = self.cliente.post('/api/perfil/correo/sincronizar', json={}, headers=self.headers)
        self.assertEqual(r.status_code, 403)
        with patch('services.firebase_service.FirebaseAuthService.verificar_token', side_effect=ValueError('Inválido')):
            r = self.cliente.post('/api/perfil/correo/sincronizar', json={'firebaseToken':'mock'}, headers=self.headers)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')

    def test_fallo_db_no_confirma_cambio_y_permite_reintentar(self):
        with patch.object(db.session, 'commit', side_effect=RuntimeError('No disponible')), patch('controllers.perfil_controller.logger'):
            self.assertEqual(self.sincronizar().status_code, 503)
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')
        self.assertEqual(self.sincronizar().status_code, 200)

    def test_permite_editar_nombre_sin_tocar_correo(self):
        r = self.cliente.put('/api/perfil', json={'nombre':'Actualizado'}, headers=self.headers)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(self.usuario.email, 'anterior@example.invalid')
