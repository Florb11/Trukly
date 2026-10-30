import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services.firebase_service import FirebaseAuthService, FirebaseMigrationConflict


class MigracionFirebaseServiceTest(unittest.TestCase):
    def setUp(self):
        self.usuario = SimpleNamespace(email='local@example.invalid', firebase_uid=None,
                                       nombre='Cuenta', apellido='Local')
        self.firebase = SimpleNamespace(uid='uid-existente', disabled=False,
                                        email_verified=False, provider_data=[])

    def test_crea_acceso_nuevo_con_password_actual_sin_marcar_email_verificado(self):
        with patch.object(FirebaseAuthService, 'obtener_usuario_por_email', return_value=None), patch.object(
            FirebaseAuthService, 'inicializar'
        ), patch('services.firebase_service.auth.create_user', return_value=self.firebase) as crear:
            self.assertEqual(FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345'), self.firebase)
            crear.assert_called_once_with(email=self.usuario.email, password='Local12345',
                                          display_name='Cuenta Local', email_verified=False, disabled=False)

    def test_configura_password_solo_para_cuenta_vacia_ya_vinculada(self):
        self.usuario.firebase_uid = self.firebase.uid
        with patch.object(FirebaseAuthService, 'obtener_usuario_por_email', return_value=self.firebase), patch(
            'services.firebase_service.auth.update_user', return_value=self.firebase
        ) as actualizar:
            FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345')
            actualizar.assert_called_once_with(self.firebase.uid, password='Local12345')

    def test_no_sobrescribe_cuenta_existente_sin_prueba_firebase(self):
        self.firebase.provider_data = [SimpleNamespace(provider_id='password')]
        with patch.object(FirebaseAuthService, 'obtener_usuario_por_email', return_value=self.firebase), patch(
            'services.firebase_service.auth.update_user'
        ) as actualizar:
            with self.assertRaises(FirebaseMigrationConflict):
                FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345')
            actualizar.assert_not_called()

    def test_vincula_cuenta_en_uso_solo_con_token_propio_y_reciente(self):
        self.firebase.provider_data = [SimpleNamespace(provider_id='password')]
        identidad = {'uid': self.firebase.uid, 'email': self.usuario.email, 'auth_time': time.time()}
        with patch.object(FirebaseAuthService, 'obtener_usuario_por_email', return_value=self.firebase), patch.object(
            FirebaseAuthService, 'verificar_token', return_value=identidad
        ), patch('services.firebase_service.auth.update_user') as actualizar:
            self.assertEqual(FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345', 'token'), self.firebase)
            actualizar.assert_not_called()
            for cambio in [{'uid': 'otro'}, {'email': 'otro@example.invalid'}, {'auth_time': time.time()-600}]:
                original = dict(identidad)
                identidad.update(cambio)
                with self.assertRaises(FirebaseMigrationConflict):
                    FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345', 'token')
                identidad.clear()
                identidad.update(original)

    def test_rechaza_cuenta_deshabilitada_o_uid_distinto(self):
        with patch.object(FirebaseAuthService, 'obtener_usuario_por_email', return_value=self.firebase):
            self.firebase.disabled = True
            with self.assertRaises(FirebaseMigrationConflict):
                FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345')
            self.firebase.disabled = False
            self.usuario.firebase_uid = 'otro-uid'
            with self.assertRaises(FirebaseMigrationConflict):
                FirebaseAuthService.migrar_usuario_local(self.usuario, 'Local12345')
