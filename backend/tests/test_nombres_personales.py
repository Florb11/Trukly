import unittest
from datetime import date
from html import escape
from types import SimpleNamespace
from unittest.mock import patch

from flask_jwt_extended import JWTManager, create_access_token

from db_instance import db
from extensions import bcrypt
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel
from routes.administrador_routes import administrador_routes
from routes.auth_routes import auth_routes
from routes.notificacion_routes import notificacion_routes
from routes.operador_routes import operador_routes
from routes.perfil_routes import perfil_routes
from routes.reporte_routes import reporte_routes
from routes.viaje_routes import viaje_routes
from services.horas_viaje_service import horas_por_chofer
from services.notificacion_service import NotificacionService


class NombresPersonalesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-personal-names-secret-key'
        JWTManager(cls.fixture.app)
        for blueprint in [administrador_routes, auth_routes, notificacion_routes, operador_routes,
                          perfil_routes, reporte_routes, viaje_routes]:
            cls.fixture.app.register_blueprint(blueprint)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        self.nombres = {1: ('María', "D'Amico"), 2: ('Juan', "O'Connor"), 3: ('Luz & Sol', "D'Ávila")}
        for uid, (nombre, apellido) in self.nombres.items():
            usuario = db.session.get(UsuarioModel, uid)
            usuario.nombre, usuario.apellido = escape(nombre), escape(apellido)
            usuario.estado = 'activo'
        usuario = db.session.get(UsuarioModel,1)
        usuario.email = 'chofer@example.invalid'
        usuario.firebase_uid = None
        db.session.get(ChoferModel,1).licencia = 'LIC12345'
        db.session.get(ChoferModel,1).vencimientoLicencia = date(2099,1,1)
        db.session.add(UsuarioModel(id_usuario=100, username='admin_nombres', password='x',
            nombre='QA', apellido='Admin', rol='admin', estado='activo'))
        db.session.add(AdministradorModel(Usuario_idUsuario=100,legajo='A100'))
        db.session.commit()
        self.client = self.fixture.app.test_client()

    def tearDown(self):
        from models.viaje_cambio_model import ViajeCambioModel
        db.session.rollback()
        NotificacionModel.query.delete()
        ViajeCambioModel.query.delete()
        AdministradorModel.query.filter_by(Usuario_idUsuario=100).delete()
        UsuarioModel.query.filter_by(id_usuario=100).delete()
        db.session.commit()
        db.session.info.pop('push_pendientes', None)

    def headers(self, uid, rol):
        return {'Authorization':'Bearer '+create_access_token(identity=str(uid),additional_claims={'rol':rol})}

    def get(self, ruta, uid=2, rol='operador'):
        r = self.client.get(ruta,headers=self.headers(uid,rol))
        self.assertEqual(r.status_code,200,r.get_json())
        return r.get_json()

    def test_perfil_y_listado_admin_muestran_apostrofes_y_tildes(self):
        perfil = self.get('/api/perfil',1,'chofer')['perfil']
        self.assertEqual((perfil['nombre'],perfil['apellido']),self.nombres[1])
        usuarios = self.get('/api/admin/usuarios',100,'admin')['usuarios']
        for uid, esperado in self.nombres.items():
            datos = next(u for u in usuarios if u['id_usuario']==uid)
            self.assertEqual((datos['nombre'],datos['apellido']),esperado)
        self.assertEqual(db.session.get(UsuarioModel,1).apellido,"D&#x27;Amico")

    def test_asignaciones_de_viajes_reportes_y_selectores(self):
        viaje = self.get('/api/viaje/1')
        self.assertEqual(viaje['chofer_nombre'],"María D'Amico")
        self.assertEqual(viaje['operador_nombre'],"Juan O'Connor")
        reporte = self.get('/api/reportes/2')['reporte']
        self.assertEqual(reporte['chofer_nombre'],"María D'Amico")
        self.assertEqual(reporte['mecanico_nombre'],"Luz & Sol D'Ávila")
        chofer = self.get('/api/operador/choferes')[0]
        self.assertEqual(chofer['apellido'],"D'Amico")
        mecanico = self.get('/api/operador/mecanicos')[0]
        self.assertEqual(mecanico['nombre'],'Luz & Sol')
        self.assertEqual(mecanico['apellido'],"D'Ávila")

    def test_estadisticas_rankings_y_horas(self):
        operador = self.get('/api/operador/estadisticas?alcance=todos&mes=2026-09')
        self.assertEqual(operador['choferes_mas_usados'][0]['apellido'],"D'Amico")
        admin = self.get('/api/admin/estadisticas?mes=2026-09',100,'admin')
        self.assertEqual(admin['choferes_mas_viajes'][0]['apellido'],"D'Amico")
        self.assertEqual(admin['operadores_mas_viajes'][0]['apellido'],"O'Connor")
        self.assertEqual(horas_por_chofer('2026-09')[0]['apellido'],"D'Amico")

    def test_guardar_repetidamente_no_duplica_codificacion_ni_cambia_nombres_omitidos(self):
        datos = {'nombre':'María &quot;', 'apellido':"D'Amico"}
        for _ in range(3):
            r = self.client.put('/api/perfil',headers=self.headers(1,'chofer'),json=datos)
            self.assertEqual(r.status_code,200,r.get_json())
            self.assertEqual(r.get_json()['perfil']['nombre'],datos['nombre'])
            self.assertEqual(r.get_json()['perfil']['apellido'],datos['apellido'])
        usuario = db.session.get(UsuarioModel,1)
        guardado = (usuario.nombre,usuario.apellido)
        for ruta, uid, rol, cuerpo in [('/api/perfil',1,'chofer',{'email':usuario.email}),
                                       ('/api/admin/usuarios/1',100,'admin',{'estado':'activo'})]:
            r = self.client.put(ruta,headers=self.headers(uid,rol),json=cuerpo)
            self.assertEqual(r.status_code,200,r.get_json())
            self.assertEqual((usuario.nombre,usuario.apellido),guardado)
        self.assertEqual(guardado,(escape(datos['nombre']),escape(datos['apellido'])))
        self.assertEqual(self.get('/api/viaje/1')['chofer_nombre'],"María &quot; D'Amico")

    def test_nombre_del_destinatario_y_actor_del_historial(self):
        NotificacionService.crear(1,'Aviso','Prueba','prueba')
        db.session.commit()
        destino = self.get('/api/notificaciones',1,'chofer')['notificaciones'][0]['usuario_destino']
        self.assertEqual(destino['apellido'],"D'Amico")
        with patch('controllers.operador_controller.NotificacionService.enviar_push_pendientes'):
            r = self.client.put('/api/operador/viajes/2',headers=self.headers(2,'operador'),json={'observaciones':'Nueva nota'})
        self.assertEqual(r.status_code,200,r.get_json())
        historial = self.get('/api/operador/viajes/2/historial')
        self.assertEqual(historial[0]['actor_nombre'],"Juan O'Connor")

    def test_login_devuelve_nombre_legible_sin_modificar_el_guardado(self):
        usuario = db.session.get(UsuarioModel,1)
        usuario.password = bcrypt.generate_password_hash('PruebaSolo123').decode('utf-8')
        db.session.commit()
        with patch('controllers.auth_controller.FirebaseAuthService.migrar_usuario_local',return_value=SimpleNamespace(uid='qa-nombres')):
            r = self.client.post('/api/auth/login',json={'username':'chofer@example.invalid','password':'PruebaSolo123'})
        self.assertEqual(r.status_code,200,r.get_json())
        self.assertEqual(r.get_json()['usuario']['apellido'],"D'Amico")
        self.assertEqual(usuario.apellido,"D&#x27;Amico")
