import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch
from flask import Flask, g
from src.Viaje import Viaje
from utils.fecha_operativa import hoy_operativo
from controllers.operador_controller import OperadorController
from controllers.viaje_controller import ViajeController


class ViajeFechasCreacionTest(unittest.TestCase):
    def test_salida_ayer_hoy_y_manana(self):
        hoy = date(2026, 10, 29)
        for salida, esperado in [("2026-10-28", False), ("2026-10-29", True), ("2026-10-30", True)]:
            self.assertEqual(Viaje.validar_fechas_creacion({"fecha_salida": salida}, hoy)[0], esperado)

    def test_llegada_no_anterior(self):
        for llegada, esperado in [("2026-10-28", False), ("2026-10-29", True), ("2026-10-30", True), ("invalida", False)]:
            self.assertEqual(Viaje.validar_fechas_creacion({"fecha_salida": "2026-10-29", "fecha_llegada": llegada}, date(2026, 10, 29))[0], esperado)

    def test_medianoche_utc_no_adelanta_dia_operativo(self):
        self.assertEqual(hoy_operativo(datetime(2026, 10, 30, 1, 30, tzinfo=timezone.utc)), date(2026, 10, 29))
        self.assertEqual(hoy_operativo(datetime(2026, 10, 30, 3, 0, tzinfo=timezone.utc)), date(2026, 10, 30))

    def test_ambos_endpoints_rechazan_pasado_antes_de_consultar_recursos(self):
        app = Flask(__name__)
        datos = {"origen": "A", "destino": "B", "fecha_salida": "2000-01-01", "Chofer_Usuario_idUsuario": 1, "Camion_id_camion": 1}
        with app.test_request_context("/", method="POST", json=datos), patch.object(OperadorController, "_ubicaciones_validas", return_value=True):
            g.operador_actual = SimpleNamespace(id_usuario=2)
            respuesta, codigo = OperadorController.crear_viaje.__wrapped__()
            self.assertEqual(codigo, 400)
            self.assertIn("hoy", respuesta.get_json()["mensaje"])
        with app.test_request_context("/", method="POST", json=datos), patch.object(ViajeController, "obtener_rol_actual", return_value="operador"), patch.object(ViajeController, "obtener_id_usuario_actual", return_value=2):
            respuesta, codigo = ViajeController.crear_viaje.__wrapped__()
            self.assertEqual(codigo, 400)
            self.assertIn("hoy", respuesta.get_json()["mensaje"])


if __name__ == "__main__":
    unittest.main()
