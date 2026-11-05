import unittest
from datetime import date, timedelta
from unittest.mock import patch
from flask_jwt_extended import JWTManager, create_access_token
from routes.notificacion_routes import notificacion_routes

from db_instance import db
from models.chofer_model import ChoferModel
from models.usuario_model import UsuarioModel
from models.notificacion_model import NotificacionModel
from services.avisos_licencias_service import generar_aviso_licencia


class AvisosLicenciasTest(unittest.TestCase):
    HOY = date(2026, 11, 5)

    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        cls.fixture.app.config["JWT_SECRET_KEY"] = "test-only-license-notification-secret"
        JWTManager(cls.fixture.app)
        cls.fixture.app.register_blueprint(notificacion_routes)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.remove()
        NotificacionModel.query.delete()
        usuario = db.session.get(UsuarioModel, 1)
        usuario.estado = "activo"
        usuario.rol = "chofer"
        self.chofer = db.session.get(ChoferModel, 1)
        self.chofer.vencimientoLicencia = self.HOY + timedelta(days=90)
        db.session.commit()
        emisor = patch("services.avisos_licencias_service.NotificacionService.enviar_push_pendientes")
        self.push = emisor.start()
        self.addCleanup(emisor.stop)

    def tearDown(self):
        db.session.rollback()
        db.session.info.pop("push_pendientes", None)
        db.session.remove()

    def test_limites_y_mensaje_con_fecha_real(self):
        for dias, etapa in [(91, None), (90, 90), (31, 90), (30, 30), (8, 30), (7, 7), (1, 7), (0, 0), (-1, 0)]:
            with self.subTest(dias=dias):
                # Cada escenario usa una sesión nueva: SQLite reutiliza el ID
                # eliminado y el aviso anterior no debe seguir en el identity map.
                db.session.info.pop("push_pendientes", None)
                db.session.remove()
                self.chofer = db.session.get(ChoferModel, 1)
                NotificacionModel.query.delete()
                self.chofer.vencimientoLicencia = self.HOY + timedelta(days=dias)
                db.session.commit()
                self.assertEqual(generar_aviso_licencia(1, self.HOY), int(etapa is not None))
                aviso = NotificacionModel.query.first()
                if etapa is not None:
                    self.assertEqual(aviso.Usuario_idUsuario, 1)
                    self.assertTrue(aviso.tipo.endswith(f":{etapa}"))
                    self.assertIn(self.chofer.vencimientoLicencia.strftime("%d/%m/%Y"), aviso.mensaje)
                    self.assertFalse(aviso.leida)
                    if dias > 0:
                        self.assertIn(f"{dias} días", aviso.mensaje)
                    elif dias < 0:
                        self.assertEqual(aviso.titulo, "Licencia vencida")
                    else:
                        self.assertEqual(aviso.titulo, "Tu licencia vence hoy")

    def test_no_repite_etapas_aunque_esten_leidas(self):
        for avance in [0, 1, 60, 61, 83, 84, 90, 91]:
            generar_aviso_licencia(1, self.HOY + timedelta(days=avance))
            NotificacionModel.query.update({"leida": True})
            db.session.commit()
        self.assertEqual(NotificacionModel.query.count(), 4)

    def test_recupera_solo_etapa_actual_si_no_corrio_antes(self):
        self.chofer.vencimientoLicencia = self.HOY + timedelta(days=20)
        db.session.commit()
        self.assertEqual(generar_aviso_licencia(1, self.HOY), 1)
        self.assertTrue(NotificacionModel.query.one().tipo.endswith(":30"))

    def test_renovacion_cambia_el_ciclo_sin_borrar_historial(self):
        self.assertEqual(generar_aviso_licencia(1, self.HOY), 1)
        self.chofer.vencimientoLicencia = self.HOY + timedelta(days=365)
        db.session.commit()
        self.assertEqual(generar_aviso_licencia(1, self.HOY + timedelta(days=1)), 0)
        self.assertEqual(generar_aviso_licencia(1, self.HOY + timedelta(days=275)), 1)
        self.assertEqual(NotificacionModel.query.count(), 2)

    def test_no_avisa_cuentas_inactivas_pendientes_ni_otros_roles(self):
        usuario = db.session.get(UsuarioModel, 1)
        for estado, rol in [("inactivo", "chofer"), ("pendiente", "chofer"), ("activo", "operador")]:
            usuario.estado, usuario.rol = estado, rol
            db.session.commit()
            self.assertEqual(generar_aviso_licencia(1, self.HOY), 0)
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_usuario_sin_chofer_no_genera_avisos(self):
        self.assertEqual(generar_aviso_licencia(999, self.HOY), 0)
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.push.assert_not_called()

    def test_push_se_envia_despues_de_confirmar(self):
        eventos = []
        commit = db.session.commit
        def confirmar():
            commit()
            eventos.append("commit")
        self.push.side_effect = lambda: eventos.append("push")
        with patch.object(db.session, "commit", side_effect=confirmar):
            generar_aviso_licencia(1, self.HOY)
        self.assertEqual(eventos, ["commit", "push"])

    def test_fallo_guardado_revierte_y_permite_reintentar(self):
        with patch.object(db.session, "commit", side_effect=RuntimeError("Prueba")):
            with self.assertRaises(RuntimeError):
                generar_aviso_licencia(1, self.HOY)
        self.assertEqual(NotificacionModel.query.count(), 0)
        self.assertNotIn("push_pendientes", db.session.info)
        self.push.assert_not_called()
        self.assertEqual(generar_aviso_licencia(1, self.HOY), 1)

    def consultar(self, identidad='1', rol='chofer'):
        token = create_access_token(identity=identidad, additional_claims={'rol':rol})
        with patch('services.avisos_licencias_service.hoy_operativo', return_value=self.HOY):
            return self.fixture.app.test_client().get('/api/notificaciones',
                headers={'Authorization':'Bearer '+token})

    def test_consulta_devuelve_aviso_nuevo_en_la_misma_respuesta_y_no_duplica(self):
        for _ in range(3):
            r = self.consultar()
            self.assertEqual(r.status_code, 200, r.get_json())
            avisos = r.get_json()['notificaciones']
            self.assertEqual(len(avisos), 1)
            self.assertTrue(avisos[0]['tipo'].startswith('licencia:'))
            self.assertEqual(avisos[0]['Usuario_idUsuario'], 1)
        self.assertEqual(NotificacionModel.query.count(), 1)
        self.push.assert_called_once()

    def test_consulta_de_otro_rol_no_ejecuta_revision(self):
        db.session.get(UsuarioModel, 2).estado = 'activo'
        db.session.commit()
        with patch('controllers.notificacion_controller.generar_aviso_licencia') as generar:
            r = self.consultar('2', 'operador')
        self.assertEqual(r.status_code, 200, r.get_json())
        generar.assert_not_called()
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_una_cuenta_desactivada_no_genera_notificacion(self):
        db.session.get(UsuarioModel, 1).estado = 'inactivo'
        db.session.commit()
        r = self.consultar()
        self.assertEqual(r.status_code, 401, r.get_json())
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_fallo_recordatorio_no_bloquea_notificaciones_existentes(self):
        NotificacionModel.query.delete()
        from services.notificacion_service import NotificacionService
        NotificacionService.crear(1, 'Aviso anterior', 'Tu viaje fue actualizado', 'viaje_actualizado')
        db.session.commit()
        with patch('services.avisos_licencias_service.NotificacionService.crear', side_effect=RuntimeError('Prueba')), patch('controllers.notificacion_controller.logger'):
            r = self.consultar()
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual([n['titulo'] for n in r.get_json()['notificaciones']], ['Aviso anterior'])

    def test_solo_revisa_la_licencia_del_usuario_que_consulta(self):
        db.session.add(UsuarioModel(id_usuario=77, username='licencia_otra', password='x', nombre='Otro',
            apellido='Chofer', rol='chofer', estado='activo'))
        db.session.add(ChoferModel(Usuario_idUsuario=77, licencia='LIC0077', legajo='C77', vencimientoLicencia=self.HOY))
        db.session.commit()
        try:
            self.chofer.vencimientoLicencia = self.HOY + timedelta(days=365)
            db.session.commit()
            self.assertEqual(self.consultar().status_code, 200)
            self.assertEqual(NotificacionModel.query.count(), 0)
        finally:
            ChoferModel.query.filter_by(Usuario_idUsuario=77).delete()
            UsuarioModel.query.filter_by(id_usuario=77).delete()
            db.session.commit()
