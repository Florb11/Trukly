import unittest
from unittest.mock import patch
from datetime import date
from flask_jwt_extended import JWTManager, create_access_token
from db_instance import db
from models.usuario_model import UsuarioModel
from models.chofer_model import ChoferModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.viaje_cambio_model import ViajeCambioModel
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from models.notificacion_model import NotificacionModel
from routes.chofer_routes import chofer_routes
from routes.operador_routes import operador_routes
from utils.fecha_operativa import hoy_operativo


class HistorialEstadosViajeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-trip-lifecycle-audit-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(chofer_routes)
        cls.fixture.app.register_blueprint(operador_routes)
        for uid in [1,2]:
            db.session.get(UsuarioModel,uid).estado = 'activo'
        db.session.get(ChoferModel,1).vencimientoLicencia = date(2099,1,1)
        db.session.get(ViajeModel,2).estado = 'finalizado'
        db.session.add(UsuarioModel(id_usuario=100,username='admin_auditoria',password='x',nombre='QA',apellido='Admin',rol='admin',estado='activo'))
        db.session.commit()
        cls.client = cls.fixture.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.add(CamionModel(id_camion=90,matricula='AUD90',marca='Marca',modelo='QA',capacidad_carga=1000,nroTanque=90,estado='en viaje'))
        db.session.add(ViajeModel(id_viaje=90,OperadorLogistico_Usuario_idUsuario=2,Chofer_Usuario_idUsuario=1,Camion_id_camion=90,fecha_salida=hoy_operativo(),origen='A',destino='B',estado='pendiente',recorrido=10))
        db.session.commit()
        emisor = patch('controllers.chofer_controller.NotificacionService.enviar_push_pendientes')
        self.push = emisor.start()
        self.addCleanup(emisor.stop)

    def tearDown(self):
        db.session.rollback()
        NotificacionModel.query.delete()
        ViajeCambioModel.query.filter_by(id_viaje=90).delete()
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).delete()
        ViajeModel.query.filter_by(id_viaje=90).delete()
        CamionModel.query.filter_by(id_camion=90).delete()
        db.session.commit()
        db.session.info.pop('push_pendientes',None)
        db.session.remove()

    def headers(self, uid='1', rol='chofer'):
        return {'Authorization':'Bearer '+create_access_token(identity=uid,additional_claims={'rol':rol})}

    def aceptar(self):
        return self.client.put('/api/choferes/viajes/90/aceptar',headers=self.headers())

    def qr(self,tipo):
        return self.client.post('/api/choferes/viajes/90/registro',json={'tipo_registro':tipo},headers=self.headers())

    def eventos(self):
        return ViajeCambioModel.query.filter_by(id_viaje=90).order_by(ViajeCambioModel.id_cambio).all()

    def test_ciclo_completo_guarda_actor_fecha_y_estados_sin_duplicar(self):
        self.assertEqual(self.aceptar().status_code,200)
        self.assertEqual(self.aceptar().status_code,400)
        self.assertEqual([e.accion for e in self.eventos()],['viaje_aceptado'])
        self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).count(),0)
        self.assertEqual(self.qr('ingreso').status_code,201)
        self.assertEqual(self.qr('ingreso').status_code,400)
        self.assertEqual(self.qr('salida').status_code,201)
        self.assertEqual(self.qr('salida').status_code,400)
        db.session.remove()
        eventos = self.eventos()
        self.assertEqual([e.accion for e in eventos],['viaje_aceptado','viaje_iniciado','viaje_finalizado'])
        for e,antes,despues in zip(eventos,['pendiente','aceptado','en curso'],['aceptado','en curso','finalizado']):
            self.assertEqual(e.id_usuario,1)
            self.assertEqual(e.actor_nombre,'Ana García')
            self.assertIsNotNone(e.fecha_hora)
            self.assertEqual(e.datos['cambios']['estado'],{'antes':antes,'despues':despues})
        self.assertIn('fecha_control',eventos[1].datos)
        for uid,rol in [('2','operador'),('100','admin')]:
            r = self.client.get('/api/operador/viajes/90/historial',headers=self.headers(uid,rol))
            self.assertEqual(r.status_code,200,r.get_json())
            self.assertEqual([e['accion'] for e in r.get_json()],['viaje_finalizado','viaje_iniciado','viaje_aceptado'])
        self.assertEqual(db.session.get(ViajeModel,90).to_dict()['tiempo_viaje']['estado'],'confirmado')

    def test_fallo_historial_aceptacion_revierte_estado_y_notificacion(self):
        with patch('controllers.chofer_controller.registrar',side_effect=RuntimeError('Prueba')),patch('controllers.chofer_controller.logger'):
            self.assertEqual(self.aceptar().status_code,500)
        db.session.remove()
        self.assertEqual(db.session.get(ViajeModel,90).estado,'pendiente')
        self.assertEqual(len(self.eventos()),0)
        self.assertEqual(NotificacionModel.query.count(),0)
        self.push.assert_not_called()

    def test_fallo_historial_qr_revierte_control_y_estado(self):
        self.assertEqual(self.aceptar().status_code,200)
        for tipo,estado,controles,eventos in [('ingreso','aceptado',0,1),('salida','en curso',1,2)]:
            with patch('controllers.chofer_controller.registrar',side_effect=RuntimeError('Prueba')),patch('controllers.chofer_controller.logger'):
                self.assertEqual(self.qr(tipo).status_code,500)
            db.session.remove()
            self.assertEqual(db.session.get(ViajeModel,90).estado,estado)
            self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=90).count(),controles)
            self.assertEqual(len(self.eventos()),eventos)
            self.assertEqual(self.qr(tipo).status_code,201)
