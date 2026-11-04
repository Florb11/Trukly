import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from flask import g

from controllers.mecanico_controller import MecanicoController
from controllers.reporte_controller import ReporteController
from db_instance import db
from models.camion_model import CamionModel
from models.reporte_model import ReporteModel
from models.viaje_model import ViajeModel
from src.Mecanico import Mecanico


class CierreReporteCamionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        ReporteModel.query.update({'estado': 'cancelado'})
        db.session.add(ReporteModel(id_reporte=80, fecha_hora=datetime.now(), descripcion='Prueba',
                                    estado='en revision', Camion_id_camion=1,
                                    Chofer_Usuario_idUsuario=1, Mecanico_Usuario_idUsuario=3))
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        ReporteModel.query.filter_by(id_reporte=80).delete()
        db.session.commit()
        db.session.remove()

    def preparar(self, estado_viaje, estado_camion='en mantenimiento'):
        db.session.get(ViajeModel, 2).estado = estado_viaje
        db.session.get(CamionModel, 1).estado = estado_camion
        db.session.get(ReporteModel, 80).estado = 'en revision'
        db.session.commit()

    def cerrar(self, actor):
        if actor == 'mecanico':
            mecanico = Mecanico.crear_desde_datos({'id_usuario': 3, 'username': 'qa',
                'email': 'qa@example.invalid', 'password': 'x', 'nombre': 'QA', 'apellido': 'Prueba',
                'estado': 'activo', 'rol': 'mecanico', 'legajo': 'M1', 'especialidad': 'Motor'})
            with self.fixture.app.test_request_context('/', method='PUT', json={'nota_reparacion': 'Reparado'}), patch.object(
                MecanicoController, 'notificar_reporte_resuelto'
            ), patch('controllers.mecanico_controller.NotificacionService.enviar_push_pendientes'):
                g.mecanico_actual = mecanico
                respuesta, codigo = MecanicoController.resolver_reporte.__wrapped__(80)
        else:
            with self.fixture.app.test_request_context('/', method='PUT', json={
                'estado': actor, 'motivo_cancelacion': 'Duplicado',
            }), patch('controllers.reporte_controller.AuthService.obtener_rol_actual', return_value='admin'), patch(
                'controllers.reporte_controller.obtener_admin_actual_desde_token',
                return_value=SimpleNamespace(cambiar_estado_reporte=lambda r, e: r.cambiar_estado(e)),
            ), patch('controllers.reporte_controller.NotificacionService.enviar_push_pendientes'):
                respuesta, codigo = ReporteController.cambiar_estado_reporte.__wrapped__(80)
        self.assertEqual(codigo, 200, respuesta.get_json())

    def test_conserva_reserva_para_viajes_pendientes_aceptados_y_en_curso(self):
        for actor in ['mecanico', 'resuelto', 'cancelado']:
            for estado in ['pendiente', 'aceptado', 'en curso']:
                with self.subTest(actor=actor, estado=estado):
                    self.preparar(estado)
                    self.cerrar(actor)
                    self.assertEqual(db.session.get(CamionModel, 1).estado, 'en viaje')
                    self.assertEqual(db.session.get(ViajeModel, 2).estado, estado)

    def test_sin_viaje_activo_vuelve_a_disponible(self):
        for actor in ['mecanico', 'resuelto', 'cancelado']:
            for estado in ['finalizado', 'cancelado']:
                with self.subTest(actor=actor, estado=estado):
                    self.preparar(estado)
                    self.cerrar(actor)
                    self.assertEqual(db.session.get(CamionModel, 1).estado, 'disponible')

    def test_otra_falla_activa_mantiene_mantenimiento(self):
        db.session.get(ReporteModel, 1).estado = 'pendiente'
        db.session.commit()
        for actor in ['mecanico', 'resuelto', 'cancelado']:
            self.preparar('en curso')
            self.cerrar(actor)
            self.assertEqual(db.session.get(CamionModel, 1).estado, 'en mantenimiento')

    def test_camion_inactivo_no_se_reactiva_al_cerrar_falla(self):
        for actor in ['mecanico', 'resuelto', 'cancelado']:
            self.preparar('en curso', 'inactivo')
            self.cerrar(actor)
            self.assertEqual(db.session.get(CamionModel, 1).estado, 'inactivo')
