import unittest
from datetime import date, timedelta
from unittest.mock import patch

from flask import g
from flask_jwt_extended import JWTManager, create_access_token

from controllers.operador_controller import OperadorController
from controllers.carga_controller import CargaController
from db_instance import db
from models.usuario_model import UsuarioModel
from models.operador_model import OperadorModel
from models.chofer_model import ChoferModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from models.viaje_cambio_model import ViajeCambioModel
from models.carga_model import CargaModel
from models.reporte_model import ReporteModel
from models.notificacion_model import NotificacionModel
from src.OperadorLogistico import OperadorLogistico
from services.notificacion_service import NotificacionService


class OperacionCompartidaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config['JWT_SECRET_KEY'] = 'test-only-shared-operation-secret-key'
        JWTManager(cls.fixture.app)
        from routes.operador_routes import operador_routes
        from routes.viaje_routes import viaje_routes
        cls.fixture.app.register_blueprint(operador_routes)
        cls.fixture.app.register_blueprint(viaje_routes)
        from routes.reporte_routes import reporte_routes
        cls.fixture.app.register_blueprint(reporte_routes)
        from routes.mecanico_routes import mecanico_routes
        cls.fixture.app.register_blueprint(mecanico_routes)
        from routes.chofer_routes import chofer_routes
        cls.fixture.app.register_blueprint(chofer_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        self.emisor_real = NotificacionService.enviar_push_pendientes
        push = patch('controllers.operador_controller.NotificacionService.enviar_push_pendientes')
        self.enviar_push = push.start()
        self.addCleanup(push.stop)
        db.session.get(ViajeModel, 2).estado = 'en curso'
        db.session.get(CamionModel, 1).estado = 'disponible'
        db.session.add_all([
            UsuarioModel(id_usuario=90, username='operador2', password='x', nombre='Segundo', apellido='Operador', rol='operador', estado='activo'),
            OperadorModel(Usuario_idUsuario=90, legajo='O90', sector='Logística'),
            UsuarioModel(id_usuario=91, username='chofer2', password='x', nombre='Segundo', apellido='Chofer', rol='chofer', estado='activo'),
            ChoferModel(Usuario_idUsuario=91, licencia='LIC91', vencimientoLicencia=date(2099,1,1), legajo='C91'),
            CamionModel(id_camion=90, matricula='QA90', marca='Marca', modelo='Modelo', capacidad_carga=1000, estado='en viaje', nroTanque=90),
            ViajeModel(id_viaje=50, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=91,
                Camion_id_camion=90, origen='A', destino='B', origen_lat=-34, origen_lon=-58,
                fecha_salida=date.today(), estado='aceptado', recorrido=10),
        ])
        db.session.commit()
        self.operador = OperadorLogistico.crear_desde_datos({
            'id_usuario': 90, 'nombre': 'Segundo', 'apellido': 'Operador', 'estado': 'activo', 'rol': 'operador'})

    def tearDown(self):
        db.session.rollback()
        NotificacionModel.query.delete()
        ViajeCambioModel.query.delete()
        CargaModel.query.filter_by(Viaje_id_viaje=50).delete()
        ReporteModel.query.filter_by(Chofer_Usuario_idUsuario=91).delete()
        ViajeModel.query.filter(ViajeModel.id_viaje >= 50).delete()
        ChoferModel.query.filter_by(Usuario_idUsuario=91).delete()
        OperadorModel.query.filter_by(Usuario_idUsuario=90).delete()
        CamionModel.query.filter_by(id_camion=90).delete()
        UsuarioModel.query.filter(UsuarioModel.id_usuario.in_([90, 91])).delete()
        db.session.commit()
        db.session.remove()

    def editar(self, datos):
        with self.fixture.app.test_request_context('/', method='PUT', json=datos):
            g.operador_actual = self.operador
            return OperadorController.editar_viaje.__wrapped__(50)

    def test_operador_ve_todos_y_filtro_mios_mantiene_creador(self):
        for query, esperado in [('', True), ('?alcance=mios', False)]:
            with self.fixture.app.test_request_context('/'+query):
                g.operador_actual = self.operador
                r, codigo = OperadorController.listar_viajes.__wrapped__()
                self.assertEqual(codigo, 200)
                self.assertEqual(any(v['id_viaje'] == 50 for v in r.get_json()), esperado)
        self.assertEqual(db.session.get(ViajeModel, 50).OperadorLogistico_Usuario_idUsuario, 2)

    def test_editar_otro_viaje_guarda_actor_real_y_no_cambia_creador(self):
        r, codigo = self.editar({'observaciones': 'Gestionado por otro operador'})
        self.assertEqual(codigo, 200, r.get_json())
        viaje = db.session.get(ViajeModel, 50)
        self.assertEqual(viaje.OperadorLogistico_Usuario_idUsuario, 2)
        self.assertEqual(viaje.origen_lat, -34)
        cambio = ViajeCambioModel.query.filter_by(id_viaje=50).one()
        self.assertEqual(cambio.id_usuario, 90)
        self.assertEqual(cambio.actor_nombre, 'Segundo Operador')
        self.assertEqual(cambio.datos['cambios']['observaciones']['despues'], 'Gestionado por otro operador')

    def test_cancelacion_de_otro_operador_con_motivo_y_auditoria(self):
        with self.fixture.app.test_request_context('/', method='PUT', json={'motivo': 'Cambio de planificación'}), patch(
            'controllers.operador_controller.AdminNotificacionService.viaje_cancelado'
        ), patch('controllers.operador_controller.NotificacionService.enviar_push_pendientes'):
            g.operador_actual = self.operador
            r, codigo = OperadorController.cancelar_viaje.__wrapped__(50)
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'disponible')
        cambio = ViajeCambioModel.query.filter_by(id_viaje=50).one()
        self.assertEqual(cambio.id_usuario, 90)
        self.assertEqual(cambio.datos['motivo'], 'Cambio de planificación')

    def test_otro_operador_puede_gestionar_cargas_y_queda_identificado(self):
        with self.fixture.app.test_request_context('/', method='POST', json={'descripcion':'Mercadería', 'tipo':'General', 'peso':'100'}):
            g.operador_actual = self.operador
            r, codigo = CargaController.gestionar.__wrapped__(50)
        self.assertEqual(codigo, 201, r.get_json())
        cambio = ViajeCambioModel.query.filter_by(id_viaje=50).one()
        self.assertEqual(cambio.accion, 'carga_agregada')
        self.assertEqual(cambio.id_usuario, 90)
        self.assertEqual(r.get_json()['peso_total_kg'], 100)

    def test_viaje_cerrado_no_se_edita_ni_audita(self):
        db.session.get(ViajeModel, 50).estado = 'finalizado'
        db.session.commit()
        self.assertEqual(self.editar({'observaciones':'No permitido'})[1], 400)
        self.assertEqual(ViajeCambioModel.query.count(), 0)

    def test_reasignacion_no_permite_chofer_ocupado(self):
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.commit()
        self.assertEqual(self.editar({'Chofer_Usuario_idUsuario': 1})[1], 409)
        self.assertEqual(db.session.get(ViajeModel, 50).Chofer_Usuario_idUsuario, 91)
        self.assertEqual(ViajeCambioModel.query.count(), 0)

    def test_creacion_registra_creador_y_actor_y_filtro_mios(self):
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.commit()
        with self.fixture.app.test_request_context('/', method='POST', json={
            'origen': 'C', 'destino': 'D', 'fecha_salida': date.today().isoformat(),
            'Chofer_Usuario_idUsuario': 91, 'Camion_id_camion': 90, 'recorrido': 15,
        }), patch('controllers.operador_controller.NotificacionService.crear'):
            g.operador_actual = self.operador
            r, codigo = OperadorController.crear_viaje.__wrapped__()
        self.assertEqual(codigo, 201, r.get_json())
        nuevo = r.get_json()['viaje']['id_viaje']
        self.assertEqual(r.get_json()['viaje']['OperadorLogistico_Usuario_idUsuario'], 90)
        self.assertEqual(ViajeCambioModel.query.filter_by(id_viaje=nuevo).one().id_usuario, 90)
        with self.fixture.app.test_request_context('/?alcance=mios'):
            g.operador_actual = self.operador
            r, _ = OperadorController.listar_viajes.__wrapped__()
            self.assertEqual([v['id_viaje'] for v in r.get_json()], [nuevo])

    def test_sin_historial_no_se_confirma_cambio(self):
        with patch('controllers.operador_controller.registrar', side_effect=RuntimeError('No disponible')), patch('controllers.operador_controller.logger'):
            self.assertEqual(self.editar({'observaciones':'No debe persistir'})[1], 500)
        self.assertIsNone(db.session.get(ViajeModel, 50).observaciones)

    def test_fallo_commit_revierte_viaje_e_historial(self):
        with patch.object(db.session, 'commit', side_effect=RuntimeError('Sin conexión')), patch('controllers.operador_controller.logger'):
            self.assertEqual(self.editar({'observaciones':'No confirmado'})[1], 500)
        self.assertIsNone(db.session.get(ViajeModel, 50).observaciones)
        self.assertEqual(ViajeCambioModel.query.count(), 0)

    def test_edicion_rechaza_fechas_y_kilometros_invalidos_sin_cambios(self):
        viaje = db.session.get(ViajeModel, 50)
        original = (viaje.fecha_salida, viaje.fecha_llegada, viaje.recorrido)
        casos = [{'fecha_salida': (date.today()-timedelta(days=1)).isoformat()},
                 {'fecha_salida':'no-es-fecha'}, {'fecha_salida':''},
                 {'fecha_salida':'2026-02-30'}, {'fecha_salida':'2026-11-04T12:00:00'},
                 {'fecha_llegada':'1999-01-01'}, {'fecha_llegada':'incorrecta'},
                 {'recorrido':-25}, {'recorrido':'NaN'}, {'recorrido':'Infinity'},
                 {'recorrido':'abc'}, {'recorrido':None}, {'recorrido':True}]
        for datos in casos:
            with self.subTest(datos=datos):
                r, codigo = self.editar(datos)
                self.assertEqual(codigo, 400, r.get_json())
                db.session.refresh(viaje)
                self.assertEqual((viaje.fecha_salida, viaje.fecha_llegada, viaje.recorrido), original)
                self.assertEqual(ViajeCambioModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_observaciones_de_viaje_antiguo_admiten_fechas_sin_modificar(self):
        viaje = db.session.get(ViajeModel, 50)
        viaje.fecha_salida = date(2000,1,1)
        viaje.fecha_llegada = date(2000,1,2)
        db.session.commit()
        r, codigo = self.editar({'fecha_salida':'2000-01-01', 'fecha_llegada':'2000-01-02',
                                'observaciones':'Corrección de notas'})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(viaje.fecha_salida, date(2000,1,1))
        self.assertEqual(viaje.fecha_llegada, date(2000,1,2))

    def test_edicion_futura_valida_y_recorrido_cero(self):
        salida = date.today()+timedelta(days=1)
        llegada = salida+timedelta(days=1)
        r, codigo = self.editar({'fecha_salida':salida.isoformat(), 'fecha_llegada':llegada.isoformat(), 'recorrido':0})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(r.get_json()['viaje']['recorrido'], 0)
        self.assertEqual(r.get_json()['viaje']['fecha_salida'], salida.isoformat())
        r, codigo = self.editar({'fecha_llegada':''})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertIsNone(r.get_json()['viaje']['fecha_llegada'])

    def test_viaje_en_curso_conserva_fecha_salida_pero_admite_observaciones(self):
        db.session.get(ViajeModel, 50).estado = 'en curso'
        db.session.commit()
        self.assertEqual(self.editar({'fecha_salida':(date.today()+timedelta(days=1)).isoformat()})[1], 400)
        self.assertEqual(self.editar({'observaciones':'Actualización en ruta'})[1], 200)

    def test_estadisticas_permiten_operacion_completa_o_creados_por_mi(self):
        for alcance, esperado in [('mios', 0), ('todos', 1)]:
            with self.fixture.app.test_request_context('/?mes='+date.today().strftime('%Y-%m')+'&alcance='+alcance):
                g.operador_actual = self.operador
                respuesta, codigo = OperadorController.obtener_estadisticas.__wrapped__()
                self.assertEqual(codigo, 200, respuesta.get_json())
                self.assertEqual(respuesta.get_json()['resumen']['total_viajes'], esperado)

    def test_api_autenticada_no_admite_chofer_como_operador(self):
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.commit()
        for id_usuario, rol, esperado in [(90, 'operador', 200), (1, 'chofer', 403)]:
            token = create_access_token(identity=str(id_usuario), additional_claims={'rol':rol})
            r = self.fixture.app.test_client().get('/api/operador/viajes/50/historial', headers={'Authorization':'Bearer '+token})
            self.assertEqual(r.status_code, esperado, r.get_json())
            detalle = self.fixture.app.test_client().get('/api/viaje/50', headers={'Authorization':'Bearer '+token})
            self.assertEqual(detalle.status_code, esperado, detalle.get_json())

    def test_flujo_compartido_autenticado_con_cargas_historial_y_cancelacion(self):
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        headers = {'Authorization':'Bearer '+token}
        cliente = self.fixture.app.test_client()
        self.assertEqual(cliente.put('/api/operador/viajes/50', json={'observaciones':'Gestión compartida'}, headers=headers).status_code, 200)
        r = cliente.post('/api/operador/viajes/50/cargas', json={'descripcion':'Prueba', 'tipo':'General', 'peso':'100'}, headers=headers)
        self.assertEqual(r.status_code, 201, r.get_json())
        id_carga = r.get_json()['cargas'][0]['id_carga']
        r = cliente.put(f'/api/operador/viajes/50/cargas/{id_carga}', json={'descripcion':'Prueba', 'tipo':'General', 'peso':'200'}, headers=headers)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['peso_total_kg'], 200)
        r = cliente.delete(f'/api/operador/viajes/50/cargas/{id_carga}', headers=headers)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['peso_total_kg'], 0)
        with patch('controllers.operador_controller.AdminNotificacionService.viaje_cancelado'), patch('controllers.operador_controller.NotificacionService.enviar_push_pendientes'):
            self.assertEqual(cliente.put('/api/operador/viajes/50/cancelar', json={'motivo':''}, headers=headers).status_code, 400)
            r = cliente.put('/api/operador/viajes/50/cancelar', json={'motivo':'Fin de prueba'}, headers=headers)
            self.assertEqual(r.status_code, 200, r.get_json())
        r = cliente.get('/api/operador/viajes/50/historial', headers=headers)
        self.assertEqual(r.status_code, 200)
        cambios = r.get_json()
        self.assertEqual({c['accion'] for c in cambios}, {'viaje_editado','carga_agregada','carga_editada','carga_eliminada','viaje_cancelado'})
        self.assertEqual(len(cambios), 5)
        self.assertTrue(all(c['id_usuario'] == 90 and c['actor_nombre'] == 'Segundo Operador' for c in cambios))
        self.assertEqual(db.session.get(ViajeModel, 50).OperadorLogistico_Usuario_idUsuario, 2)

    def test_reasignacion_compartida_exige_aceptacion_nueva_y_actualiza_nombre(self):
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.commit()
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        r = self.fixture.app.test_client().put('/api/operador/viajes/50', json={'Chofer_Usuario_idUsuario':1}, headers={'Authorization':'Bearer '+token})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['viaje']['estado'], 'pendiente')
        self.assertEqual(r.get_json()['viaje']['chofer_nombre'], 'Ana García')
        self.assertEqual(r.get_json()['viaje']['OperadorLogistico_Usuario_idUsuario'], 2)
        cambio = ViajeCambioModel.query.filter_by(id_viaje=50).one()
        self.assertEqual(cambio.datos['cambios']['Chofer_Usuario_idUsuario'], {'antes':91,'despues':1})

    def crear_con_chofer_libre(self):
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.commit()
        with self.fixture.app.test_request_context('/', method='POST', json={
            'origen':'A', 'destino':'B', 'fecha_salida':date.today().isoformat(),
            'Chofer_Usuario_idUsuario':91, 'Camion_id_camion':90, 'recorrido':10,
        }):
            g.operador_actual = self.operador
            return OperadorController.crear_viaje.__wrapped__()

    def test_creacion_guarda_aviso_y_luego_envia_push(self):
        eventos = []
        original = db.session.commit
        def confirmar():
            original()
            eventos.append('commit')
        self.enviar_push.side_effect = lambda: eventos.append('push')
        with patch.object(db.session, 'commit', side_effect=confirmar):
            r, codigo = self.crear_con_chofer_libre()
        self.assertEqual(codigo, 201, r.get_json())
        self.assertEqual(eventos[-2:], ['commit', 'push'])
        self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=91, tipo='viaje_asignado').count(), 1)
        self.enviar_push.assert_called_once()

    def test_reasignacion_envia_avisos_a_ambos_choferes_despues_de_guardar(self):
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.commit()
        eventos = []
        original = db.session.commit
        def confirmar():
            original()
            eventos.append('commit')
        self.enviar_push.side_effect = lambda: eventos.append('push')
        with patch.object(db.session, 'commit', side_effect=confirmar):
            r, codigo = self.editar({'Chofer_Usuario_idUsuario':1})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(eventos, ['commit', 'push'])
        self.assertEqual({n.Usuario_idUsuario for n in NotificacionModel.query.all()}, {1,91})

    def test_fallo_guardado_no_envia_push(self):
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.commit()
        with patch.object(db.session, 'commit', side_effect=RuntimeError('Base caída')), patch('controllers.operador_controller.logger'):
            self.assertEqual(self.editar({'Chofer_Usuario_idUsuario':1})[1], 500)
        self.enviar_push.assert_not_called()
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.assertEqual(db.session.get(ViajeModel, 50).Chofer_Usuario_idUsuario, 91)

    def test_error_firebase_no_deshace_viaje_ni_notificacion(self):
        # Se ejecuta el emisor real; el fallo externo se simula antes de contactar Firebase.
        self.enviar_push.side_effect = self.emisor_real
        with patch('services.firebase_service.FirebaseAuthService.inicializar', side_effect=RuntimeError('Firebase caído')), patch('utils.app_logger.get_app_logger'):
            r, codigo = self.crear_con_chofer_libre()
        self.assertEqual(codigo, 201, r.get_json())
        self.assertEqual(db.session.get(ViajeModel, r.get_json()['viaje']['id_viaje']).estado, 'pendiente')
        self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=91).count(), 1)
        self.assertNotIn('push_pendientes', db.session.info)

    def test_licencia_vencida_impide_crear_y_reasignar(self):
        from utils.fecha_operativa import hoy_operativo
        db.session.get(ChoferModel, 91).vencimientoLicencia = hoy_operativo() - timedelta(days=1)
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.commit()
        with self.fixture.app.test_request_context('/', method='POST', json={
            'origen':'A', 'destino':'B', 'fecha_salida':hoy_operativo().isoformat(),
            'Chofer_Usuario_idUsuario':91, 'Camion_id_camion':90, 'recorrido':10,
        }):
            g.operador_actual = self.operador
            respuesta, codigo = OperadorController.crear_viaje.__wrapped__()
        self.assertEqual(codigo, 409, respuesta.get_json())
        viaje = db.session.get(ViajeModel, 50)
        viaje.estado = 'pendiente'
        viaje.Chofer_Usuario_idUsuario = 1
        db.session.commit()
        respuesta, codigo = self.editar({'Chofer_Usuario_idUsuario':91})
        self.assertEqual(codigo, 409, respuesta.get_json())
        self.assertEqual(viaje.Chofer_Usuario_idUsuario, 1)
        self.assertEqual(ViajeCambioModel.query.count(), 0)

    def test_disponibles_excluye_licencia_vencida_pero_admite_vencimiento_hoy(self):
        from utils.fecha_operativa import hoy_operativo
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        for vencimiento, incluido in [(hoy_operativo()-timedelta(days=1), False), (hoy_operativo(), True)]:
            db.session.get(ChoferModel, 91).vencimientoLicencia = vencimiento
            db.session.commit()
            with self.fixture.app.test_request_context('/?disponibles=1'):
                g.operador_actual = self.operador
                respuesta, codigo = OperadorController.listar_choferes.__wrapped__()
            self.assertEqual(codigo, 200)
            self.assertEqual(any(c['id_usuario']==91 for c in respuesta.get_json()), incluido)

    def test_ruta_general_tambien_bloquea_licencia_vencida(self):
        from utils.fecha_operativa import hoy_operativo
        db.session.get(ChoferModel, 91).vencimientoLicencia = hoy_operativo() - timedelta(days=1)
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.commit()
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        respuesta = self.fixture.app.test_client().post('/api/viaje',
            headers={'Authorization':'Bearer '+token}, json={
                'origen':'A', 'destino':'B', 'fecha_salida':hoy_operativo().isoformat(),
                'Chofer_Usuario_idUsuario':91, 'Camion_id_camion':90, 'recorrido':10,
            })
        self.assertEqual(respuesta.status_code, 409, respuesta.get_json())
        self.assertIn('licencia', respuesta.get_json()['mensaje'])
        self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje > 50).count(), 0)

    def test_ambas_rutas_rechazan_chofer_ocupado_sin_efectos(self):
        from utils.fecha_operativa import hoy_operativo
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        client = self.fixture.app.test_client()
        datos = {'origen':'A', 'destino':'B', 'fecha_salida':hoy_operativo().isoformat(),
                 'Chofer_Usuario_idUsuario':91, 'Camion_id_camion':1, 'recorrido':10}
        for estado in ['pendiente', 'aceptado', 'en curso']:
            db.session.get(ViajeModel, 50).estado = estado
            db.session.commit()
            for ruta in ['/api/operador/viajes', '/api/viaje']:
                with self.subTest(estado=estado, ruta=ruta):
                    respuesta = client.post(ruta, headers={'Authorization':'Bearer '+token}, json=datos)
                    self.assertEqual(respuesta.status_code, 400, respuesta.get_json())
                    self.assertIn('chofer ya tiene', respuesta.get_json()['mensaje'])
                    self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje>50).count(), 0)
                    self.assertEqual(ViajeCambioModel.query.count(), 0)
                    self.assertEqual(NotificacionModel.query.count(), 0)
                    self.assertEqual(db.session.get(CamionModel, 1).estado, 'disponible')
        self.enviar_push.assert_not_called()

    def test_ruta_general_permite_chofer_con_viaje_cerrado(self):
        db.session.get(ViajeModel, 2).estado = "finalizado"
        from utils.fecha_operativa import hoy_operativo
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        client = self.fixture.app.test_client()
        for estado in ['finalizado', 'cancelado']:
            with self.subTest(estado=estado):
                db.session.get(ViajeModel, 50).estado = estado
                db.session.commit()
                respuesta = client.post('/api/viaje', headers={'Authorization':'Bearer '+token}, json={
                    'origen':'A', 'destino':'B', 'fecha_salida':hoy_operativo().isoformat(),
                    'Chofer_Usuario_idUsuario':91, 'Camion_id_camion':1, 'recorrido':10,
                })
                self.assertEqual(respuesta.status_code, 201, respuesta.get_json())
                creado = db.session.get(ViajeModel, respuesta.get_json()['viaje']['id_viaje'])
                self.assertEqual(creado.estado, 'pendiente')
                creado.estado = 'finalizado'
                db.session.get(CamionModel, 1).estado = 'disponible'
                db.session.commit()

    def crear_general(self, chofer=91, camion=90):
        from utils.fecha_operativa import hoy_operativo
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        return self.fixture.app.test_client().post('/api/viaje',
            headers={'Authorization':'Bearer '+token}, json={
                'origen':'A', 'destino':'B', 'fecha_salida':hoy_operativo().isoformat(),
                'Chofer_Usuario_idUsuario':chofer, 'Camion_id_camion':camion, 'recorrido':10})

    def test_general_rechaza_chofer_inactivo_o_pendiente(self):
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        for estado in ['inactivo', 'pendiente']:
            db.session.get(UsuarioModel, 91).estado = estado
            db.session.commit()
            r = self.crear_general()
            self.assertEqual(r.status_code, 400, r.get_json())
            self.assertIn('chofer', r.get_json()['mensaje'])
            self.assertEqual(db.session.get(CamionModel, 90).estado, 'disponible')
            self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje>50).count(), 0)
            self.assertEqual(NotificacionModel.query.count(), 0)
            self.assertEqual(ViajeCambioModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_general_reserva_camion_e_impide_segunda_asignacion(self):
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.commit()
        r = self.crear_general()
        self.assertEqual(r.status_code, 201, r.get_json())
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'en viaje')
        r = self.crear_general(chofer=1)
        self.assertEqual(r.status_code, 400, r.get_json())
        self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje>50).count(), 1)
        self.assertEqual(NotificacionModel.query.count(), 1)
        self.assertEqual(ViajeCambioModel.query.count(), 1)

    def test_general_rechaza_camion_con_viaje_aunque_diga_disponible(self):
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.commit()
        # El camión 1 figura disponible pero conserva el viaje 2 en curso.
        r = self.crear_general(camion=1)
        self.assertEqual(r.status_code, 400, r.get_json())
        self.assertIn('camión ya tiene', r.get_json()['mensaje'])
        self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje>50).count(), 0)

    def test_general_revierte_reserva_si_falla_guardado(self):
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.commit()
        with patch.object(db.session, 'commit', side_effect=RuntimeError('Fallo de prueba')), patch('controllers.viaje_controller.logger'):
            r = self.crear_general()
        self.assertEqual(r.status_code, 500, r.get_json())
        self.assertEqual(db.session.get(CamionModel, 90).estado, 'disponible')
        self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje>50).count(), 0)
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.assertEqual(ViajeCambioModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_cancelacion_solo_antes_de_iniciar_para_admin_y_operador(self):
        db.session.add(UsuarioModel(id_usuario=99, username='admin_cancelacion', password='x',
            nombre='QA', apellido='Admin', rol='admin', estado='activo'))
        db.session.commit()
        try:
            for rol, identidad, ruta in [('operador','90','/api/operador/viajes/50/cancelar'),
                                         ('admin','99','/api/admin/viajes/50/cancelar')]:
                token = create_access_token(identity=identidad, additional_claims={'rol':rol})
                for estado in ['en curso', 'finalizado', 'cancelado', 'pendiente', 'aceptado']:
                    with self.subTest(rol=rol, estado=estado):
                        NotificacionModel.query.delete()
                        ViajeCambioModel.query.delete()
                        viaje = db.session.get(ViajeModel, 50)
                        viaje.estado = estado
                        viaje.observaciones = 'Original'
                        db.session.get(CamionModel, 90).estado = 'en viaje'
                        db.session.commit()
                        r = self.fixture.app.test_client().put(ruta,
                            headers={'Authorization':'Bearer '+token}, json={'motivo':'Cambio de plan'})
                        permitido = estado in ['pendiente', 'aceptado']
                        self.assertEqual(r.status_code, 200 if permitido else 400, r.get_json())
                        self.assertEqual(viaje.estado, 'cancelado' if permitido else estado)
                        self.assertEqual(db.session.get(CamionModel, 90).estado,
                                         'disponible' if permitido else 'en viaje')
                        if not permitido:
                            self.assertEqual(viaje.observaciones, 'Original')
                            self.assertEqual(ViajeCambioModel.query.count(), 0)
                            self.assertEqual(NotificacionModel.query.count(), 0)
        finally:
            db.session.rollback()
            NotificacionModel.query.delete()
            ViajeCambioModel.query.delete()
            UsuarioModel.query.filter_by(id_usuario=99).delete()
            db.session.commit()

    def test_descripcion_reporte_conserva_simbolos_en_creacion_y_consulta(self):
        from models.reporte_model import ReporteModel
        from controllers.mecanico_controller import MecanicoController
        from services.admin_notificacion_service import AdminNotificacionService
        db.session.get(ViajeModel, 50).estado = 'en curso'
        db.session.commit()
        token = create_access_token(identity='91', additional_claims={'rol':'chofer'})
        headers = {'Authorization':'Bearer '+token}
        client = self.fixture.app.test_client()
        for texto in ['El motor hace "tac tac" & vibra', "Pérdida en caño <motor> y 'válvula'", 'Escribí &quot; literalmente', '<script>alert(1)</script>']:
            r = client.post('/api/reportes', headers=headers,
                json={'Camion_id_camion':90, 'descripcion':texto})
            self.assertEqual(r.status_code, 201, r.get_json())
            datos = r.get_json()['reporte']
            self.assertEqual(datos['descripcion'], texto)
            reporte = db.session.get(ReporteModel, datos['id_reporte'])
            self.assertEqual(reporte.to_dict()['descripcion'], texto)
            self.assertEqual(MecanicoController.preparar_respuesta_reporte(reporte)['descripcion'], texto)
            r = client.get('/api/reportes/'+str(reporte.id_reporte), headers=headers)
            self.assertEqual(r.get_json()['reporte']['descripcion'], texto)
            with patch.object(AdminNotificacionService, '_crear') as aviso:
                AdminNotificacionService.nueva_falla(reporte)
                # El aviso administrativo tampoco debe mostrar entidades HTML.
                self.assertIn(texto, aviso.call_args.args[3])

    def test_descripcion_historica_se_decodifica_una_sola_vez(self):
        from models.reporte_model import ReporteModel
        from controllers.reporte_controller import ReporteController
        reporte = db.session.get(ReporteModel, 1)
        original = reporte.descripcion
        try:
            reporte.descripcion = 'Motor &quot;tac&quot; &amp; válvula &lt;A&gt;'
            esperado = 'Motor "tac" & válvula <A>'
            self.assertEqual(reporte.to_dict()['descripcion'], esperado)
            self.assertEqual(ReporteController.preparar_respuesta_reporte(reporte)['descripcion'], esperado)
            self.assertEqual(reporte.descripcion, 'Motor &quot;tac&quot; &amp; válvula &lt;A&gt;')
        finally:
            reporte.descripcion = original

    def test_nota_reparacion_conserva_simbolos_y_notificacion(self):
        from controllers.reporte_controller import ReporteController
        from controllers.mecanico_controller import MecanicoController
        db.session.get(UsuarioModel, 3).estado = 'activo'
        token = create_access_token(identity='3', additional_claims={'rol':'mecanico'})
        client = self.fixture.app.test_client()
        reporte = db.session.get(ReporteModel, 2)
        original = (reporte.estado, reporte.nota_reparacion, reporte.fecha_resolucion)
        try:
            for nota in ['Se cambió la pieza "A" & el caño', "Ajuste <motor> y 'válvula'", 'Texto literal &quot; &amp;', '<script>alert(1)</script>']:
                reporte.estado = 'en revision'
                db.session.commit()
                r = client.put('/api/mecanico/reportes/2/resolver',
                    headers={'Authorization':'Bearer '+token}, json={'nota_reparacion':nota})
                self.assertEqual(r.status_code, 200, r.get_json())
                self.assertEqual(r.get_json()['reporte']['nota_reparacion'], nota)
                self.assertEqual(reporte.to_dict()['nota_reparacion'], nota)
                self.assertEqual(ReporteController.preparar_respuesta_reporte(reporte)['nota_reparacion'], nota)
                self.assertEqual(MecanicoController.preparar_respuesta_reporte(reporte)['nota_reparacion'], nota)
                aviso = NotificacionModel.query.filter_by(tipo='reporte_resuelto').order_by(NotificacionModel.id_notificacion.desc()).first()
                self.assertIn(nota, aviso.mensaje)
        finally:
            reporte.estado, reporte.nota_reparacion, reporte.fecha_resolucion = original
            db.session.commit()

    def test_nota_historica_no_se_decodifica_al_persistir_otros_cambios(self):
        from controllers.reporte_controller import ReporteController
        from controllers.mecanico_controller import MecanicoController
        reporte = db.session.get(ReporteModel, 2)
        original = reporte.nota_reparacion
        try:
            reporte.nota_reparacion = 'Pieza &quot;A&quot; &amp; texto &amp;quot;'
            esperado = 'Pieza "A" & texto &quot;'
            for controller in [ReporteController, MecanicoController]:
                self.assertEqual(controller.preparar_respuesta_reporte(reporte)['nota_reparacion'], esperado)
                dominio = controller.crear_objeto_reporte(reporte)
                controller.actualizar_modelo_reporte(reporte, dominio)
                self.assertEqual(reporte.nota_reparacion, 'Pieza &quot;A&quot; &amp; texto &amp;quot;')
            self.assertEqual(reporte.to_dict()['nota_reparacion'], esperado)
        finally:
            reporte.nota_reparacion = original

    def test_cambios_importantes_piden_aceptar_y_avisan_una_vez(self):
        from utils.fecha_operativa import hoy_operativo
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.commit()
        for datos in [{'origen':'Nuevo origen'}, {'destino':'Nuevo destino'},
                      {'fecha_salida':(hoy_operativo()+timedelta(days=1)).isoformat()},
                      {'Camion_id_camion':1}]:
            with self.subTest(datos=datos):
                viaje = db.session.get(ViajeModel, 50)
                viaje.estado = 'aceptado'
                NotificacionModel.query.delete()
                db.session.commit()
                r, codigo = self.editar(datos)
                self.assertEqual(codigo, 200, r.get_json())
                self.assertEqual(viaje.estado, 'pendiente')
                aviso = NotificacionModel.query.one()
                self.assertEqual(aviso.Usuario_idUsuario, 91)
                self.assertEqual(aviso.tipo, 'viaje_actualizado')
                self.assertIn('aceptá', aviso.mensaje)
                # Reenviar el mismo formulario no invalida una nueva aceptación.
                viaje.estado = 'aceptado'
                db.session.commit()
                r, codigo = self.editar(datos)
                self.assertEqual(codigo, 200, r.get_json())
                self.assertEqual(viaje.estado, 'aceptado')
                self.assertEqual(NotificacionModel.query.count(), 1)

    def test_observaciones_no_invalidan_aceptacion_ni_generan_aviso(self):
        viaje = db.session.get(ViajeModel, 50)
        r, codigo = self.editar({'observaciones':'Nueva observación'})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(viaje.estado, 'aceptado')
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_qr_requiere_nueva_aceptacion_despues_de_cambiar_destino(self):
        token = create_access_token(identity='91', additional_claims={'rol':'chofer'})
        client = self.fixture.app.test_client()
        headers = {'Authorization':'Bearer '+token}
        r, codigo = self.editar({'destino':'Nuevo destino'})
        self.assertEqual(codigo, 200, r.get_json())
        r = client.post('/api/choferes/viajes/50/registro', headers=headers, json={'tipo_registro':'ingreso'})
        self.assertEqual(r.status_code, 400, r.get_json())
        r = client.put('/api/choferes/viajes/50/aceptar', headers=headers)
        self.assertEqual(r.status_code, 200, r.get_json())
        r = client.post('/api/choferes/viajes/50/registro', headers=headers, json={'tipo_registro':'ingreso'})
        self.assertEqual(r.status_code, 201, r.get_json())
        from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=50).delete()
        db.session.commit()

    def test_cambio_importante_fallido_revierte_aceptacion_y_aviso(self):
        with patch.object(db.session, 'commit', side_effect=RuntimeError('Fallo de prueba')), patch('controllers.operador_controller.logger'):
            r, codigo = self.editar({'destino':'No guardar'})
        self.assertEqual(codigo, 500, r.get_json())
        viaje = db.session.get(ViajeModel, 50)
        self.assertEqual(viaje.estado, 'aceptado')
        self.assertEqual(viaje.destino, 'B')
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.assertEqual(ViajeCambioModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_cambio_destino_en_curso_no_vuelve_a_pendiente(self):
        viaje = db.session.get(ViajeModel, 50)
        viaje.estado = 'en curso'
        db.session.commit()
        r, codigo = self.editar({'destino':'Desvío autorizado'})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(viaje.estado, 'en curso')
        aviso = NotificacionModel.query.one()
        self.assertIn('actualizados', aviso.mensaje)
        self.assertNotIn('aceptá', aviso.mensaje)

    def test_creacion_exige_licencia_hasta_salida_en_ambas_rutas(self):
        from utils.fecha_operativa import hoy_operativo
        salida = hoy_operativo()+timedelta(days=7)
        db.session.get(ViajeModel, 50).estado = 'cancelado'
        db.session.get(CamionModel, 90).estado = 'disponible'
        db.session.get(ChoferModel, 91).vencimientoLicencia = salida-timedelta(days=1)
        db.session.commit()
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        datos = {'origen':'A', 'destino':'B', 'fecha_salida':salida.isoformat(),
                 'Chofer_Usuario_idUsuario':91, 'Camion_id_camion':90, 'recorrido':10}
        for ruta in ['/api/operador/viajes', '/api/viaje']:
            r = self.fixture.app.test_client().post(ruta, headers={'Authorization':'Bearer '+token}, json=datos)
            self.assertEqual(r.status_code, 409, r.get_json())
            self.assertIn('fecha de salida', r.get_json()['mensaje'])
            self.assertEqual(ViajeModel.query.filter(ViajeModel.id_viaje>50).count(), 0)
            self.assertEqual(db.session.get(CamionModel, 90).estado, 'disponible')
            self.assertEqual(NotificacionModel.query.count(), 0)
            self.assertEqual(ViajeCambioModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_reprogramar_rechaza_licencia_insuficiente_sin_mutar(self):
        from utils.fecha_operativa import hoy_operativo
        db.session.get(ChoferModel, 91).vencimientoLicencia = hoy_operativo()+timedelta(days=1)
        db.session.commit()
        viaje = db.session.get(ViajeModel, 50)
        salida_original = viaje.fecha_salida
        r, codigo = self.editar({'fecha_salida':(hoy_operativo()+timedelta(days=7)).isoformat()})
        self.assertEqual(codigo, 409, r.get_json())
        self.assertEqual(viaje.fecha_salida, salida_original)
        self.assertEqual(viaje.estado, 'aceptado')
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.assertEqual(ViajeCambioModel.query.count(), 0)
        # Las observaciones siguen pudiendo editarse.
        self.assertEqual(self.editar({'observaciones':'Confirmar renovación'})[1], 200)

    def test_reasignar_comprueba_la_fecha_final_del_formulario(self):
        from utils.fecha_operativa import hoy_operativo
        salida = hoy_operativo()+timedelta(days=7)
        viaje = db.session.get(ViajeModel, 50)
        viaje.fecha_salida = salida
        db.session.get(ViajeModel, 2).estado = 'finalizado'
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.get(ChoferModel, 1).vencimientoLicencia = salida-timedelta(days=1)
        db.session.commit()
        r, codigo = self.editar({'Chofer_Usuario_idUsuario':1})
        self.assertEqual(codigo, 409, r.get_json())
        self.assertEqual(viaje.Chofer_Usuario_idUsuario, 91)
        self.assertEqual(viaje.estado, 'aceptado')
        self.assertEqual(NotificacionModel.query.count(), 0)
        # Si se adelanta a una fecha cubierta, puede reasignarse conjuntamente.
        r, codigo = self.editar({'Chofer_Usuario_idUsuario':1, 'fecha_salida':(salida-timedelta(days=1)).isoformat()})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(viaje.Chofer_Usuario_idUsuario, 1)
        self.assertEqual(viaje.estado, 'pendiente')

    def test_licencia_valida_el_mismo_dia_de_salida(self):
        from utils.fecha_operativa import hoy_operativo
        salida = hoy_operativo()+timedelta(days=7)
        db.session.get(ChoferModel, 91).vencimientoLicencia = salida
        db.session.commit()
        r, codigo = self.editar({'fecha_salida':salida.isoformat()})
        self.assertEqual(codigo, 200, r.get_json())
        self.assertEqual(db.session.get(ViajeModel, 50).estado, 'pendiente')

    def test_descripcion_larga_o_expandida_no_guarda_reporte(self):
        viaje = db.session.get(ViajeModel, 50)
        viaje.estado = 'en curso'
        db.session.commit()
        token = create_access_token(identity='91', additional_claims={'rol':'chofer'})
        client = self.fixture.app.test_client()
        cantidad = ReporteModel.query.count()
        for texto in ['A'*201, '"'*34, '&'*41]:
            r = client.post('/api/reportes', headers={'Authorization':'Bearer '+token},
                json={'Camion_id_camion':90, 'descripcion':texto})
            self.assertEqual(r.status_code, 400, r.get_json())
            self.assertIn('larga', r.get_json()['mensaje'])
            self.assertEqual(ReporteModel.query.count(), cantidad)
            self.assertEqual(NotificacionModel.query.count(), 0)
            self.assertEqual(viaje.estado, 'en curso')
            self.assertEqual(db.session.get(CamionModel, 90).estado, 'en viaje')
        self.enviar_push.assert_not_called()

    def test_nota_larga_o_expandida_no_resuelve_ni_modifica_reporte(self):
        db.session.get(UsuarioModel, 3).estado = 'activo'
        reporte = db.session.get(ReporteModel, 2)
        original = (reporte.estado, reporte.nota_reparacion, reporte.fecha_resolucion)
        reporte.estado = 'en revision'
        reporte.nota_reparacion = 'Original'
        reporte.fecha_resolucion = None
        db.session.commit()
        token = create_access_token(identity='3', additional_claims={'rol':'mecanico'})
        try:
            for nota in ['B'*256, '"'*43, '&'*52]:
                r = self.fixture.app.test_client().put('/api/mecanico/reportes/2/resolver',
                    headers={'Authorization':'Bearer '+token}, json={'nota_reparacion':nota})
                self.assertEqual(r.status_code, 400, r.get_json())
                self.assertIn('larga', r.get_json()['mensaje'])
                self.assertEqual(reporte.estado, 'en revision')
                self.assertEqual(reporte.nota_reparacion, 'Original')
                self.assertIsNone(reporte.fecha_resolucion)
                self.assertEqual(NotificacionModel.query.count(), 0)
            self.enviar_push.assert_not_called()
        finally:
            reporte.estado, reporte.nota_reparacion, reporte.fecha_resolucion = original
            db.session.commit()

    def test_textos_en_limite_se_conservan_completos_incluso_con_simbolos(self):
        db.session.get(ViajeModel, 50).estado = 'en curso'
        db.session.get(UsuarioModel, 3).estado = 'activo'
        db.session.commit()
        client = self.fixture.app.test_client()
        driver = create_access_token(identity='91', additional_claims={'rol':'chofer'})
        mecanico = create_access_token(identity='3', additional_claims={'rol':'mecanico'})
        for descripcion, nota in [('D'*200, 'N'*255), ('D'*194+'"', 'N'*249+'"')]:
            r = client.post('/api/reportes', headers={'Authorization':'Bearer '+driver},
                json={'Camion_id_camion':90, 'descripcion':descripcion})
            self.assertEqual(r.status_code, 201, r.get_json())
            reporte = db.session.get(ReporteModel, r.get_json()['reporte']['id_reporte'])
            self.assertEqual(len(reporte.descripcion), 200)
            self.assertEqual(r.get_json()['reporte']['descripcion'], descripcion)
            reporte.Mecanico_Usuario_idUsuario = 3
            reporte.estado = 'en revision'
            db.session.commit()
            r = client.put('/api/mecanico/reportes/'+str(reporte.id_reporte)+'/resolver',
                headers={'Authorization':'Bearer '+mecanico}, json={'nota_reparacion':nota})
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(len(reporte.nota_reparacion), 255)
            self.assertEqual(r.get_json()['reporte']['nota_reparacion'], nota)
            aviso = NotificacionModel.query.filter_by(tipo='reporte_resuelto').order_by(NotificacionModel.id_notificacion.desc()).first()
            self.assertLessEqual(len(aviso.mensaje), 255)
            self.assertIn('nota completa', aviso.mensaje)

    def test_estadisticas_cuentan_aceptados_y_estados_suman_total_segun_alcance(self):
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        campos = {'pendiente':'viajes_pendientes', 'aceptado':'viajes_aceptados',
                  'en curso':'viajes_en_curso', 'finalizado':'viajes_finalizados', 'cancelado':'viajes_cancelados'}
        viaje = db.session.get(ViajeModel, 50)
        mes = viaje.fecha_salida.strftime('%Y-%m')
        for creador in [2, 90]:
            for estado, campo in campos.items():
                viaje.OperadorLogistico_Usuario_idUsuario = creador
                viaje.estado = estado
                db.session.commit()
                for alcance in ['todos', 'mios']:
                    with self.subTest(creador=creador, estado=estado, alcance=alcance):
                        r = self.fixture.app.test_client().get('/api/operador/estadisticas?mes='+mes+'&alcance='+alcance,
                            headers={'Authorization':'Bearer '+token})
                        self.assertEqual(r.status_code, 200, r.get_json())
                        resumen = r.get_json()['resumen']
                        esperado = int(alcance=='todos' or creador==90)
                        self.assertEqual(resumen['total_viajes'], esperado)
                        self.assertEqual(resumen[campo], esperado)
                        self.assertEqual(sum(resumen[c] for c in campos.values()), resumen['total_viajes'])
                        self.assertEqual(len(r.get_json()['ultimos_viajes']), esperado)

    def test_estadisticas_mes_vacio_incluye_aceptados_en_cero(self):
        token = create_access_token(identity='90', additional_claims={'rol':'operador'})
        r = self.fixture.app.test_client().get('/api/operador/estadisticas?mes=2024-01&alcance=todos',
            headers={'Authorization':'Bearer '+token})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()['resumen']['viajes_aceptados'], 0)
        self.assertEqual(r.get_json()['resumen']['total_viajes'], 0)

    def aceptar_como_chofer(self, identidad='91', accion='aceptar'):
        token = create_access_token(identity=identidad, additional_claims={'rol':'chofer'})
        return self.fixture.app.test_client().put('/api/choferes/viajes/50/'+accion,
            headers={'Authorization':'Bearer '+token})

    def test_aceptacion_avisa_solo_al_operador_creador_sin_iniciar_horas(self):
        from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
        for accion in ['aceptar', 'iniciar']:
            NotificacionModel.query.delete()
            viaje = db.session.get(ViajeModel, 50)
            viaje.estado = 'pendiente'
            db.session.commit()
            eventos = []
            commit = db.session.commit
            def guardar():
                commit()
                eventos.append('commit')
            self.enviar_push.reset_mock()
            self.enviar_push.side_effect = lambda: eventos.append('push')
            with patch.object(db.session, 'commit', side_effect=guardar):
                r = self.aceptar_como_chofer(accion=accion)
            self.assertEqual(r.status_code, 200, r.get_json())
            self.assertEqual(eventos, ['commit', 'push'])
            self.assertEqual(viaje.estado, 'aceptado')
            aviso = NotificacionModel.query.one()
            self.assertEqual(aviso.Usuario_idUsuario, 2)
            self.assertEqual(aviso.tipo, 'viaje_aceptado')
            self.assertIn('Segundo Chofer', aviso.mensaje)
            self.assertIn('#50', aviso.mensaje)
            self.assertIn('pendiente de salida', aviso.mensaje)
            self.assertFalse(aviso.leida)
            self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=50).count(), 0)
            self.assertIsNone(r.get_json()['viaje']['tiempo_viaje']['segundos_confirmados'])
            self.assertEqual(self.aceptar_como_chofer(accion=accion).status_code, 400)
            self.assertEqual(NotificacionModel.query.count(), 1)
            self.enviar_push.assert_called_once()

    def test_aceptacion_fallida_no_guarda_estado_ni_aviso(self):
        viaje = db.session.get(ViajeModel, 50)
        viaje.estado = 'pendiente'
        db.session.commit()
        with patch.object(db.session, 'commit', side_effect=RuntimeError('Prueba')), patch('controllers.chofer_controller.logger'):
            r = self.aceptar_como_chofer()
        self.assertEqual(r.status_code, 500, r.get_json())
        self.assertEqual(viaje.estado, 'pendiente')
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_otro_chofer_no_acepta_ni_genera_aviso(self):
        db.session.get(UsuarioModel, 1).estado = 'activo'
        db.session.get(ViajeModel, 50).estado = 'pendiente'
        db.session.commit()
        r = self.aceptar_como_chofer('1')
        self.assertEqual(r.status_code, 404, r.get_json())
        self.assertEqual(db.session.get(ViajeModel, 50).estado, 'pendiente')
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.enviar_push.assert_not_called()

    def test_nueva_aceptacion_por_cambio_importante_genera_otro_aviso(self):
        db.session.get(ViajeModel, 50).estado = 'pendiente'
        db.session.commit()
        self.assertEqual(self.aceptar_como_chofer().status_code, 200)
        self.assertEqual(self.editar({'destino':'Nuevo destino'})[1], 200)
        self.assertEqual(self.aceptar_como_chofer().status_code, 200)
        self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=2, tipo='viaje_aceptado').count(), 2)
        self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=90).count(), 0)

    def preparar_reasignacion_mecanico(self):
        from models.mecanico_model import MecanicoModel
        from models.administrador_model import AdministradorModel
        reporte = db.session.get(ReporteModel, 2)
        original = (reporte.estado, reporte.Mecanico_Usuario_idUsuario)
        db.session.get(UsuarioModel, 3).estado = 'activo'
        db.session.add(UsuarioModel(id_usuario=77, username='mecanico_reasignacion', password='x',
            nombre='Nuevo', apellido='Mecánico', rol='mecanico', estado='activo'))
        db.session.add(MecanicoModel(Usuario_idUsuario=77, legajo='M77', especialidad='Motor'))
        db.session.add(UsuarioModel(id_usuario=99, username='admin_reasignacion', password='x',
            nombre='QA', apellido='Admin', rol='admin', estado='activo'))
        db.session.add(AdministradorModel(Usuario_idUsuario=99, legajo='A99'))
        db.session.commit()
        return original

    def limpiar_reasignacion_mecanico(self, original):
        from models.mecanico_model import MecanicoModel
        from models.administrador_model import AdministradorModel
        db.session.rollback()
        reporte = db.session.get(ReporteModel, 2)
        reporte.estado, reporte.Mecanico_Usuario_idUsuario = original
        NotificacionModel.query.delete()
        db.session.flush()
        MecanicoModel.query.filter_by(Usuario_idUsuario=77).delete()
        AdministradorModel.query.filter_by(Usuario_idUsuario=99).delete()
        UsuarioModel.query.filter(UsuarioModel.id_usuario.in_([77,99])).delete()
        db.session.commit()
        db.session.info.pop('push_pendientes', None)

    def reasignar_mecanico(self, rol):
        token = create_access_token(identity='99' if rol=='admin' else '90', additional_claims={'rol':rol})
        ruta = '/api/reportes/2/estado' if rol=='admin' else '/api/reportes/2/asignar-mecanico'
        return self.fixture.app.test_client().put(ruta, headers={'Authorization':'Bearer '+token},
            json={'estado':'en revision', 'Mecanico_Usuario_idUsuario':77})

    def test_reasignacion_mecanico_avisa_a_ambos_y_no_duplica_al_repetir(self):
        original = self.preparar_reasignacion_mecanico()
        try:
            for rol in ['admin', 'operador']:
                reporte = db.session.get(ReporteModel, 2)
                reporte.estado = 'en revision'
                reporte.Mecanico_Usuario_idUsuario = 3
                NotificacionModel.query.delete()
                db.session.commit()
                r = self.reasignar_mecanico(rol)
                self.assertEqual(r.status_code, 200, r.get_json())
                self.assertEqual(reporte.Mecanico_Usuario_idUsuario, 77)
                anterior = NotificacionModel.query.filter_by(Usuario_idUsuario=3).one()
                nuevo = NotificacionModel.query.filter_by(Usuario_idUsuario=77).one()
                self.assertEqual(anterior.tipo, 'reporte_reasignado')
                self.assertIn('#2', anterior.mensaje)
                self.assertEqual(nuevo.tipo, 'reporte_asignado')
                self.assertEqual(self.reasignar_mecanico(rol).status_code, 200)
                self.assertEqual(NotificacionModel.query.count(), 2)
        finally:
            self.limpiar_reasignacion_mecanico(original)

    def test_no_se_reasigna_reporte_cerrado_aunque_el_mecanico_sea_el_mismo(self):
        original = self.preparar_reasignacion_mecanico()
        try:
            for rol in ['admin', 'operador']:
                for estado in ['resuelto', 'cancelado']:
                    reporte = db.session.get(ReporteModel, 2)
                    reporte.estado = estado
                    reporte.Mecanico_Usuario_idUsuario = 77
                    db.session.commit()
                    r = self.reasignar_mecanico(rol)
                    self.assertIn(r.status_code, [400,409], r.get_json())
                    self.assertEqual(reporte.estado, estado)
                    self.assertEqual(NotificacionModel.query.count(), 0)
        finally:
            self.limpiar_reasignacion_mecanico(original)

    def test_fallo_en_aviso_anterior_o_commit_revierte_reasignacion_y_avisos(self):
        original = self.preparar_reasignacion_mecanico()
        try:
            for rol in ['admin', 'operador']:
                for fallo in ['aviso_anterior', 'commit']:
                    reporte = db.session.get(ReporteModel, 2)
                    reporte.estado = 'en revision'
                    reporte.Mecanico_Usuario_idUsuario = 3
                    NotificacionModel.query.delete()
                    db.session.commit()
                    self.enviar_push.reset_mock()
                    if fallo=='commit':
                        simular = patch.object(db.session, 'commit', side_effect=RuntimeError('Prueba'))
                    else:
                        simular = patch('controllers.reporte_controller.NotificacionService.crear', side_effect=RuntimeError('Prueba'))
                    with simular, patch('controllers.reporte_controller.logger'):
                        r = self.reasignar_mecanico(rol)
                    self.assertEqual(r.status_code, 500, r.get_json())
                    self.assertEqual(reporte.Mecanico_Usuario_idUsuario, 3)
                    self.assertEqual(reporte.estado, 'en revision')
                    self.assertEqual(NotificacionModel.query.count(), 0)
                    self.enviar_push.assert_not_called()
        finally:
            self.limpiar_reasignacion_mecanico(original)


    def test_observaciones_largas_no_guardan_edicion_parcial(self):
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        client = self.fixture.app.test_client()
        original = db.session.get(ViajeModel,50).to_dict()
        for texto in ['A'*201, 'Entrega "confirmada" & recibida. '*6]:
            r = client.put('/api/operador/viajes/50',headers={'Authorization':'Bearer '+token},json={'observaciones':texto,'origen':'No guardar','recorrido':99})
            self.assertEqual(r.status_code,400,r.get_json())
            self.assertIn('observaciones',r.get_json()['mensaje'])
            db.session.remove()
            viaje = db.session.get(ViajeModel,50)
            self.assertEqual((viaje.estado,viaje.origen,viaje.recorrido,viaje.observaciones),(original['estado'],original['origen'],original['recorrido'],original['observaciones']))
            self.assertEqual(ViajeCambioModel.query.filter_by(id_viaje=50).count(),0)
            self.assertEqual(NotificacionModel.query.count(),0)
            self.enviar_push.assert_not_called()

    def test_observaciones_en_limite_y_vacias_permiten_editar(self):
        from html import escape
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        for texto in ['A'*200, "'"*33, '']:
            r = self.fixture.app.test_client().put('/api/operador/viajes/50',headers={'Authorization':'Bearer '+token},json={'observaciones':texto})
            self.assertEqual(r.status_code,200,r.get_json())
            db.session.remove()
            viaje = db.session.get(ViajeModel,50)
            self.assertEqual(viaje.observaciones,escape(texto))
            self.assertEqual(viaje.estado,'aceptado')

    def test_creacion_comparte_limite_de_observaciones(self):
        from src.Viaje import Viaje
        from utils.input_sanitizer import InputSanitizer
        datos = {'fecha_salida':date.today().isoformat(),'origen':'A','destino':'B','recorrido':10}
        for texto, esperado in [('A'*200,True),('A'*201,False),("'"*34,False),('',True),(None,True)]:
            valido, mensaje = Viaje.validar_datos_viaje({**datos,'observaciones':InputSanitizer.texto(texto)})
            self.assertEqual(valido,esperado,mensaje)


    def test_ids_asignacion_invalidos_no_modifican_viaje_ni_recursos(self):
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        client = self.fixture.app.test_client()
        original = db.session.get(ViajeModel,50).to_dict()
        invalidos = [1.9,91.9,True,False,0,-1,None,[],{},'1.9','1e0','١','¹',2147483648,'9'*5000]
        for campo in ['Camion_id_camion','Chofer_Usuario_idUsuario']:
            for valor in invalidos:
                with self.subTest(campo=campo,valor=str(valor)[:20]):
                    r = client.put('/api/operador/viajes/50',headers={'Authorization':'Bearer '+token},json={campo:valor,'observaciones':'No guardar'})
                    self.assertEqual(r.status_code,400,r.get_json())
                    db.session.remove()
                    viaje = db.session.get(ViajeModel,50)
                    self.assertEqual((viaje.Camion_id_camion,viaje.Chofer_Usuario_idUsuario,viaje.estado,viaje.observaciones),(original['Camion_id_camion'],original['Chofer_Usuario_idUsuario'],original['estado'],original['observaciones']))
                    self.assertEqual(db.session.get(CamionModel,90).estado,'en viaje')
                    self.assertEqual(db.session.get(CamionModel,1).estado,'disponible')
                    self.assertEqual(ViajeCambioModel.query.filter_by(id_viaje=50).count(),0)
                    self.assertEqual(NotificacionModel.query.count(),0)
                    self.enviar_push.assert_not_called()

    def test_ids_enteros_en_texto_o_numero_conservan_asignacion(self):
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        for chofer, camion in [(91,90),('91','90'),(' 91 ',' 90 ')]:
            r = self.fixture.app.test_client().put('/api/operador/viajes/50',headers={'Authorization':'Bearer '+token},json={'Chofer_Usuario_idUsuario':chofer,'Camion_id_camion':camion})
            self.assertEqual(r.status_code,200,r.get_json())
            db.session.remove()
            viaje = db.session.get(ViajeModel,50)
            self.assertEqual((viaje.Chofer_Usuario_idUsuario,viaje.Camion_id_camion,viaje.estado),(91,90,'aceptado'))

    def test_camion_decimal_disponible_no_se_asigna_por_truncamiento(self):
        db.session.get(ViajeModel,2).estado = 'finalizado'
        db.session.commit()
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        r = self.fixture.app.test_client().put('/api/operador/viajes/50',headers={'Authorization':'Bearer '+token},json={'Camion_id_camion':1.9})
        self.assertEqual(r.status_code,400,r.get_json())
        db.session.remove()
        self.assertEqual(db.session.get(ViajeModel,50).Camion_id_camion,90)
        self.assertEqual(db.session.get(CamionModel,90).estado,'en viaje')
        self.assertEqual(db.session.get(CamionModel,1).estado,'disponible')


    def test_creacion_rechaza_ids_invalidos_en_ambas_rutas_y_aliases(self):
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        client = self.fixture.app.test_client()
        db.session.get(ViajeModel,50).estado = 'cancelado'
        db.session.get(CamionModel,90).estado = 'disponible'
        db.session.commit()
        original = ViajeModel.query.count()
        base = {'origen':'A','destino':'B','fecha_salida':date.today().isoformat(),'recorrido':10,'Chofer_Usuario_idUsuario':91,'Camion_id_camion':90}
        for ruta in ['/api/operador/viajes','/api/viaje']:
            campos = ['Chofer_Usuario_idUsuario','Camion_id_camion']
            if ruta == '/api/viaje':
                campos += ['id_chofer','id_camion','id_operador','OperadorLogistico_Usuario_idUsuario']
            for campo in campos:
                for valor in [91.9,90.9,True,False,None,0,-1,[],{},'3.9','٣',2147483648,'9'*5000]:
                    with self.subTest(ruta=ruta,campo=campo,valor=str(valor)[:20]):
                        r = client.post(ruta,json={**base,campo:valor},headers={'Authorization':'Bearer '+token})
                        self.assertEqual(r.status_code,400,r.get_json())
                        db.session.remove()
                        self.assertEqual(ViajeModel.query.count(),original)
                        self.assertEqual(db.session.get(CamionModel,90).estado,'disponible')
                        self.assertEqual(NotificacionModel.query.count(),0)
                        self.enviar_push.assert_not_called()

    def test_creacion_acepta_ids_validos_como_texto_en_ambas_rutas(self):
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        for ruta in ['/api/operador/viajes','/api/viaje']:
            for anterior in ViajeModel.query.filter(ViajeModel.id_viaje>=50).all():
                anterior.estado = 'cancelado'
            db.session.get(CamionModel,90).estado = 'disponible'
            db.session.commit()
            datos = {'origen':'A','destino':'B','fecha_salida':date.today().isoformat(),'recorrido':10,'Chofer_Usuario_idUsuario':'91','Camion_id_camion':'90'}
            r = self.fixture.app.test_client().post(ruta,json=datos,headers={'Authorization':'Bearer '+token})
            self.assertEqual(r.status_code,201,r.get_json())
            db.session.remove()
            viaje = ViajeModel.query.order_by(ViajeModel.id_viaje.desc()).first()
            self.assertEqual((viaje.Chofer_Usuario_idUsuario,viaje.Camion_id_camion,viaje.estado),(91,90,'pendiente'))
            self.assertEqual(db.session.get(CamionModel,90).estado,'en viaje')


    def test_creacion_recorrido_invalido_no_crea_ni_reserva(self):
        from src.Viaje import Viaje
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        db.session.get(ViajeModel,50).estado = 'cancelado'
        db.session.get(CamionModel,90).estado = 'disponible'
        db.session.commit()
        cantidad = ViajeModel.query.count()
        datos = {'origen':'A','destino':'B','fecha_salida':date.today().isoformat(),'Chofer_Usuario_idUsuario':91,'Camion_id_camion':90}
        invalidos = ['Infinity','-Infinity','NaN','1e999',True,False,None,[],{},'texto',-1,10**400]
        for ruta in ['/api/operador/viajes','/api/viaje']:
            for recorrido in invalidos:
                with self.subTest(ruta=ruta,recorrido=str(recorrido)[:20]):
                    self.assertFalse(Viaje.numero_no_negativo(recorrido))
                    r = self.fixture.app.test_client().post(ruta,json={**datos,'recorrido':recorrido},headers={'Authorization':'Bearer '+token})
                    self.assertEqual(r.status_code,400,r.get_json())
                    self.assertIn('recorrido',r.get_json()['mensaje'])
                    db.session.remove()
                    self.assertEqual(ViajeModel.query.count(),cantidad)
                    self.assertEqual(db.session.get(CamionModel,90).estado,'disponible')
                    self.assertEqual(NotificacionModel.query.count(),0)
                    self.enviar_push.assert_not_called()

    def test_creacion_recorrido_cero_decimal_y_omitido(self):
        token = create_access_token(identity='90',additional_claims={'rol':'operador'})
        for ruta in ['/api/operador/viajes','/api/viaje']:
            for valor in [0,12.5,'12.5','omitido']:
                for viaje in ViajeModel.query.filter(ViajeModel.id_viaje>=50).all():
                    viaje.estado = 'cancelado'
                db.session.get(CamionModel,90).estado = 'disponible'
                db.session.commit()
                datos = {'origen':'A','destino':'B','fecha_salida':date.today().isoformat(),'Chofer_Usuario_idUsuario':91,'Camion_id_camion':90}
                if valor != 'omitido':
                    datos['recorrido'] = valor
                r = self.fixture.app.test_client().post(ruta,json=datos,headers={'Authorization':'Bearer '+token})
                self.assertEqual(r.status_code,201,r.get_json())
                db.session.remove()
                viaje = ViajeModel.query.order_by(ViajeModel.id_viaje.desc()).first()
                self.assertEqual(viaje.recorrido,0 if valor=='omitido' else float(valor))
                self.assertEqual(db.session.get(CamionModel,90).estado,'en viaje')
