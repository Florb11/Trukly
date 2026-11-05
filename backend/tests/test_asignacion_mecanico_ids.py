import unittest
from unittest.mock import patch
from flask_jwt_extended import JWTManager, create_access_token
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.reporte_model import ReporteModel
from models.notificacion_model import NotificacionModel
from models.camion_model import CamionModel
from routes.reporte_routes import reporte_routes


class AsignacionMecanicoIdsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-mechanic-identifiers-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(reporte_routes)
        for uid in [2,3]:
            db.session.get(UsuarioModel,uid).estado = 'activo'
        db.session.add(UsuarioModel(id_usuario=100,username='admin_ids',password='x',nombre='QA',apellido='Admin',estado='activo',rol='admin'))
        db.session.add(AdministradorModel(Usuario_idUsuario=100,legajo='A100'))
        db.session.commit()
        cls.client = cls.fixture.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        emisor = patch('services.notificacion_service.NotificacionService.enviar_push_pendientes')
        self.push = emisor.start()
        self.addCleanup(emisor.stop)
        self.preparar()

    def tearDown(self):
        db.session.rollback()
        db.session.info.pop('push_pendientes',None)
        db.session.remove()

    def preparar(self):
        r = db.session.get(ReporteModel,1)
        r.estado, r.Mecanico_Usuario_idUsuario = 'pendiente', None
        db.session.get(CamionModel,1).estado = 'disponible'
        NotificacionModel.query.delete()
        db.session.commit()
        self.push.reset_mock()

    def asignar(self, rol, valor=None, cuerpo=None):
        uid = '100' if rol == 'admin' else '2'
        token = create_access_token(identity=uid,additional_claims={'rol':rol})
        ruta = '/api/reportes/1/estado' if rol == 'admin' else '/api/reportes/1/asignar-mecanico'
        datos = {'estado':'en revision','Mecanico_Usuario_idUsuario':valor} if cuerpo is None else cuerpo
        return self.client.put(ruta,json=datos,headers={'Authorization':'Bearer '+token})

    def test_ids_invalidos_no_cambian_reporte_camion_ni_avisos(self):
        invalidos = [3.9,3.0,True,False,0,-3,None,[],{},'3.9','3e0','٣','³',2147483648,'9'*5000]
        for rol in ['admin','operador']:
            for valor in invalidos:
                with self.subTest(rol=rol,valor=str(valor)[:25]):
                    r = self.asignar(rol,valor)
                    self.assertEqual(r.status_code,400,r.get_json())
                    db.session.remove()
                    reporte = db.session.get(ReporteModel,1)
                    self.assertEqual(reporte.estado,'pendiente')
                    self.assertIsNone(reporte.Mecanico_Usuario_idUsuario)
                    self.assertEqual(db.session.get(CamionModel,1).estado,'disponible')
                    self.assertEqual(NotificacionModel.query.count(),0)
                    self.push.assert_not_called()

    def test_ids_enteros_y_selector_en_texto_siguen_funcionando(self):
        for rol in ['admin','operador']:
            for valor in [3,'3',' 3 ']:
                self.preparar()
                r = self.asignar(rol,valor)
                self.assertEqual(r.status_code,200,r.get_json())
                db.session.remove()
                reporte = db.session.get(ReporteModel,1)
                self.assertEqual((reporte.estado,reporte.Mecanico_Usuario_idUsuario),('en revision',3))
                self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=3).count(),1)

    def test_cuerpos_invalidos_rechazados(self):
        for rol in ['admin','operador']:
            for cuerpo in [[],['x'],'texto',42]:
                self.assertEqual(self.asignar(rol,cuerpo=cuerpo).status_code,400)
