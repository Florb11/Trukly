import unittest

from flask_jwt_extended import JWTManager, create_access_token

from routes.administrador_routes import administrador_routes
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from models.viaje_model import ViajeModel
from models.camion_model import CamionModel
from routes.camion_routes import camion_routes
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
        cls.fixture.app.register_blueprint(camion_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.get(CamionModel, 1).estado = "en viaje"
        db.session.get(ViajeModel, 2).estado = "en curso"
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
        db.session.get(ViajeModel, 2).estado = "finalizado"
        db.session.commit()
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

    def test_viajes_activos_bloquean_desactivar_y_dejar_pendiente(self):
        for viaje_estado in ['pendiente', 'aceptado', 'en curso']:
            db.session.get(ViajeModel, 2).estado = viaje_estado
            db.session.commit()
            for ruta, datos in [('/api/admin/usuarios/1/desactivar', None),
                                ('/api/admin/usuarios/1', {'estado':'inactivo', 'nombre':'No guardar'}),
                                ('/api/admin/usuarios/1', {'estado':'pendiente', 'nombre':'No guardar'})]:
                with self.subTest(viaje=viaje_estado, ruta=ruta, datos=datos):
                    nombre = db.session.get(UsuarioModel, 1).nombre
                    r = self.cliente.put(ruta, json=datos, headers=self.headers)
                    self.assertEqual(r.status_code, 409, r.get_json())
                    self.assertEqual(db.session.get(UsuarioModel, 1).estado, 'activo')
                    self.assertEqual(db.session.get(UsuarioModel, 1).nombre, nombre)
                    self.assertEqual(db.session.get(ViajeModel, 2).estado, viaje_estado)
                    self.assertIn('regreso por QR' if viaje_estado=='en curso' else 'reasignalos', r.get_json()['mensaje'])

    def test_boton_desactiva_con_viajes_cerrados(self):
        for estado in ['finalizado', 'cancelado']:
            db.session.get(ViajeModel, 2).estado = estado
            db.session.get(UsuarioModel, 1).estado = 'activo'
            db.session.commit()
            r = self.cliente.put('/api/admin/usuarios/1/desactivar', headers=self.headers)
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(db.session.get(UsuarioModel, 1).estado, 'inactivo')

    def test_editar_datos_personales_de_chofer_en_viaje_sigue_permitido(self):
        r = self.cliente.put('/api/admin/usuarios/1', headers=self.headers,
                             json={'nombre':'Actualizado', 'estado':'activo'})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(db.session.get(UsuarioModel, 1).estado, 'activo')
        self.assertEqual(db.session.get(ViajeModel, 2).estado, 'en curso')

    def test_camion_con_viaje_activo_no_se_desactiva_por_ninguna_ruta(self):
        for estado in ['pendiente', 'aceptado', 'en curso']:
            db.session.get(ViajeModel, 2).estado = estado
            db.session.commit()
            for ruta in ['/api/admin/camiones/1/estado', '/api/admin/camiones/1']:
                with self.subTest(estado=estado, ruta=ruta):
                    camion = db.session.get(CamionModel, 1)
                    marca_original = camion.marca
                    r = self.cliente.put(ruta, headers=self.headers,
                        json={'estado':'inactivo', 'marca':'No guardar'})
                    self.assertEqual(r.status_code, 409, r.get_json())
                    self.assertEqual(camion.estado, 'en viaje')
                    self.assertEqual(camion.marca, marca_original)
                    self.assertEqual(db.session.get(ViajeModel, 2).estado, estado)
                    self.assertIn('regreso por QR' if estado=='en curso' else 'reasigná', r.get_json()['mensaje'])

    def test_camion_con_viajes_cerrados_se_puede_desactivar(self):
        for estado in ['finalizado', 'cancelado']:
            db.session.get(ViajeModel, 2).estado = estado
            for ruta in ['/api/admin/camiones/1/estado', '/api/admin/camiones/1']:
                db.session.get(CamionModel, 1).estado = 'disponible'
                db.session.commit()
                r = self.cliente.put(ruta, headers=self.headers, json={'estado':'inactivo'})
                self.assertEqual(r.status_code, 200, r.get_json())
                self.assertEqual(db.session.get(CamionModel, 1).estado, 'inactivo')

    def test_camion_en_viaje_permite_editar_datos_sin_desactivar(self):
        r = self.cliente.put('/api/admin/camiones/1', headers=self.headers,
                             json={'modelo':'Actualizado'})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(db.session.get(CamionModel, 1).modelo, 'Actualizado')
        self.assertEqual(db.session.get(CamionModel, 1).estado, 'en viaje')
        self.assertEqual(db.session.get(ViajeModel, 2).estado, 'en curso')
