import unittest
from html import escape
from flask_jwt_extended import JWTManager, create_access_token
from db_instance import db
from models.usuario_model import UsuarioModel
from routes.perfil_routes import perfil_routes


class PerfilValidacionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'profile-validation-test-secret-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(perfil_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        u = db.session.get(UsuarioModel, 1)
        u.estado = 'activo'
        u.firebase_uid = None
        u.nombre, u.apellido, u.email = 'Ana', 'Garcia', 'ana@example.invalid'
        db.session.commit()
        self.client = self.fixture.app.test_client()
        self.headers = {'Authorization': 'Bearer ' + create_access_token(identity='1', additional_claims={'rol': 'chofer'})}

    def put(self, datos):
        return self.client.put('/api/perfil', json=datos, headers=self.headers)

    def test_invalidos_no_guardan_cambios_parciales(self):
        for campo, valor in [('nombre', 'A'*101), ('apellido', 'B'*101),
                             ('nombre', "'"*21), ('nombre', []), ('apellido', None),
                             ('nombre', '  '), ('email', 'sin-arroba'),
                             ('email', 'a@b'), ('email', 'a '*80+'@b.com'),
                             ('email', 'a'*145+'@b.com'), ('email', [])]:
            with self.subTest(campo=campo, valor=valor):
                datos = {'nombre': 'Cambio', 'apellido': 'Cambio', 'email': 'nuevo@example.invalid'}
                datos[campo] = valor
                r = self.put(datos)
                self.assertEqual(r.status_code, 400, r.get_json())
                db.session.remove()
                u = db.session.get(UsuarioModel,1)
                self.assertEqual((u.nombre,u.apellido,u.email), ('Ana','Garcia','ana@example.invalid'))

    def test_limites_validos_y_caracteres_codificados(self):
        for nombre in ['A'*100, "'"*16]:
            r = self.put({'nombre': nombre, 'apellido': 'B'*100, 'email': 'C'*140+'@x.invalid'})
            self.assertEqual(r.status_code,200,r.get_json())
            self.assertEqual(r.get_json()['perfil']['nombre'],nombre)
            db.session.remove()
            self.assertEqual(db.session.get(UsuarioModel,1).nombre,escape(nombre))

    def test_correo_duplicado_y_firebase_conservan_cuenta(self):
        u2 = db.session.get(UsuarioModel,2)
        u2.email = 'ocupado@example.invalid'
        db.session.commit()
        self.assertEqual(self.put({'nombre':'Cambio','email':'OCUPADO@example.invalid'}).status_code,409)
        db.session.remove()
        u = db.session.get(UsuarioModel,1)
        self.assertEqual(u.nombre,'Ana')
        u.firebase_uid = 'test-profile-firebase'
        db.session.commit()
        self.assertEqual(self.put({'email':'nuevo@example.invalid'}).status_code,409)
        db.session.remove()
        self.assertEqual(db.session.get(UsuarioModel,1).email,'ana@example.invalid')
        self.assertEqual(self.put({'nombre':'Nuevo'}).status_code,200)

    def test_cuerpo_invalido(self):
        for cuerpo in [[], ['x'], 'texto', 42]:
            self.assertEqual(self.put(cuerpo).status_code,400)



    def test_licencia_y_legajo_respetan_limites_sin_cambios_parciales(self):
        from models.chofer_model import ChoferModel
        chofer = db.session.get(ChoferModel,1)
        original = (chofer.licencia,chofer.legajo,chofer.vencimientoLicencia)
        for campo, valor in [("licencia","A"*51),("legajo","B"*51),("legajo","'"*9)]:
            datos = {"nombre":"No guardar","licencia":"LIC12345","legajo":"C1","vencimientoLicencia":"2099-01-01"}
            datos[campo] = valor
            r = self.put(datos)
            self.assertEqual(r.status_code,400,r.get_json())
            db.session.remove()
            chofer = db.session.get(ChoferModel,1)
            self.assertEqual((chofer.licencia,chofer.legajo,chofer.vencimientoLicencia),original)
            self.assertEqual(db.session.get(UsuarioModel,1).nombre,"Ana")
        r = self.put({"licencia":"A"*50,"legajo":"B"*50,"vencimientoLicencia":"2099-01-01"})
        self.assertEqual(r.status_code,200,r.get_json())
        db.session.remove()
        chofer = db.session.get(ChoferModel,1)
        self.assertEqual((chofer.licencia,chofer.legajo),("A"*50,"B"*50))

    def test_validadores_compartidos_rechazan_legajo_y_licencia_largos(self):
        from controllers.auth_controller import AuthController
        from controllers.admin_usuarios_controller import AdminUsuariosController
        from src.Chofer import Chofer
        datos = {"licencia":"A"*50,"legajo":"B"*50,"vencimientoLicencia":"2099-01-01"}
        for crear in [AuthController._crear_validador_datos_chofer, AdminUsuariosController._crear_validador_datos_chofer]:
            self.assertTrue(crear().validar(datos)[0])
            for campo in ["licencia","legajo"]:
                self.assertFalse(crear().validar({**datos,campo:"A"*51})[0])
        self.assertTrue(Chofer.validar_legajo("'"*8)[0])
