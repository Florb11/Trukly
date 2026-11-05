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
from routes.chofer_routes import chofer_routes
from models.camion_model import CamionModel
from utils.fecha_operativa import hoy_operativo


class RegistrosPermisosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-records-authorization-key'
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(registro_ingreso_salida_routes)
        cls.fixture.app.register_blueprint(chofer_routes)
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


    def test_creacion_manual_bloqueada_para_todos_sin_alterar_controles(self):
        for uid, rol, esperado in [(100,'admin',409),(2,'operador',409),(1,'chofer',403),(3,'mecanico',403),(None,None,401)]:
            headers = {} if uid is None else {'Authorization':'Bearer '+create_access_token(identity=str(uid),additional_claims={'rol':rol})}
            for datos in [{}, {'Viaje_id_viaje':77,'fecha_hora':'2026-09-01T09:00:00','tipo_registro':'ingreso'}]:
                r = self.client.post('/api/registros-ingreso-salida',json=datos,headers=headers)
                self.assertEqual(r.status_code,esperado,r.get_json())
                if esperado == 409:
                    self.assertIn('QR',r.get_json()['mensaje'])
                db.session.remove()
                self.assertEqual(RegistroIngresoSalidaModel.query.count(),2)
                self.assertEqual(db.session.get(ViajeModel,77).estado,'finalizado')

    def test_bloqueo_manual_no_impide_salida_y_regreso_qr(self):
        viaje = db.session.get(ViajeModel,77)
        viaje.estado = 'aceptado'
        viaje.fecha_salida = hoy_operativo()
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=77).delete()
        db.session.commit()
        try:
            operador = {'Authorization':'Bearer '+create_access_token(identity='2',additional_claims={'rol':'operador'})}
            r = self.client.post('/api/registros-ingreso-salida',json={'Viaje_id_viaje':77,'fecha_hora':'2026-09-01T09:00:00','tipo_registro':'ingreso'},headers=operador)
            self.assertEqual(r.status_code,409)
            self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=77).count(),0)
            chofer = {'Authorization':'Bearer '+create_access_token(identity='77',additional_claims={'rol':'chofer'})}
            for tipo, estado in [('ingreso','en curso'),('salida','finalizado')]:
                r = self.client.post('/api/choferes/viajes/77/registro',json={'tipo_registro':tipo},headers=chofer)
                self.assertEqual(r.status_code,201,r.get_json())
                db.session.remove()
                self.assertEqual(db.session.get(ViajeModel,77).estado,estado)
            self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=77).count(),2)
            self.assertEqual(db.session.get(CamionModel,1).estado,'en mantenimiento')
        finally:
            RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=77).delete()
            db.session.add(RegistroIngresoSalidaModel(id_registro=91,Viaje_id_viaje=77,fecha_hora=datetime(2026,9,1,10),tipo_registro='ingreso',observacion='Control del segundo chofer'))
            db.session.get(ViajeModel,77).estado = 'finalizado'
            db.session.get(ViajeModel,77).fecha_salida = date(2026,9,1)
            db.session.get(CamionModel,1).estado = 'disponible'
            db.session.commit()


    def test_historial_normaliza_ambos_esquemas_por_viaje_sin_cambiar_horas(self):
        from services.horas_viaje_service import tiempo_viaje
        db.session.add(ViajeModel(id_viaje=78,OperadorLogistico_Usuario_idUsuario=2,Chofer_Usuario_idUsuario=1,Camion_id_camion=1,fecha_salida=date(2026,9,2),origen='E',destino='F',estado='finalizado',recorrido=10))
        registro = db.session.get(RegistroIngresoSalidaModel,90)
        registro.tipo_registro = ' SALIDA '
        db.session.add_all([
            RegistroIngresoSalidaModel(id_registro=92,Viaje_id_viaje=1,fecha_hora=datetime(2026,9,1,12),tipo_registro=' ENTRADA '),
            RegistroIngresoSalidaModel(id_registro=93,Viaje_id_viaje=78,fecha_hora=datetime(2026,9,2,8),tipo_registro='ingreso'),
            RegistroIngresoSalidaModel(id_registro=94,Viaje_id_viaje=78,fecha_hora=datetime(2026,9,2,10),tipo_registro='salida'),
        ])
        db.session.commit()
        try:
            token = create_access_token(identity='1',additional_claims={'rol':'chofer'})
            r = self.client.get('/api/choferes/mis-registros',headers={'Authorization':'Bearer '+token})
            self.assertEqual(r.status_code,200,r.get_json())
            filas = r.get_json()
            self.assertEqual([f['id_registro'] for f in filas],[94,93,92,90])
            self.assertEqual({f['id_registro']:f['tipo_registro'] for f in filas},{90:'ingreso',92:'salida',93:'ingreso',94:'salida'})
            self.assertEqual(sum(f['tipo_registro']=='ingreso' for f in filas),2)
            self.assertEqual(sum(f['tipo_registro']=='salida' for f in filas),2)
            self.assertEqual(tiempo_viaje(db.session.get(ViajeModel,1))['segundos_confirmados'],10800)
            self.assertEqual(tiempo_viaje(db.session.get(ViajeModel,78))['segundos_confirmados'],7200)
            self.assertEqual(db.session.get(RegistroIngresoSalidaModel,90).tipo_registro,' SALIDA ')
            self.assertEqual(db.session.get(RegistroIngresoSalidaModel,92).tipo_registro,' ENTRADA ')
        finally:
            RegistroIngresoSalidaModel.query.filter(RegistroIngresoSalidaModel.id_registro.in_([92,93,94])).delete(synchronize_session=False)
            db.session.get(RegistroIngresoSalidaModel,90).tipo_registro = 'ingreso'
            ViajeModel.query.filter_by(id_viaje=78).delete()
            db.session.commit()
            db.session.remove()
