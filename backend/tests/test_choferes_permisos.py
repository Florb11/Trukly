import unittest
from datetime import date
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token

from db_instance import db
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from models.usuario_model import UsuarioModel
from routes.chofer_routes import chofer_routes


class ChoferesPermisosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-driver-permissions-secret'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(chofer_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        for uid in [1, 2, 3]:
            db.session.get(UsuarioModel, uid).estado = 'activo'
        db.session.add_all([
            UsuarioModel(id_usuario=100, username='admin_permisos', password='x', nombre='QA', apellido='Admin', rol='admin', estado='activo'),
            AdministradorModel(Usuario_idUsuario=100, legajo='A100'),
            UsuarioModel(id_usuario=77, username='otro_chofer', password='x', nombre='Otro', apellido='Chofer', rol='chofer', estado='activo'),
            ChoferModel(Usuario_idUsuario=77, licencia='LIC0077', legajo='C77', vencimientoLicencia=date(2099,1,1)),
            UsuarioModel(id_usuario=78, username='chofer_sin_datos', password='x', nombre='Nuevo', apellido='Chofer', rol='chofer', estado='pendiente'),
        ])
        db.session.commit()
        self.client = self.fixture.app.test_client()
        self.datos = {'Usuario_idUsuario':78, 'licencia':'LIC0078', 'legajo':'C78', 'vencimientoLicencia':'2099-01-01'}

    def tearDown(self):
        db.session.rollback()
        ChoferModel.query.filter(ChoferModel.Usuario_idUsuario.in_([77,78])).delete()
        AdministradorModel.query.filter_by(Usuario_idUsuario=100).delete()
        UsuarioModel.query.filter(UsuarioModel.id_usuario.in_([77,78,100])).delete()
        db.session.commit()
        db.session.remove()

    def headers(self, uid, rol):
        return {'Authorization':'Bearer '+create_access_token(identity=str(uid), additional_claims={'rol':rol})}

    def test_sin_sesion_no_consulta_ni_crea_datos(self):
        for metodo, ruta in [('GET','/api/choferes'), ('GET','/api/choferes/1'), ('POST','/api/choferes')]:
            r = self.client.open(ruta, method=metodo, json=self.datos if metodo=='POST' else None)
            self.assertEqual(r.status_code, 401, r.get_json())
        self.assertIsNone(db.session.get(ChoferModel,78))

    def test_matriz_de_consulta_por_rol(self):
        for uid, rol, lista, detalle in [(100,'admin',200,200), (2,'operador',200,200),
                                        (1,'chofer',403,200), (3,'mecanico',403,403)]:
            h = self.headers(uid,rol)
            self.assertEqual(self.client.get('/api/choferes',headers=h).status_code,lista)
            self.assertEqual(self.client.get('/api/choferes/1',headers=h).status_code,detalle)
        self.assertEqual(self.client.get('/api/choferes/77',headers=self.headers(1,'chofer')).status_code,403)

    def test_cuentas_inactivas_y_rol_falso_no_evaden_permisos(self):
        h = self.headers(1,'admin')
        self.assertEqual(self.client.get('/api/choferes',headers=h).status_code,403)
        self.assertEqual(self.client.post('/api/choferes',headers=h,json=self.datos).status_code,403)
        for uid, rol in [(100,'admin'), (2,'operador'), (1,'chofer')]:
            db.session.get(UsuarioModel,uid).estado = 'inactivo'
            db.session.commit()
            self.assertEqual(self.client.get('/api/choferes/1',headers=self.headers(uid,rol)).status_code,403)
        self.assertIsNone(db.session.get(ChoferModel,78))

    def test_solo_admin_puede_completar_alta_antigua(self):
        for uid, rol in [(1,'chofer'), (2,'operador'), (3,'mecanico')]:
            r = self.client.post('/api/choferes',headers=self.headers(uid,rol),json=self.datos)
            self.assertEqual(r.status_code,403,r.get_json())
        r = self.client.post('/api/choferes',headers=self.headers(100,'admin'),json=self.datos)
        self.assertEqual(r.status_code,201,r.get_json())
        self.assertEqual(db.session.get(ChoferModel,78).vencimientoLicencia,date(2099,1,1))
        self.assertEqual(self.client.post('/api/choferes',headers=self.headers(100,'admin'),json=self.datos).status_code,409)

    def test_alta_rechaza_usuario_de_otro_rol_o_inexistente(self):
        for uid, esperado in [(2,400),(999,404)]:
            r = self.client.post('/api/choferes',headers=self.headers(100,'admin'),json={**self.datos,'Usuario_idUsuario':uid})
            self.assertEqual(r.status_code,esperado,r.get_json())
        self.assertIsNone(db.session.get(ChoferModel,2))

    def test_alta_rechaza_datos_invalidos_sin_guardar(self):
        casos = [None, {}, {**self.datos,'Usuario_idUsuario':True}, {**self.datos,'Usuario_idUsuario':1.5},
                 {**self.datos,'licencia':'abc'}, {**self.datos,'legajo':'x'*51},
                 {**self.datos,'vencimientoLicencia':'fecha inválida'}, {**self.datos,'vencimientoLicencia':'2000-01-01'}]
        for datos in casos:
            r = self.client.post('/api/choferes',headers=self.headers(100,'admin'),json=datos)
            self.assertEqual(r.status_code,400,r.get_json())
            self.assertIsNone(db.session.get(ChoferModel,78))

    def test_alta_revierte_si_falla_el_guardado(self):
        with patch.object(db.session,'commit',side_effect=RuntimeError('Prueba')),patch('controllers.chofer_controller.logger'):
            r = self.client.post('/api/choferes',headers=self.headers(100,'admin'),json=self.datos)
        self.assertEqual(r.status_code,500,r.get_json())
        self.assertIsNone(db.session.get(ChoferModel,78))
        self.assertEqual(db.session.get(UsuarioModel,78).rol,'chofer')
