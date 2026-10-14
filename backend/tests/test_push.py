import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask, g
from controllers.push_controller import PushController
from services.notificacion_service import NotificacionService


class PushTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_delete_cannot_remove_other_users_device(self):
        with self.app.test_request_context(method="DELETE", json={"token": "device"}):
            g.usuario_actual = SimpleNamespace(id_usuario=7)
            with patch("controllers.push_controller.PushDispositivoModel") as model, patch("controllers.push_controller.db") as database:
                model.query.filter_by.return_value.first.return_value = SimpleNamespace(Usuario_idUsuario=8)
                _, status = PushController.dispositivo.__wrapped__()
                self.assertEqual(status, 200)
                database.session.delete.assert_not_called()

    def test_register_binds_device_to_authenticated_user(self):
        with self.app.test_request_context(method="POST", json={"token": "device"}):
            g.usuario_actual = SimpleNamespace(id_usuario=7)
            with patch("controllers.push_controller.PushDispositivoModel") as model, patch("controllers.push_controller.db") as database:
                device = SimpleNamespace(Usuario_idUsuario=8)
                model.query.filter_by.return_value.first.return_value = device
                _, status = PushController.dispositivo.__wrapped__()
                self.assertEqual(status, 200)
                self.assertEqual(device.Usuario_idUsuario, 7)
                database.session.commit.assert_called_once()

    def test_push_targets_only_recipient_devices(self):
        with patch("services.notificacion_service.db") as database, patch("models.push_dispositivo_model.PushDispositivoModel") as model, patch("services.firebase_service.FirebaseAuthService.inicializar"), patch("firebase_admin.messaging.send") as send:
            database.session.info = {"push_pendientes": [{"usuario": 7, "titulo": "Aviso", "mensaje": "Mensaje"}]}
            model.query.filter_by.return_value.all.return_value = [SimpleNamespace(token="device")]
            NotificacionService.enviar_push_pendientes()
            model.query.filter_by.assert_called_once_with(Usuario_idUsuario=7)
            self.assertEqual(send.call_args.args[0].token, "device")
            self.assertNotIn("push_pendientes", database.session.info)

    def test_firebase_failure_does_not_escape_to_business_operation(self):
        with patch("services.notificacion_service.db") as database, patch("services.firebase_service.FirebaseAuthService.inicializar", side_effect=RuntimeError("test")), patch("utils.app_logger.get_app_logger", return_value=MagicMock()):
            database.session.info = {"push_pendientes": [{"usuario": 7, "titulo": "Aviso", "mensaje": "Mensaje"}]}
            NotificacionService.enviar_push_pendientes()
            database.session.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
