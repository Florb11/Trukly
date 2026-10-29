import unittest
from types import SimpleNamespace
from unittest.mock import patch
from flask import g
from controllers.chofer_controller import ChoferController
from controllers.viaje_controller import ViajeController
from models.viaje_model import ViajeModel


class ChoferViajeAsignacionesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def comprobar(self, datos):
        self.assertEqual(datos["chofer_nombre"], "Ana García")
        self.assertEqual(datos["operador_nombre"], "Juan Pérez")
        self.assertEqual(datos["camion_nombre"], "Marca Modelo (AAA111)")
        self.assertNotIn("password", datos)

    def test_listado_que_consume_la_web_chofer(self):
        chofer = SimpleNamespace(id_usuario=1, obtener_mis_viajes=lambda query: query.filter_by(Chofer_Usuario_idUsuario=1).all())
        with self.fixture.app.test_request_context("/api/choferes/mis-viajes"):
            g.chofer_actual = chofer
            respuesta, codigo = ChoferController.listar_viajes_propios.__wrapped__()
        self.assertEqual(codigo, 200)
        for datos in respuesta.get_json():
            self.comprobar(datos)

    def test_detalle_que_consume_el_modal(self):
        with self.fixture.app.test_request_context("/api/viaje/1"), patch.object(ViajeController, "obtener_rol_actual", return_value="chofer"), patch.object(ViajeController, "obtener_id_usuario_actual", return_value=1):
            respuesta, codigo = ViajeController.obtener_viaje.__wrapped__(1)
        self.assertEqual(codigo, 200)
        self.comprobar(respuesta.get_json())

    def test_reportes_propios_incluyen_nombres(self):
        chofer = SimpleNamespace(id_usuario=1, obtener_mis_reportes=lambda query: query.filter_by(Chofer_Usuario_idUsuario=1).all())
        with self.fixture.app.test_request_context("/api/choferes/mis-reportes"):
            g.chofer_actual = chofer
            respuesta, codigo = ChoferController.listar_reportes_propios.__wrapped__()
        self.assertEqual(codigo, 200)
        filas = respuesta.get_json()
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[0]["chofer_nombre"], "Ana García")
        self.assertEqual(filas[0]["camion_nombre"], "Marca Modelo (AAA111)")
        self.assertEqual(filas[1]["mecanico_nombre"], "Sol Díaz")
        self.assertIsNone(filas[0]["mecanico_nombre"])

    def test_otro_chofer_no_accede_a_las_asignaciones(self):
        with self.fixture.app.test_request_context("/api/viaje/1"), patch.object(ViajeController, "obtener_rol_actual", return_value="chofer"), patch.object(ViajeController, "obtener_id_usuario_actual", return_value=999):
            _, codigo = ViajeController.obtener_viaje.__wrapped__(1)
        self.assertEqual(codigo, 403)


if __name__ == "__main__":
    unittest.main()
