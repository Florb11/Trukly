import unittest
from datetime import date
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

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        self.emisor_real = NotificacionService.enviar_push_pendientes
        push = patch('controllers.operador_controller.NotificacionService.enviar_push_pendientes')
        self.enviar_push = push.start()
        self.addCleanup(push.stop)
        db.session.get(ViajeModel, 2).estado = 'en curso'
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
