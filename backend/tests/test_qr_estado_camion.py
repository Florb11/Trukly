import unittest
from datetime import date, datetime, timedelta
from types import SimpleNamespace

from flask import g

from controllers.chofer_controller import ChoferController
from db_instance import db
from models.chofer_model import ChoferModel
from utils.fecha_operativa import hoy_operativo
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel


class QrEstadoCamionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.add(CamionModel(id_camion=90, matricula='QR90', marca='Prueba', modelo='QA',
                                   capacidad_carga=1000, estado='disponible', nroTanque=90))
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.get(ChoferModel, 1).vencimientoLicencia = hoy_operativo() + timedelta(days=365)
        db.session.add(ViajeModel(id_viaje=90, OperadorLogistico_Usuario_idUsuario=2,
                                  Chofer_Usuario_idUsuario=1, Camion_id_camion=90,
                                  fecha_salida=date.today(), origen='A', destino='B',
                                  estado='aceptado', recorrido=10))
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).delete()
        ViajeModel.query.filter_by(id_viaje=90).delete()
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.commit()
        db.session.remove()

    def escanear(self, tipo='ingreso'):
        with self.fixture.app.test_request_context('/', method='POST', json={'tipo_registro': tipo}):
            g.chofer_actual = SimpleNamespace(id_usuario=1)
            respuesta, codigo = ChoferController.registrar_ingreso_salida.__wrapped__(90)
            return respuesta.get_json(), codigo

    def test_camion_no_habilitado_no_inicia_ni_guarda_qr(self):
        for estado in ['inactivo', 'en mantenimiento']:
            with self.subTest(estado=estado):
                db.session.get(CamionModel, 90).estado = estado
                db.session.commit()
                respuesta, codigo = self.escanear()
                self.assertEqual(codigo, 409, respuesta)
                self.assertIn('operador', respuesta['mensaje'])
                self.assertEqual(db.session.get(ViajeModel, 90).estado, 'aceptado')
                self.assertEqual(db.session.get(CamionModel, 90).estado, estado)
                self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).count(), 0)

    def test_reservado_inicia_y_no_duplica_control(self):
        db.session.get(CamionModel, 90).estado = 'en viaje'
        db.session.commit()
        self.assertEqual(self.escanear()[1], 201)
        self.assertEqual(db.session.get(ViajeModel, 90).estado, 'en curso')
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'en viaje')
        self.assertEqual(self.escanear()[1], 400)
        self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).count(), 1)

    def test_disponible_inicia_y_regreso_libera_camion(self):
        self.assertEqual(self.escanear()[1], 201)
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'en viaje')
        registro = RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).one()
        registro.fecha_hora = datetime.now() - timedelta(minutes=2)
        db.session.commit()
        self.assertEqual(self.escanear('salida')[1], 201)
        self.assertEqual(db.session.get(ViajeModel, 90).estado, 'finalizado')
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'disponible')

    def test_mantenimiento_no_impide_registrar_regreso_de_viaje_en_curso(self):
        self.assertEqual(self.escanear()[1], 201)
        db.session.get(CamionModel, 90).estado = 'en mantenimiento'
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).one().fecha_hora = datetime.now() - timedelta(minutes=2)
        db.session.commit()
        self.assertEqual(self.escanear('salida')[1], 201)
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'en mantenimiento')

    def test_licencia_vencida_bloquea_salida_sin_mutaciones(self):
        db.session.get(ChoferModel, 1).vencimientoLicencia = hoy_operativo() - timedelta(days=1)
        db.session.commit()
        respuesta, codigo = self.escanear()
        self.assertEqual(codigo, 409, respuesta)
        self.assertIn('licencia', respuesta['mensaje'])
        self.assertEqual(db.session.get(ViajeModel, 90).estado, 'aceptado')
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'disponible')
        self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).count(), 0)

    def test_licencia_valida_hoy_y_vencida_al_regresar(self):
        db.session.get(ChoferModel, 1).vencimientoLicencia = hoy_operativo()
        db.session.commit()
        self.assertEqual(self.escanear()[1], 201)
        db.session.get(ChoferModel, 1).vencimientoLicencia = hoy_operativo() - timedelta(days=1)
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).one().fecha_hora = datetime.now() - timedelta(minutes=2)
        db.session.commit()
        self.assertEqual(self.escanear('salida')[1], 201)
        self.assertEqual(db.session.get(ViajeModel, 90).estado, 'finalizado')
