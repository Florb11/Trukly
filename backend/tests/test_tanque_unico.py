import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.camion_model import CamionModel
from controllers.camion_controller import CamionController
from routes.camion_routes import camion_routes


class TanqueUnicoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-unique-tank-secret-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(camion_routes)
        db.session.add(UsuarioModel(id_usuario=100,username='admin_tanques',password='x',nombre='QA',apellido='Admin',rol='admin',estado='activo'))
        db.session.add(AdministradorModel(Usuario_idUsuario=100,legajo='A100'))
        db.session.add(CamionModel(id_camion=90,matricula='TANQUE90',marca='Marca',modelo='QA',capacidad_carga=1000,nroTanque=90,estado='disponible'))
        db.session.commit()
        cls.client = cls.fixture.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        self.headers = {'Authorization':'Bearer '+create_access_token(identity='100',additional_claims={'rol':'admin'})}

    def tearDown(self):
        db.session.rollback()
        CamionModel.query.filter(CamionModel.id_camion.notin_([1,90])).delete()
        camion = db.session.get(CamionModel,90)
        camion.nroTanque, camion.marca = 90,'Marca'
        db.session.get(CamionModel,1).estado = 'disponible'
        db.session.commit()
        db.session.remove()

    def datos(self, tanque):
        return {'matricula':'NUEVO99','marca':'Marca','modelo':'QA','capacidad_carga':1000,'nroTanque':tanque,'estado':'disponible'}

    def test_creacion_rechaza_numero_usado_incluso_inactivo(self):
        for estado in ['disponible','inactivo']:
            db.session.get(CamionModel,1).estado = estado
            db.session.commit()
            for valor in [1,'01',' 1 ',1.0]:
                r = self.client.post('/api/admin/camiones',json=self.datos(valor),headers=self.headers)
                self.assertEqual(r.status_code,409,r.get_json())
                self.assertIn('número de tanque',r.get_json()['mensaje'])
                db.session.remove()
                self.assertEqual(CamionModel.query.count(),2)

    def test_edicion_no_pisa_datos_con_numero_duplicado_y_permite_el_propio(self):
        r = self.client.put('/api/admin/camiones/90',json={'nroTanque':1,'marca':'No guardar'},headers=self.headers)
        self.assertEqual(r.status_code,409,r.get_json())
        db.session.remove()
        camion = db.session.get(CamionModel,90)
        self.assertEqual((camion.nroTanque,camion.marca),(90,'Marca'))
        for datos in [{'nroTanque':'90','marca':'Actualizada'},{'modelo':'Otro'}]:
            r = self.client.put('/api/admin/camiones/90',json=datos,headers=self.headers)
            self.assertEqual(r.status_code,200,r.get_json())

    def test_numero_libre_se_puede_crear_y_cambiar(self):
        r = self.client.post('/api/admin/camiones',json=self.datos(2),headers=self.headers)
        self.assertEqual(r.status_code,201,r.get_json())
        uid = r.get_json()['camion']['id_camion']
        r = self.client.put('/api/admin/camiones/'+str(uid),json={'nroTanque':3},headers=self.headers)
        self.assertEqual(r.status_code,200,r.get_json())
        self.assertEqual(r.get_json()['camion']['nroTanque'],3)

    def test_base_impide_duplicados_aunque_se_salte_preconsulta(self):
        with patch.object(CamionController,'_tanque_duplicado',return_value=False):
            r = self.client.post('/api/admin/camiones',json=self.datos(1),headers=self.headers)
            self.assertEqual(r.status_code,409,r.get_json())
            r = self.client.put('/api/admin/camiones/90',json={'nroTanque':1,'marca':'No guardar'},headers=self.headers)
            self.assertEqual(r.status_code,409,r.get_json())
        db.session.remove()
        self.assertEqual(CamionModel.query.count(),2)
        self.assertEqual(db.session.get(CamionModel,90).nroTanque,90)
        self.assertEqual(db.session.get(CamionModel,90).marca,'Marca')


class MigracionTanqueUnicoTest(unittest.TestCase):
    def setUp(self):
        ruta = Path(__file__).resolve().parents[1]/'database'/'migrations'/'2026_11_05_tanque_unico.py'
        spec = importlib.util.spec_from_file_location('migracion_tanque_unico',ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        self.migrar = modulo.migrar
        self.engine = create_engine('sqlite:///:memory:')
        with self.engine.begin() as conn:
            conn.execute(text('CREATE TABLE Camion (id_camion INTEGER PRIMARY KEY, nroTanque INTEGER NOT NULL, estado TEXT)'))
            conn.execute(text("INSERT INTO Camion VALUES (1,1,'disponible'), (2,2,'inactivo')"))

    def tearDown(self):
        self.engine.dispose()

    def test_comprobacion_no_modifica_y_aplicar_es_idempotente(self):
        self.migrar(self.engine)
        self.assertEqual(inspect(self.engine).get_indexes('Camion'),[])
        self.migrar(self.engine,True)
        self.migrar(self.engine,True)
        self.assertTrue(inspect(self.engine).get_indexes('Camion')[0]['unique'])
        with self.assertRaises(IntegrityError), self.engine.begin() as conn:
            conn.execute(text("INSERT INTO Camion VALUES (3,1,'disponible')"))

    def test_duplicados_impiden_migrar_sin_renumerar_datos(self):
        with self.engine.begin() as conn:
            conn.execute(text('UPDATE Camion SET nroTanque=1 WHERE id_camion=2'))
        for aplicar in [False,True]:
            with self.assertRaisesRegex(ValueError,'tanque 1: camiones 1, 2'):
                self.migrar(self.engine,aplicar)
        with self.engine.connect() as conn:
            self.assertEqual(conn.execute(text('SELECT nroTanque FROM Camion ORDER BY id_camion')).scalars().all(),[1,1])
        self.assertEqual(inspect(self.engine).get_indexes('Camion'),[])
