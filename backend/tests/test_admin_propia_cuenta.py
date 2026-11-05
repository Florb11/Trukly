import unittest

from flask_jwt_extended import JWTManager, create_access_token

from routes.administrador_routes import administrador_routes
from db_instance import db
from models.usuario_model import UsuarioModel
from models.administrador_model import AdministradorModel
from models.chofer_model import ChoferModel
from models.viaje_model import ViajeModel
from models.camion_model import CamionModel
from models.reporte_model import ReporteModel
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
        db.session.get(UsuarioModel, 3).estado = "activo"
        db.session.get(ReporteModel, 2).estado = "resuelto"
        db.session.get(ReporteModel, 2).Mecanico_Usuario_idUsuario = 3
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

    def test_mecanico_con_reportes_activos_no_se_desactiva_ni_queda_pendiente(self):
        for estado in ['pendiente', 'en revision']:
            db.session.get(ReporteModel, 2).estado = estado
            db.session.commit()
            for ruta, datos in [('/api/admin/usuarios/3/desactivar', None),
                                ('/api/admin/usuarios/3', {'estado':'inactivo', 'nombre':'No guardar'}),
                                ('/api/admin/usuarios/3', {'estado':'pendiente', 'nombre':'No guardar'})]:
                with self.subTest(estado=estado, ruta=ruta, datos=datos):
                    nombre = db.session.get(UsuarioModel, 3).nombre
                    r = self.cliente.put(ruta, headers=self.headers, json=datos)
                    self.assertEqual(r.status_code, 409, r.get_json())
                    self.assertIn('reasignalos', r.get_json()['mensaje'])
                    self.assertEqual(db.session.get(UsuarioModel, 3).estado, 'activo')
                    self.assertEqual(db.session.get(UsuarioModel, 3).nombre, nombre)
                    self.assertEqual(db.session.get(ReporteModel, 2).estado, estado)
                    self.assertEqual(db.session.get(ReporteModel, 2).Mecanico_Usuario_idUsuario, 3)

    def test_mecanico_con_reportes_cerrados_puede_desactivarse(self):
        for estado in ['resuelto', 'cancelado']:
            db.session.get(ReporteModel, 2).estado = estado
            for ruta, datos in [('/api/admin/usuarios/3/desactivar', None),
                                ('/api/admin/usuarios/3', {'estado':'inactivo'}),
                                ('/api/admin/usuarios/3', {'estado':'pendiente'})]:
                db.session.get(UsuarioModel, 3).estado = 'activo'
                db.session.commit()
                r = self.cliente.put(ruta, headers=self.headers, json=datos)
                self.assertEqual(r.status_code, 200, r.get_json())
                self.assertEqual(db.session.get(UsuarioModel, 3).estado, (datos or {}).get('estado', 'inactivo'))

    def test_reportes_de_otro_mecanico_no_bloquean_desactivacion(self):
        reporte = db.session.get(ReporteModel, 1)
        reporte.estado = 'en revision'
        reporte.Mecanico_Usuario_idUsuario = None
        db.session.commit()
        r = self.cliente.put('/api/admin/usuarios/3/desactivar', headers=self.headers)
        self.assertEqual(r.status_code, 200, r.get_json())

    def test_mecanico_con_reportes_activos_permite_editar_datos_personales(self):
        db.session.get(ReporteModel, 2).estado = 'en revision'
        db.session.commit()
        r = self.cliente.put('/api/admin/usuarios/3', headers=self.headers,
                             json={'nombre':'Actualizado', 'estado':'activo'})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(db.session.get(UsuarioModel, 3).estado, 'activo')
        self.assertEqual(db.session.get(ReporteModel, 2).estado, 'en revision')

    def test_camion_rechaza_capacidad_invalida_al_crear_y_editar_sin_cambios(self):
        camion = db.session.get(CamionModel, 1)
        original = (camion.capacidad_carga, camion.marca)
        for valor in ['Infinity', '-Infinity', 'NaN', True, False, 0, -1, 'abc', [], {}, 10**400]:
            for metodo, ruta in [('POST','/api/admin/camiones'), ('PUT','/api/admin/camiones/1')]:
                with self.subTest(valor=str(valor)[:30], metodo=metodo):
                    datos = {'matricula':'QA-CAP', 'marca':'No guardar', 'modelo':'QA',
                             'estado':'disponible', 'nroTanque':2, 'capacidad_carga':valor}
                    if metodo=='PUT':
                        datos = {'marca':'No guardar', 'capacidad_carga':valor}
                    r = self.cliente.open(ruta, method=metodo, headers=self.headers, json=datos)
                    self.assertEqual(r.status_code, 400, r.get_json())
                    db.session.refresh(camion)
                    self.assertEqual((camion.capacidad_carga, camion.marca), original)
                    self.assertIsNone(CamionModel.query.filter_by(matricula='QA-CAP').first())

    def test_camion_rechaza_tanque_decimal_booleano_o_fuera_de_rango(self):
        camion = db.session.get(CamionModel, 1)
        original = (camion.nroTanque, camion.marca)
        for valor in [1.9, '1.9', True, False, 0, -1, 'Infinity', 'NaN', '9'*5000, 2147483648, [], {}]:
            for metodo, ruta in [('POST','/api/admin/camiones'), ('PUT','/api/admin/camiones/1')]:
                with self.subTest(valor=str(valor)[:30], metodo=metodo):
                    datos = {'matricula':'QA-TAN', 'marca':'No guardar', 'modelo':'QA',
                             'estado':'disponible', 'nroTanque':valor, 'capacidad_carga':1000}
                    if metodo=='PUT':
                        datos = {'marca':'No guardar', 'nroTanque':valor}
                    r = self.cliente.open(ruta, method=metodo, headers=self.headers, json=datos)
                    self.assertEqual(r.status_code, 400, r.get_json())
                    db.session.refresh(camion)
                    self.assertEqual((camion.nroTanque, camion.marca), original)
                    self.assertIsNone(CamionModel.query.filter_by(matricula='QA-TAN').first())

    def test_camion_acepta_capacidad_decimal_y_tanque_entero_valido(self):
        for tanque in [1, ' 2 ', 3.0, 2147483647]:
            r = self.cliente.post('/api/admin/camiones', headers=self.headers, json={
                'matricula':'QA-VALIDO', 'marca':'Marca', 'modelo':'QA',
                'estado':'disponible', 'nroTanque':tanque, 'capacidad_carga':'2500.125'})
            self.assertEqual(r.status_code, 201, r.get_json())
            camion = CamionModel.query.filter_by(matricula='QAVALIDO').one()
            self.assertEqual(camion.nroTanque, int(tanque))
            self.assertEqual(camion.capacidad_carga, 2500.125)
            r = self.cliente.put('/api/admin/camiones/'+str(camion.id_camion), headers=self.headers,
                                  json={'capacidad_carga':'3000.5', 'nroTanque':'4'})
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(camion.capacidad_carga, 3000.5)
            self.assertEqual(camion.nroTanque, 4)
            db.session.delete(camion)
            db.session.commit()

    def test_dominio_camion_rechaza_numeros_invalidos_sin_sanitizador(self):
        from src.Camion import Camion
        datos = {'matricula':'QA', 'marca':'Marca', 'modelo':'Modelo', 'estado':'disponible',
                 'capacidad_carga':1000, 'nroTanque':1}
        for campo, valor in [('capacidad_carga', float('nan')), ('capacidad_carga', float('inf')),
                             ('capacidad_carga', True), ('nroTanque', 1.9), ('nroTanque', True)]:
            self.assertFalse(Camion.validar_datos_camion({**datos, campo:valor})[0])

    def test_camion_rechaza_textos_largos_al_crear_y_editar_sin_mutaciones(self):
        camion = db.session.get(CamionModel, 1)
        original = (camion.matricula, camion.marca, camion.modelo)
        for campo, limite in [('matricula',15), ('marca',20), ('modelo',20)]:
            for metodo, ruta in [('POST','/api/admin/camiones'), ('PUT','/api/admin/camiones/1')]:
                with self.subTest(campo=campo, metodo=metodo):
                    datos = {'matricula':'QA-LIMITE', 'marca':'Marca', 'modelo':'Modelo',
                             'capacidad_carga':1000, 'nroTanque':1, 'estado':'disponible', campo:'X'*(limite+1)}
                    if metodo=='PUT':
                        datos = {campo:'X'*(limite+1)}
                    cantidad = CamionModel.query.count()
                    r = self.cliente.open(ruta, method=metodo, headers=self.headers, json=datos)
                    self.assertEqual(r.status_code, 400, r.get_json())
                    self.assertIn(str(limite), r.get_json()['mensaje'])
                    self.assertEqual(CamionModel.query.count(), cantidad)
                    db.session.refresh(camion)
                    self.assertEqual((camion.matricula, camion.marca, camion.modelo), original)

    def test_camion_acepta_textos_en_el_limite(self):
        datos = {'matricula':'M'*15, 'marca':'A'*20, 'modelo':'B'*20,
                 'capacidad_carga':1000, 'nroTanque':1, 'estado':'disponible'}
        r = self.cliente.post('/api/admin/camiones', headers=self.headers, json=datos)
        self.assertEqual(r.status_code, 201, r.get_json())
        camion = CamionModel.query.filter_by(matricula='M'*15).one()
        try:
            r = self.cliente.put('/api/admin/camiones/'+str(camion.id_camion), headers=self.headers,
                                  json={'marca':'C'*20, 'modelo':'D'*20})
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(camion.marca, 'C'*20)
            self.assertEqual(camion.modelo, 'D'*20)
        finally:
            db.session.delete(camion)
            db.session.commit()

    def test_matricula_normalizada_se_guarda_y_rechaza_variantes_duplicadas(self):
        datos = {'matricula':' zz- 123-aa ', 'marca':'Marca', 'modelo':'QA',
                 'capacidad_carga':1000, 'nroTanque':1, 'estado':'disponible'}
        r = self.cliente.post('/api/admin/camiones', headers=self.headers, json=datos)
        self.assertEqual(r.status_code, 201, r.get_json())
        self.assertEqual(r.get_json()['camion']['matricula'], 'ZZ123AA')
        camion = CamionModel.query.filter_by(matricula='ZZ123AA').one()
        try:
            cantidad = CamionModel.query.count()
            for matricula in ['ZZ123AA', 'zz123aa', 'ZZ 123 AA', 'ZZ-123-AA', 'zz\t123 aa']:
                r = self.cliente.post('/api/admin/camiones', headers=self.headers, json={**datos, 'matricula':matricula})
                self.assertEqual(r.status_code, 400, r.get_json())
                self.assertEqual(CamionModel.query.count(), cantidad)
            r = self.cliente.put('/api/admin/camiones/'+str(camion.id_camion), headers=self.headers,
                                  json={'matricula':'zz-123 aa', 'modelo':'Actualizado'})
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(camion.matricula, 'ZZ123AA')
            self.assertEqual(camion.modelo, 'Actualizado')
        finally:
            db.session.delete(camion)
            db.session.commit()

    def test_detecta_matricula_historica_y_no_pisa_otro_camion(self):
        historico = CamionModel(id_camion=90, matricula=' zx- 901 ', marca='Marca', modelo='QA',
                                 capacidad_carga=1000, nroTanque=1, estado='disponible')
        db.session.add(historico)
        db.session.commit()
        try:
            r = self.cliente.post('/api/admin/camiones', headers=self.headers, json={
                'matricula':'ZX901', 'marca':'Marca', 'modelo':'QA', 'capacidad_carga':1000,
                'nroTanque':1, 'estado':'disponible'})
            self.assertEqual(r.status_code, 400, r.get_json())
            original = db.session.get(CamionModel, 1).matricula
            r = self.cliente.put('/api/admin/camiones/1', headers=self.headers, json={'matricula':'Z X-901'})
            self.assertEqual(r.status_code, 400, r.get_json())
            self.assertEqual(db.session.get(CamionModel, 1).matricula, original)
            r = self.cliente.put('/api/admin/camiones/90', headers=self.headers, json={'matricula':'ZX901'})
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(historico.matricula, 'ZX901')
        finally:
            db.session.delete(historico)
            db.session.commit()

    def test_matricula_solo_con_separadores_se_rechaza(self):
        original = db.session.get(CamionModel, 1).matricula
        for matricula in [' - ', '--', ' \t ']:
            r = self.cliente.put('/api/admin/camiones/1', headers=self.headers, json={'matricula':matricula})
            self.assertEqual(r.status_code, 400, r.get_json())
            self.assertEqual(db.session.get(CamionModel, 1).matricula, original)

    def test_normalizacion_matricula_tambien_en_dominio(self):
        from src.Camion import Camion
        datos = {'matricula':'aa-123 bb', 'marca':'Marca', 'modelo':'QA',
                 'capacidad_carga':1000, 'nroTanque':1, 'estado':'disponible'}
        self.assertEqual(Camion.crear_desde_datos(datos).matricula, 'AA123BB')
        self.assertIsNone(Camion.crear_desde_datos({**datos, 'matricula':'-- --'}))
