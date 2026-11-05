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
from src.OperadorLogistico import OperadorLogistico


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
