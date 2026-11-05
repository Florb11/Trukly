import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from flask import g

from controllers.chofer_controller import ChoferController
from controllers.reporte_controller import ReporteController
from db_instance import db
from models.camion_model import CamionModel
from models.reporte_model import ReporteModel
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from models.usuario_model import UsuarioModel
from models.viaje_model import ViajeModel
from services.camion_disponibilidad_service import marcar_camion_tras_reporte


class FallaDuranteViajeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.get(CamionModel, 1).estado = 'en viaje'
        db.session.get(ViajeModel, 2).estado = 'en curso'
        db.session.get(UsuarioModel, 3).estado = 'activo'
        ReporteModel.query.update({'estado': 'cancelado'})
        db.session.add(RegistroIngresoSalidaModel(Viaje_id_viaje=2, tipo_registro='ingreso',
                         fecha_hora=datetime.now() - timedelta(minutes=2)))
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=2).delete()
        ReporteModel.query.filter(ReporteModel.id_reporte > 2).delete()
        db.session.commit()
        db.session.remove()

    def crear_reporte(self):
        with self.fixture.app.test_request_context('/', method='POST', json={
            'Camion_id_camion': 1, 'descripcion': 'Falla detectada durante el viaje',
        }), patch('controllers.reporte_controller.AuthService.obtener_id_usuario_actual', return_value=1), patch.object(
            ReporteController, 'notificar_reporte_creado'
        ), patch('controllers.reporte_controller.AdminNotificacionService.nueva_falla'), patch(
            'controllers.reporte_controller.NotificacionService.enviar_push_pendientes'
        ):
            respuesta, codigo = ReporteController.crear_reporte.__wrapped__()
            self.assertEqual(codigo, 201, respuesta.get_json())
            return respuesta.get_json()['reporte']['id_reporte']

    def cambiar_reporte(self, id_reporte, estado, rol='admin'):
        datos = {'estado': estado, 'motivo_cancelacion': 'Reporte duplicado'}
        if estado == 'en revision':
            datos['Mecanico_Usuario_idUsuario'] = 3
        with self.fixture.app.test_request_context('/', method='PUT', json=datos), patch(
            'controllers.reporte_controller.AuthService.obtener_rol_actual', return_value=rol
        ), patch('controllers.reporte_controller.obtener_admin_actual_desde_token', return_value=SimpleNamespace(
            cambiar_estado_reporte=lambda r, e: r.cambiar_estado(e)
        )), patch.object(ReporteController, 'notificar_reporte_asignado'), patch(
            'controllers.reporte_controller.NotificacionService.enviar_push_pendientes'
        ):
            respuesta, codigo = ReporteController.cambiar_estado_reporte.__wrapped__(id_reporte)
            self.assertEqual(codigo, 200, respuesta.get_json())

    def regreso(self):
        with self.fixture.app.test_request_context('/', method='POST', json={'tipo_registro': 'salida'}):
            g.chofer_actual = SimpleNamespace(id_usuario=1)
            respuesta, codigo = ChoferController.registrar_ingreso_salida.__wrapped__(2)
            self.assertEqual(codigo, 201, respuesta.get_json())

    def test_reportar_y_asignar_mecanico_conserva_en_viaje(self):
        id_reporte = self.crear_reporte()
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'en viaje')
        self.cambiar_reporte(id_reporte, 'en revision')
        self.assertEqual(db.session.get(ReporteModel, id_reporte).Mecanico_Usuario_idUsuario, 3)
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'en viaje')
        self.assertEqual(db.session.get(ViajeModel, 2).estado, 'en curso')

    def test_regreso_con_falla_pendiente_pasa_a_mantenimiento(self):
        self.crear_reporte()
        self.regreso()
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'en mantenimiento')
        self.assertEqual(db.session.get(ViajeModel, 2).estado, 'finalizado')

    def test_cerrar_falla_antes_de_regreso_no_libera_camion(self):
        for estado in ['resuelto', 'cancelado']:
            with self.subTest(estado=estado):
                id_reporte = self.crear_reporte()
                self.cambiar_reporte(id_reporte, estado)
                self.assertEqual(db.session.get(CamionModel, 1).estado, 'en viaje')
        self.regreso()
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'disponible')

    def test_sin_viaje_en_curso_falla_activa_pasa_a_mantenimiento(self):
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.get(CamionModel, 1).estado = 'disponible'
        db.session.commit()
        self.assertTrue(marcar_camion_tras_reporte(1))
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'en mantenimiento')
