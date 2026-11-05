import unittest
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token

from db_instance import db
from models.administrador_model import AdministradorModel
from models.operador_model import OperadorModel
from models.usuario_model import UsuarioModel
from routes.operador_routes import operador_routes


class OperadoresPermisosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-operator-permissions-secret'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(operador_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        for uid in [1,2,3]:
            db.session.get(UsuarioModel,uid).estado = 'activo'
        db.session.add_all([
            UsuarioModel(id_usuario=100, username='admin_operadores', password='x', nombre='QA', apellido='Admin', rol='admin', estado='activo'),
            AdministradorModel(Usuario_idUsuario=100, legajo='A100'),
            UsuarioModel(id_usuario=77, username='otro_operador', password='x', nombre='Otro', apellido='Operador', rol='operador', estado='activo'),
            OperadorModel(Usuario_idUsuario=77, legajo='O77', sector='Logística'),
            UsuarioModel(id_usuario=78, username='operador_sin_datos', password='x', nombre='Nuevo', apellido='Operador', rol='operador', estado='pendiente'),
        ])
        db.session.commit()
        self.client = self.fixture.app.test_client()
        self.datos = {'Usuario_idUsuario':78, 'Legajo':'O78', 'Sector':'Logística'}

    def tearDown(self):
        db.session.rollback()
        OperadorModel.query.filter(OperadorModel.Usuario_idUsuario.in_([77,78])).delete()
        AdministradorModel.query.filter_by(Usuario_idUsuario=100).delete()
        UsuarioModel.query.filter(UsuarioModel.id_usuario.in_([77,78,100])).delete()
        db.session.commit()
        db.session.remove()

    def headers(self, uid, rol):
        return {'Authorization':'Bearer '+create_access_token(identity=str(uid), additional_claims={'rol':rol})}

    def test_sin_sesion_no_consulta_ni_crea_operadores(self):
        for metodo, ruta in [('GET','/api/operador'), ('GET','/api/operador/2'), ('POST','/api/operador')]:
            r = self.client.open(ruta, method=metodo, json=self.datos if metodo=='POST' else None)
            self.assertEqual(r.status_code,401,r.get_json())
        self.assertIsNone(db.session.get(OperadorModel,78))

    def test_consultas_permitidas_segun_rol_y_propietario(self):
        for uid, rol, lista, detalle in [(100,'admin',200,200), (2,'operador',403,200),
                                        (1,'chofer',403,403), (3,'mecanico',403,403)]:
            h = self.headers(uid,rol)
            self.assertEqual(self.client.get('/api/operador',headers=h).status_code,lista)
            self.assertEqual(self.client.get('/api/operador/2',headers=h).status_code,detalle)
        self.assertEqual(self.client.get('/api/operador/77',headers=self.headers(2,'operador')).status_code,403)
        self.assertEqual(self.client.get('/api/operador/77',headers=self.headers(100,'admin')).status_code,200)

    def test_rol_falso_y_cuentas_inactivas_no_evaden_permisos(self):
        self.assertEqual(self.client.get('/api/operador',headers=self.headers(1,'admin')).status_code,403)
        self.assertEqual(self.client.post('/api/operador',headers=self.headers(1,'admin'),json=self.datos).status_code,403)
        for uid, rol in [(100,'admin'), (2,'operador')]:
            db.session.get(UsuarioModel,uid).estado = 'inactivo'
            db.session.commit()
            self.assertEqual(self.client.get('/api/operador/2',headers=self.headers(uid,rol)).status_code,403)
        self.assertIsNone(db.session.get(OperadorModel,78))

    def test_solo_admin_completa_perfil_y_no_duplica(self):
        for uid, rol in [(1,'chofer'), (2,'operador'), (3,'mecanico')]:
            self.assertEqual(self.client.post('/api/operador',headers=self.headers(uid,rol),json=self.datos).status_code,403)
        h = self.headers(100,'admin')
        r = self.client.post('/api/operador',headers=h,json=self.datos)
        self.assertEqual(r.status_code,201,r.get_json())
        self.assertEqual(db.session.get(OperadorModel,78).sector,'Logística')
        self.assertEqual(db.session.get(UsuarioModel,78).estado,'pendiente')
        self.assertEqual(self.client.post('/api/operador',headers=h,json=self.datos).status_code,409)

    def test_alta_valida_rol_del_usuario_y_campos_sin_dejar_datos(self):
        casos = [(None,400), ({},400), ({**self.datos,'Usuario_idUsuario':True},400),
                 ({**self.datos,'Usuario_idUsuario':1.5},400), ({**self.datos,'Usuario_idUsuario':1},400),
                 ({**self.datos,'Usuario_idUsuario':999},404), ({**self.datos,'Legajo':''},400),
                 ({**self.datos,'Sector':'x'*46},400), ({**self.datos,'Legajo':'x'*46},400)]
        for datos, codigo in casos:
            r = self.client.post('/api/operador',headers=self.headers(100,'admin'),json=datos)
            self.assertEqual(r.status_code,codigo,r.get_json())
            self.assertIsNone(db.session.get(OperadorModel,78))
            self.assertIsNone(db.session.get(OperadorModel,1))

    def test_fallo_de_guardado_revierte_el_alta(self):
        with patch.object(db.session,'commit',side_effect=RuntimeError('Prueba')),patch('controllers.operador_controller.logger'):
            r = self.client.post('/api/operador',headers=self.headers(100,'admin'),json=self.datos)
        self.assertEqual(r.status_code,500,r.get_json())
        self.assertIsNone(db.session.get(OperadorModel,78))
        self.assertEqual(db.session.get(UsuarioModel,78).rol,'operador')
