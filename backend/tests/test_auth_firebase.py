import unittest
import time
from unittest.mock import patch
from types import SimpleNamespace

from flask_jwt_extended import JWTManager

from controllers.auth_controller import AuthController
from controllers.perfil_controller import PerfilController
from db_instance import db
from extensions import bcrypt
from models.usuario_model import UsuarioModel


class AuthFirebaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-jwt-secret-for-auth-regressions'
        JWTManager(cls.fixture.app)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.remove()
        self.usuario = UsuarioModel(
            username='prueba_auth', email='auth@example.invalid',
            nombre='Prueba', apellido='Local', rol='chofer', estado='activo',
            firebase_uid='uid-local',
            password=bcrypt.generate_password_hash('firebase:uid-local').decode(),
        )
        db.session.add(self.usuario)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        UsuarioModel.query.filter(UsuarioModel.username.in_(['prueba_auth', 'registro_auth'])).delete()
        db.session.commit()

        db.session.remove()

    def login(self, clave):
        with self.fixture.app.test_request_context('/', method='POST', json={
            'username': self.usuario.email, 'password': clave,
        }):
            return AuthController.login()

    def test_bloquea_password_interna_de_versiones_anteriores(self):
        with patch('controllers.auth_controller.create_access_token') as emitir:
            self.assertEqual(self.login('firebase:uid-local')[1], 401)
            emitir.assert_not_called()

    def test_bloquea_password_local_antigua_tras_vincular_firebase(self):
        self.usuario.password = bcrypt.generate_password_hash('Antigua123').decode()
        db.session.commit()
        self.assertEqual(self.login('Antigua123')[1], 401)

    def test_cuenta_local_migra_solo_tras_validar_password_y_estado(self):
        self.usuario.firebase_uid = None
        self.usuario.password = bcrypt.generate_password_hash('Local12345').decode()
        db.session.commit()
        with patch('controllers.auth_controller.FirebaseAuthService.migrar_usuario_local', return_value=SimpleNamespace(uid='uid-migrado')) as migrar:
            self.assertEqual(self.login('Incorrecta123')[1], 401)
            self.usuario.estado = 'inactivo'
            db.session.commit()
            self.assertEqual(self.login('Local12345')[1], 403)
            migrar.assert_not_called()
            self.usuario.estado = 'activo'
            db.session.commit()
            self.assertEqual(self.login('Local12345')[1], 200)
            migrar.assert_called_once()
            self.assertEqual(self.usuario.firebase_uid, 'uid-migrado')
            self.assertEqual(self.login('Local12345')[1], 401)

    def test_admin_local_vinculado_conserva_acceso_y_perfil_local(self):
        self.usuario.rol = 'admin'
        self.usuario.password = bcrypt.generate_password_hash('ActualFirebase123').decode()
        db.session.commit()
        self.assertEqual(self.login('Incorrecta123')[1], 401)
        self.assertTrue(PerfilController._preparar_respuesta_perfil(self.usuario)['password_local'])
        (_, codigo), actualizar = self.cambiar_password()
        self.assertEqual(codigo, 200)
        actualizar.assert_not_called()
        self.assertEqual(self.login('ActualFirebase123')[1], 401)
        self.usuario.estado = 'inactivo'
        db.session.commit()
        self.assertEqual(self.login('NuevaFirebase123')[1], 403)
        self.usuario.estado = 'activo'
        db.session.commit()
        with patch('controllers.auth_controller.FirebaseAuthService.migrar_usuario_local', return_value=SimpleNamespace(uid='uid-local')):
            self.assertEqual(self.login('NuevaFirebase123')[1], 200)
        self.assertFalse(PerfilController._preparar_respuesta_perfil(self.usuario)['password_local'])
        self.assertEqual(self.login('NuevaFirebase123')[1], 401)

    def test_admin_no_puede_entrar_con_password_interna(self):
        self.usuario.rol = 'admin'
        db.session.commit()
        self.assertEqual(self.login('firebase:uid-local')[1], 401)
        self.assertFalse(PerfilController._preparar_respuesta_perfil(self.usuario)['password_local'])

    def test_fallo_migracion_conserva_credencial_local_y_no_emite_token(self):
        self.usuario.firebase_uid = None
        self.usuario.password = bcrypt.generate_password_hash('Local12345').decode()
        db.session.commit()
        anterior = self.usuario.password
        with patch('controllers.auth_controller.FirebaseAuthService.migrar_usuario_local', side_effect=RuntimeError('sin conexión')), patch(
            'controllers.auth_controller.create_access_token'
        ) as emitir, patch('controllers.auth_controller.logger'):
            self.assertEqual(self.login('Local12345')[1], 503)
            emitir.assert_not_called()
        db.session.refresh(self.usuario)
        self.assertEqual(self.usuario.password, anterior)
        self.assertIsNone(self.usuario.firebase_uid)

    def test_token_firebase_solo_no_vincula_cuenta_local_por_correo(self):
        self.usuario.firebase_uid = None
        db.session.commit()
        with self.fixture.app.test_request_context('/', method='POST', json={'token': 'mock'}), patch(
            'controllers.auth_controller.FirebaseAuthService.verificar_token', return_value={
                'uid': 'uid-nuevo', 'email': self.usuario.email,
            }
        ):
            self.assertEqual(AuthController.login_firebase()[1], 409)
        self.assertIsNone(self.usuario.firebase_uid)

    def test_login_firebase_valido_y_cuentas_no_activas(self):
        for estado, esperado in [('activo', 200), ('inactivo', 403), ('pendiente', 403)]:
            self.usuario.estado = estado
            db.session.commit()
            with self.fixture.app.test_request_context('/', method='POST', json={'token': 'mock'}), patch(
                'controllers.auth_controller.FirebaseAuthService.verificar_token',
                return_value={'uid': 'uid-local', 'email': self.usuario.email},
            ):
                self.assertEqual(AuthController.login_firebase()[1], esperado)

    def test_nuevo_registro_no_genera_password_derivada_del_uid(self):
        with self.fixture.app.test_request_context('/', method='POST', json={
            'firebaseToken': 'mock', 'username': 'registro_auth',
            'email': 'registro@example.invalid', 'nombre': 'Prueba', 'apellido': 'Registro',
        }), patch('controllers.auth_controller.FirebaseAuthService.verificar_token', return_value={
            'uid': 'uid-registro', 'email': 'registro@example.invalid',
        }):
            self.assertEqual(AuthController.registrar_chofer_firebase()[1], 201)
        usuario = UsuarioModel.query.filter_by(username='registro_auth').one()
        self.assertFalse(bcrypt.check_password_hash(usuario.password, 'firebase:uid-registro'))
        self.assertEqual(usuario.estado, 'pendiente')

    def cambiar_password(self, identidad=None, datos=None, error=None):
        payload = {'password_actual': 'ActualFirebase123', 'password_nueva': 'NuevaFirebase123',
                   'confirmar_password': 'NuevaFirebase123', 'firebaseToken': 'mock'}
        payload.update(datos or {})
        with self.fixture.app.test_request_context('/', method='PUT', json=payload), patch.object(
            PerfilController, '_obtener_usuario_actual', return_value=self.usuario
        ), patch('controllers.perfil_controller.FirebaseAuthService.verificar_token',
                 return_value=identidad, side_effect=error), patch(
            'controllers.perfil_controller.FirebaseAuthService.cambiar_password'
        ) as actualizar:
            respuesta = PerfilController.cambiar_password.__wrapped__()
            return respuesta, actualizar

    def identidad_reciente(self):
        return {'uid': 'uid-local', 'auth_time': time.time(),
                'firebase': {'sign_in_provider': 'password'}}

    def test_cambio_firebase_actualiza_solo_firebase(self):
        hash_anterior = self.usuario.password
        (_, codigo), actualizar = self.cambiar_password(self.identidad_reciente())
        self.assertEqual(codigo, 200)
        actualizar.assert_called_once_with('uid-local', 'NuevaFirebase123')
        self.assertEqual(self.usuario.password, hash_anterior)
        self.assertEqual(self.login('NuevaFirebase123')[1], 401)

    def test_cambio_rechaza_otro_uid_token_viejo_futuro_o_proveedor_google(self):
        for cambio in [{'uid': 'otro'}, {'auth_time': time.time()-600},
                       {'auth_time': time.time()+600}, {'auth_time': None},
                       {'firebase': {'sign_in_provider': 'google.com'}}]:
            identidad = self.identidad_reciente()
            identidad.update(cambio)
            (_, codigo), actualizar = self.cambiar_password(identidad)
            self.assertEqual(codigo, 403)
            actualizar.assert_not_called()

    def test_cambio_rechaza_token_invalido_y_ausente(self):
        (_, codigo), actualizar = self.cambiar_password(error=ValueError('Token inválido'))
        self.assertEqual(codigo, 403)
        actualizar.assert_not_called()
        (_, codigo), actualizar = self.cambiar_password(datos={'firebaseToken': None})
        self.assertEqual(codigo, 403)
        actualizar.assert_not_called()

    def test_cambio_valida_confirmacion_fortaleza_y_password_diferente(self):
        for datos in [{'confirmar_password': 'OtraClave123'},
                      {'password_nueva': 'abc', 'confirmar_password': 'abc'},
                      {'password_nueva': 'ActualFirebase123', 'confirmar_password': 'ActualFirebase123'}]:
            (_, codigo), actualizar = self.cambiar_password(self.identidad_reciente(), datos)
            self.assertEqual(codigo, 400)
            actualizar.assert_not_called()

    def test_cambio_local_sigue_validando_y_actualizando_hash(self):
        self.usuario.firebase_uid = None
        self.usuario.password = bcrypt.generate_password_hash('ActualFirebase123').decode()
        db.session.commit()
        (_, codigo), actualizar = self.cambiar_password()
        self.assertEqual(codigo, 200)
        actualizar.assert_not_called()
        self.assertTrue(bcrypt.check_password_hash(self.usuario.password, 'NuevaFirebase123'))

    def test_falla_firebase_no_informa_exito_ni_cambia_hash_local(self):
        anterior = self.usuario.password
        with self.fixture.app.test_request_context('/', method='PUT', json={
            'password_actual': 'ActualFirebase123', 'password_nueva': 'NuevaFirebase123',
            'confirmar_password': 'NuevaFirebase123', 'firebaseToken': 'mock',
        }), patch.object(PerfilController, '_obtener_usuario_actual', return_value=self.usuario), patch(
            'controllers.perfil_controller.FirebaseAuthService.verificar_token', return_value=self.identidad_reciente()
        ), patch('controllers.perfil_controller.FirebaseAuthService.cambiar_password', side_effect=RuntimeError('indisponible')), patch('controllers.perfil_controller.logger'):
            self.assertEqual(PerfilController.cambiar_password.__wrapped__()[1], 502)
        self.assertEqual(self.usuario.password, anterior)


if __name__ == '__main__':
    unittest.main()
