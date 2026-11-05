import unittest

from flask_jwt_extended import JWTManager, create_access_token

from routes.administrador_routes import administrador_routes
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from src.Administrador import Administrador
from src.Usuario import Usuario


class AdminPropiaCuentaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-admin-self-protection-secret'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(administrador_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.add(UsuarioModel(id_usuario=100, username='admin_qa', email='admin@example.invalid',
            password='x', nombre='QA', apellido='Admin', estado='activo', rol='admin'))
        db.session.add(AdministradorModel(Usuario_idUsuario=100, legajo='A100'))
        chofer = db.session.get(UsuarioModel, 1)
        chofer.email = 'chofer@example.invalid'
        chofer.estado = 'activo'
        db.session.get(ChoferModel, 1).licencia = 'LIC12345'
        db.session.commit()
        token = create_access_token(identity='100', additional_claims={'rol':'admin'})
        self.headers = {'Authorization':'Bearer '+token}
        self.cliente = self.fixture.app.test_client()

    def tearDown(self):
        db.session.rollback()
        AdministradorModel.query.filter_by(Usuario_idUsuario=100).delete()
        UsuarioModel.query.filter_by(id_usuario=100).delete()
        db.session.commit()
        db.session.remove()

    def test_edicion_no_desactiva_ni_deja_pendiente_al_admin_actual(self):
        for estado in ['inactivo', 'pendiente']:
            r = self.cliente.put('/api/admin/usuarios/100', json={'estado':estado, 'nombre':'No guardar'}, headers=self.headers)
            self.assertEqual(r.status_code, 400, r.get_json())
            self.assertIn('propia cuenta', r.get_json()['mensaje'])
            db.session.refresh(db.session.get(UsuarioModel, 100))
            self.assertEqual(db.session.get(UsuarioModel, 100).estado, 'activo')
            self.assertEqual(db.session.get(UsuarioModel, 100).nombre, 'QA')
            self.assertEqual(self.cliente.get('/api/admin/usuarios', headers=self.headers).status_code, 200)

    def test_boton_dedicado_sigue_bloqueando_autodesactivacion(self):
        r = self.cliente.put('/api/admin/usuarios/100/desactivar', headers=self.headers)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(db.session.get(UsuarioModel, 100).estado, 'activo')

    def test_permite_editar_datos_propios_con_estado_activo(self):
        r = self.cliente.put('/api/admin/usuarios/100', json={'nombre':'Actualizado', 'estado':'activo'}, headers=self.headers)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(db.session.get(UsuarioModel, 100).nombre, 'Actualizado')
        self.assertEqual(db.session.get(UsuarioModel, 100).estado, 'activo')

    def test_permite_desactivar_y_reactivar_otro_usuario(self):
        for estado in ['inactivo', 'activo']:
            r = self.cliente.put('/api/admin/usuarios/1', json={'estado':estado}, headers=self.headers)
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(db.session.get(UsuarioModel, 1).estado, estado)

    def test_regla_de_dominio_tambien_protege_cuenta_propia(self):
        admin = Administrador.crear_desde_datos({'id_usuario':100, 'estado':'activo', 'rol':'admin'})
        usuario = Usuario.crear_desde_datos({'id_usuario':100, 'estado':'activo', 'rol':'admin',
                                           'username':'qa', 'email':'qa@example.invalid', 'nombre':'QA', 'apellido':'Prueba'})
        self.assertFalse(admin.modificar_usuario(usuario, 'qa', 'qa@example.invalid', 'Otro', 'Nombre', 'inactivo'))
        self.assertEqual(usuario.estado, 'activo')
        self.assertEqual(usuario.nombre, 'QA')
