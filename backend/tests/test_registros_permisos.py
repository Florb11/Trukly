import unittest
from datetime import date, datetime
from flask_jwt_extended import JWTManager, create_access_token
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from models.viaje_model import ViajeModel
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from routes.registro_ingreso_salida_routes import registro_ingreso_salida_routes


class RegistrosPermisosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-records-authorization-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(registro_ingreso_salida_routes)
        for uid in [1,2,3]:
            db.session.get(UsuarioModel,uid).estado = 'activo'
        db.session.add_all([
            UsuarioModel(id_usuario=77,username='otro_chofer_qa',password='x',nombre='Otro',apellido='Chofer',rol='chofer',estado='activo'),
            ChoferModel(Usuario_idUsuario=77,licencia='LIC7777',legajo='C77',vencimientoLicencia=date(2099,1,1)),
            UsuarioModel(id_usuario=100,username='admin_registros',password='x',nombre='QA',apellido='Admin',rol='admin',estado='activo'),
            AdministradorModel(Usuario_idUsuario=100,legajo='A100'),
            ViajeModel(id_viaje=77,OperadorLogistico_Usuario_idUsuario=2,Chofer_Usuario_idUsuario=77,Camion_id_camion=1,fecha_salida=date(2026,9,1),origen='C',destino='D',estado='finalizado',recorrido=10),
            RegistroIngresoSalidaModel(id_registro=90,Viaje_id_viaje=1,fecha_hora=datetime(2026,9,1,9),tipo_registro='ingreso',observacion='Control del primer chofer'),
            RegistroIngresoSalidaModel(id_registro=91,Viaje_id_viaje=77,fecha_hora=datetime(2026,9,1,10),tipo_registro='ingreso',observacion='Control del segundo chofer'),
        ])
        db.session.commit()
        cls.client = cls.fixture.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def get(self, ruta, uid=None, rol=None):
        headers = {} if uid is None else {'Authorization':'Bearer '+create_access_token(identity=str(uid),additional_claims={'rol':rol})}
        return self.client.get('/api/registros-ingreso-salida'+ruta,headers=headers)

    def test_chofer_solo_lista_y_consulta_sus_controles(self):
        for uid, propio, ajeno in [(1,90,91),(77,91,90)]:
            r = self.get('',uid,'chofer')
            self.assertEqual(r.status_code,200)
            self.assertEqual([fila['id_registro'] for fila in r.get_json()],[propio])
            self.assertEqual(self.get('/'+str(propio),uid,'chofer').status_code,200)
            prohibido = self.get('/'+str(ajeno),uid,'chofer')
            inexistente = self.get('/999',uid,'chofer')
            self.assertEqual(prohibido.status_code,404)
            self.assertEqual(prohibido.get_json(),inexistente.get_json())

    def test_admin_y_operador_consultan_todos(self):
        for uid, rol in [(100,'admin'),(2,'operador')]:
            r = self.get('',uid,rol)
            self.assertEqual(r.status_code,200)
            self.assertEqual({fila['id_registro'] for fila in r.get_json()},{90,91})
            for registro in [90,91]:
                self.assertEqual(self.get('/'+str(registro),uid,rol).status_code,200)

    def test_sin_sesion_y_mecanico_no_acceden(self):
        for ruta in ['', '/90']:
            self.assertEqual(self.get(ruta).status_code,401)
            self.assertEqual(self.get(ruta,3,'mecanico').status_code,403)

    def test_reasignacion_quita_acceso_al_chofer_anterior(self):
        viaje = db.session.get(ViajeModel,77)
        viaje.Chofer_Usuario_idUsuario = 1
        db.session.commit()
        try:
            self.assertEqual(self.get('',77,'chofer').get_json(),[])
            self.assertEqual(self.get('/91',77,'chofer').status_code,404)
            self.assertEqual(self.get('/91',1,'chofer').status_code,200)
        finally:
            viaje.Chofer_Usuario_idUsuario = 77
            db.session.commit()
