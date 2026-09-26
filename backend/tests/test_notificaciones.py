import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from controllers.notificacion_controller import NotificacionController
from services.notificacion_service import NotificacionService
from src.Notificacion import Notificacion


class NotificacionServiceTest(unittest.TestCase):
    @patch.object(NotificacionService, "agregar_a_sesion")
    def test_crear_construye_una_notificacion_valida(self, agregar):
        agregar.side_effect = lambda notificacion: notificacion

        notificacion = NotificacionService.crear(
            17,
            "Nuevo viaje asignado",
            "Se te asignó el viaje #42.",
            "viaje_asignado",
            datetime(2026, 9, 26, 10, 30),
        )

        self.assertEqual(notificacion.id_usuario, 17)
        self.assertEqual(notificacion.tipo, "viaje_asignado")
        self.assertFalse(notificacion.leida)
        self.assertTrue(notificacion.validar_datos())

    @patch.object(NotificacionService, "crear")
    def test_crear_para_usuarios_elimina_destinatarios_duplicados(self, crear):
        NotificacionService.crear_para_usuarios(
            [22, 23, 22],
            "Aviso",
            "Mensaje",
            "prueba",
        )

        self.assertEqual([llamada.args[0] for llamada in crear.call_args_list], [22, 23])


class NotificacionPermisosTest(unittest.TestCase):
    def test_convertir_modelo_no_reemplaza_el_destinatario(self):
        modelo = SimpleNamespace(
            id_notificacion=5,
            Usuario_idUsuario=17,
            titulo="Nuevo viaje",
            mensaje="Se te asignó un viaje.",
            leida=False,
            fecha_hora=datetime(2026, 9, 26, 10, 30),
            tipo="viaje_asignado",
        )
        otro_usuario = SimpleNamespace(id_usuario=23, rol="mecanico")

        notificacion = NotificacionController.crear_objeto_notificacion(modelo)

        self.assertEqual(notificacion.id_usuario, 17)
        self.assertFalse(notificacion.marcar_como_leida_por(otro_usuario))
        self.assertFalse(notificacion.leida)

    def test_admin_no_puede_modificar_una_notificacion_ajena(self):
        admin = SimpleNamespace(id_usuario=1, rol="admin")
        notificacion = Notificacion(
            5,
            17,
            "Nuevo viaje",
            "Se te asignó un viaje.",
            False,
            datetime(2026, 9, 26, 10, 30),
        )

        self.assertFalse(notificacion.marcar_como_leida_por(admin))
        self.assertFalse(notificacion.leida)

    def test_destinatario_puede_marcar_como_leida(self):
        usuario = SimpleNamespace(id_usuario=17, rol="chofer")
        notificacion = Notificacion(
            5,
            17,
            "Nuevo viaje",
            "Se te asignó un viaje.",
            False,
            datetime(2026, 9, 26, 10, 30),
        )

        self.assertTrue(notificacion.marcar_como_leida_por(usuario))
        self.assertTrue(notificacion.leida)


if __name__ == "__main__":
    unittest.main()
