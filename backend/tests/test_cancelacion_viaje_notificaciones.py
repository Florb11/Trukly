import unittest
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token

from db_instance import db
from models.administrador_model import AdministradorModel
from models.camion_model import CamionModel
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel
from models.viaje_model import ViajeModel
from models.viaje_cambio_model import ViajeCambioModel
from routes.operador_routes import operador_routes
from routes.viaje_routes import viaje_routes


class CancelacionViajeNotificacionesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-trip-cancellation-secret'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(operador_routes)
        cls.fixture.app.register_blueprint(viaje_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.add(UsuarioModel(id_usuario=100, username='admin_cancelar', password='x',
            nombre='QA', apellido='Admin', rol='admin', estado='activo'))
        db.session.add(AdministradorModel(Usuario_idUsuario=100, legajo='A100'))
        for uid in [1, 2]:
            db.session.get(UsuarioModel, uid).estado = 'activo'
        db.session.commit()
        self.client = self.fixture.app.test_client()
        emisor = patch('services.notificacion_service.NotificacionService.enviar_push_pendientes')
        self.push = emisor.start()
        self.addCleanup(emisor.stop)

    def tearDown(self):
        db.session.rollback()
        NotificacionModel.query.delete()
        ViajeCambioModel.query.delete()
        AdministradorModel.query.filter_by(Usuario_idUsuario=100).delete()
        UsuarioModel.query.filter_by(id_usuario=100).delete()
        db.session.commit()
        db.session.info.pop('push_pendientes', None)

    def preparar(self, estado='aceptado'):
        NotificacionModel.query.delete()
        ViajeCambioModel.query.delete()
        viaje = db.session.get(ViajeModel, 2)
        viaje.estado = estado
        viaje.observaciones = 'Observación original'
        db.session.get(CamionModel, 1).estado = 'en viaje'
        db.session.commit()
        self.push.reset_mock()

    def cancelar(self, rol, motivo='Cambio de "plan" & fecha'):
        identidad = '100' if rol == 'admin' else '2'
        token = create_access_token(identity=identidad, additional_claims={'rol':rol})
        ruta = '/api/admin/viajes/2/cancelar' if rol == 'admin' else '/api/operador/viajes/2/cancelar'
        return self.client.put(ruta, headers={'Authorization':'Bearer '+token}, json={'motivo':motivo})

    def test_cancelacion_avisa_a_chofer_y_admin_una_sola_vez(self):
        for rol in ['admin', 'operador']:
            for estado in ['pendiente', 'aceptado']:
                with self.subTest(rol=rol, estado=estado):
                    self.preparar(estado)
                    r = self.cancelar(rol)
                    self.assertEqual(r.status_code, 200, r.get_json())
                    aviso = NotificacionModel.query.filter_by(Usuario_idUsuario=1).one()
                    self.assertEqual(aviso.tipo, 'viaje_cancelado')
                    self.assertEqual(aviso.titulo, 'Viaje cancelado')
                    self.assertIn('#2', aviso.mensaje)
                    self.assertIn('Cambio de "plan" & fecha', aviso.mensaje)
                    self.assertFalse(aviso.leida)
                    self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=100).count(), 1)
                    self.push.assert_called_once()
                    self.assertEqual(self.cancelar(rol).status_code, 400)
                    self.assertEqual(NotificacionModel.query.count(), 2)
                    self.push.assert_called_once()

    def test_cancelacion_no_permitida_no_genera_avisos(self):
        for rol in ['admin', 'operador']:
            for estado in ['en curso', 'finalizado', 'cancelado']:
                self.preparar(estado)
                self.assertEqual(self.cancelar(rol).status_code, 400)
                self.assertEqual(NotificacionModel.query.count(), 0)
                self.push.assert_not_called()

    def comprobar_reversion(self):
        viaje = db.session.get(ViajeModel, 2)
        self.assertEqual(viaje.estado, 'aceptado')
        self.assertEqual(viaje.observaciones, 'Observación original')
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'en viaje')
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.assertEqual(ViajeCambioModel.query.count(), 0)
        self.push.assert_not_called()

    def test_fallo_al_crear_aviso_revierte_cancelacion(self):
        for rol in ['admin', 'operador']:
            self.preparar()
            with patch('services.viaje_notificacion_service.NotificacionService.crear', side_effect=RuntimeError('Prueba')), patch('controllers.operador_controller.logger'), patch('controllers.viaje_controller.logger'):
                self.assertEqual(self.cancelar(rol).status_code, 500)
            self.comprobar_reversion()

    def test_fallo_commit_revierte_avisos_y_no_envia_push(self):
        for rol in ['admin', 'operador']:
            self.preparar()
            with patch.object(db.session, 'commit', side_effect=RuntimeError('Prueba')), patch('controllers.operador_controller.logger'), patch('controllers.viaje_controller.logger'):
                self.assertEqual(self.cancelar(rol).status_code, 500)
            self.comprobar_reversion()


    def test_motivo_invalido_no_cancela_ni_genera_avisos(self):
        for rol in ['admin','operador']:
            for motivo in ['A'*182, 'A'*200, "'"*31, None, [], '   ']:
                with self.subTest(rol=rol,motivo=motivo):
                    self.preparar()
                    r = self.cancelar(rol,motivo)
                    self.assertEqual(r.status_code,400,r.get_json())
                    db.session.remove()
                    self.comprobar_reversion()

    def test_motivo_al_limite_cancela_sin_exceder_columna(self):
        for rol in ['admin','operador']:
            for motivo in ['A'*181, "'"*30]:
                self.preparar()
                r = self.cancelar(rol,motivo)
                self.assertEqual(r.status_code,200,r.get_json())
                db.session.remove()
                viaje = db.session.get(ViajeModel,2)
                self.assertEqual(viaje.estado,'cancelado')
                self.assertLessEqual(len(viaje.observaciones),200)
                self.assertEqual(NotificacionModel.query.count(),2)

    def test_dominio_no_muta_si_motivo_excede_limite(self):
        from src.Viaje import Viaje
        self.preparar()
        viaje = Viaje.crear_desde_datos(db.session.get(ViajeModel,2).to_dict())
        self.assertFalse(viaje.cancelar('A'*182))
        self.assertEqual(viaje.estado,'aceptado')
        self.assertEqual(viaje.observaciones,'Observación original')
