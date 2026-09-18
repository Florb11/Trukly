import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import app
from models.camion_model import CamionModel
from models.reporte_model import ReporteModel
from models.viaje_model import ViajeModel
from services.camion_disponibilidad_service import actualizar_camion_tras_cancelacion
from src.Camion import Camion


class CamionDisponibilidadServiceTest(unittest.TestCase):
    def setUp(self):
        self.contexto = app.app_context()
        self.contexto.push()
        self.addCleanup(self.contexto.pop)
        self.viaje = SimpleNamespace(id_viaje=10, Camion_id_camion=4)
        self.camion = SimpleNamespace(id_camion=4, estado=Camion.ESTADO_EN_VIAJE)
        self.camiones = patch.object(CamionModel, "query").start()
        self.viajes = patch.object(ViajeModel, "query").start()
        self.reportes = patch.object(ReporteModel, "query").start()
        self.addCleanup(patch.stopall)
        self.camiones.get.return_value = self.camion
        self.viajes.filter.return_value.first.return_value = None
        self.reportes.filter.return_value.first.return_value = None

    def test_libera_camion_sin_viajes_ni_reportes_activos(self):
        actualizar_camion_tras_cancelacion(self.viaje)
        self.assertEqual(self.camion.estado, Camion.ESTADO_DISPONIBLE)

    def test_conserva_ocupacion_si_hay_otro_viaje_activo(self):
        self.viajes.filter.return_value.first.return_value = object()
        actualizar_camion_tras_cancelacion(self.viaje)
        self.assertEqual(self.camion.estado, Camion.ESTADO_EN_VIAJE)

    def test_pasa_a_mantenimiento_si_hay_reporte_activo(self):
        self.reportes.filter.return_value.first.return_value = object()
        actualizar_camion_tras_cancelacion(self.viaje)
        self.assertEqual(self.camion.estado, Camion.ESTADO_EN_MANTENIMIENTO)

    def test_no_modifica_camion_que_ya_esta_en_mantenimiento(self):
        self.camion.estado = Camion.ESTADO_EN_MANTENIMIENTO
        actualizar_camion_tras_cancelacion(self.viaje)
        self.assertEqual(self.camion.estado, Camion.ESTADO_EN_MANTENIMIENTO)
        self.viajes.filter.assert_not_called()


if __name__ == "__main__":
    unittest.main()
