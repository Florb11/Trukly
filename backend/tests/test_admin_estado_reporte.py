import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch
from db_instance import db
from models.reporte_model import ReporteModel
from models.usuario_model import UsuarioModel
from models.notificacion_model import NotificacionModel
from controllers.reporte_controller import ReporteController
from src.ReporteFalla import ReporteFalla


class AdminEstadoReporteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        db.session.get(UsuarioModel, 3).estado = "activo"
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.add(ReporteModel(id_reporte=80, fecha_hora=datetime(2026, 10, 29), descripcion="Falla de prueba", estado="pendiente", Camion_id_camion=1, Chofer_Usuario_idUsuario=1))
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        NotificacionModel.query.delete()
        ReporteModel.query.filter_by(id_reporte=80).delete()
        db.session.get(UsuarioModel, 3).estado = "activo"
        db.session.commit()
        db.session.info.pop("push_pendientes", None)

    def cambiar(self, datos, rol="admin"):
        admin = SimpleNamespace(cambiar_estado_reporte=lambda reporte, estado: reporte.cambiar_estado(estado))
        with self.fixture.app.test_request_context("/", method="PUT", json=datos), patch("controllers.reporte_controller.AuthService.obtener_rol_actual", return_value=rol), patch("controllers.reporte_controller.obtener_admin_actual_desde_token", return_value=admin), patch("controllers.reporte_controller.NotificacionService.enviar_push_pendientes"):
            respuesta, codigo = ReporteController.cambiar_estado_reporte.__wrapped__(80)
            return respuesta.get_json(), codigo

    def test_revision_necesita_mecanico_tambien_en_dominio(self):
        r, codigo = self.cambiar({"estado": "en revision"})
        self.assertEqual(codigo, 400)
        self.assertEqual(db.session.get(ReporteModel, 80).estado, "pendiente")
        dominio = ReporteFalla.crear_desde_datos({"estado": "pendiente"})
        self.assertFalse(dominio.cambiar_estado("en revision"))

    def test_asignacion_y_estado_juntos_notifican_una_vez(self):
        datos = {"estado": "en revision", "Mecanico_Usuario_idUsuario": 3}
        r, codigo = self.cambiar(datos)
        self.assertEqual(codigo, 200)
        self.assertEqual(r["reporte"]["Mecanico_Usuario_idUsuario"], 3)
        self.assertEqual(r["reporte"]["estado"], "en revision")
        self.assertEqual(r["reporte"]["mecanico_nombre"], "Sol Díaz")
        self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=3).count(), 1)
        self.assertEqual(self.cambiar(datos)[1], 200)
        self.assertEqual(NotificacionModel.query.filter_by(Usuario_idUsuario=3).count(), 1)

    def test_mecanico_inactivo_inexistente_y_rol_incorrecto(self):
        db.session.get(UsuarioModel, 3).estado = "inactivo"
        db.session.commit()
        for id_mecanico in [3, 999, 1, True, 3.5]:
            with self.subTest(id=id_mecanico):
                self.assertEqual(self.cambiar({"estado": "en revision", "Mecanico_Usuario_idUsuario": id_mecanico})[1], 400)
        self.assertIsNone(db.session.get(ReporteModel, 80).Mecanico_Usuario_idUsuario)

    def test_cancelar_requiere_motivo_y_lo_conserva(self):
        for motivo in [None, " ", "x" * 256, True]:
            self.assertEqual(self.cambiar({"estado": "cancelado", "motivo_cancelacion": motivo})[1], 400)
        r, codigo = self.cambiar({"estado": "cancelado", "motivo_cancelacion": " Reporte duplicado "})
        self.assertEqual(codigo, 200)
        self.assertEqual(r["reporte"]["motivo_cancelacion"], "Reporte duplicado")
        self.assertEqual(db.session.get(ReporteModel, 80).motivo_cancelacion, "Reporte duplicado")

    def test_falla_de_notificacion_revierte_asignacion_y_estado(self):
        with patch.object(ReporteController, "notificar_reporte_asignado", side_effect=RuntimeError("prueba")), patch("controllers.reporte_controller.logger"):
            _, codigo = self.cambiar({"estado": "en revision", "Mecanico_Usuario_idUsuario": 3})
        self.assertEqual(codigo, 500)
        r = db.session.get(ReporteModel, 80)
        self.assertEqual(r.estado, "pendiente")
        self.assertIsNone(r.Mecanico_Usuario_idUsuario)
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_operador_conserva_su_flujo_de_cancelacion(self):
        self.assertEqual(self.cambiar({"estado": "cancelado"}, "operador")[1], 200)

    def test_mecanico_no_resuelve_reportes_cerrados_ni_modifica_sus_datos(self):
        from flask import g
        from controllers.mecanico_controller import MecanicoController
        modelo = db.session.get(ReporteModel, 80)
        modelo.Mecanico_Usuario_idUsuario = 3
        for estado in ["cancelado", "resuelto"]:
            modelo.estado = estado
            modelo.nota_reparacion = "Nota original"
            db.session.commit()
            dominio = MecanicoController.crear_objeto_reporte(modelo)
            self.assertFalse(dominio.resolver_por_mecanico(3, "Nueva nota"))
            self.assertEqual(dominio.estado, estado)
            self.assertEqual(dominio.nota_reparacion, "Nota original")
            with self.fixture.app.test_request_context("/", method="PUT", json={"nota_reparacion": "Nueva nota"}), patch.object(MecanicoController, "notificar_reporte_resuelto") as notificar:
                g.mecanico_actual = SimpleNamespace(id_usuario=3)
                respuesta, codigo = MecanicoController.resolver_reporte.__wrapped__(80)
                self.assertEqual(codigo, 409, respuesta.get_json())
                notificar.assert_not_called()
            db.session.refresh(modelo)
            self.assertEqual(modelo.estado, estado)
            self.assertEqual(modelo.nota_reparacion, "Nota original")
            self.assertIsNone(modelo.fecha_resolucion)

    def test_mecanico_puede_seguir_resolviendo_reportes_activos(self):
        for estado in ["pendiente", "en revision"]:
            dominio = ReporteFalla.crear_desde_datos({"estado": estado, "id_mecanico": 3})
            self.assertTrue(dominio.resolver_por_mecanico(3, "Reparación realizada"))
            self.assertEqual(dominio.estado, "resuelto")

    def test_lista_muestra_solo_mecanicos_activos(self):
        with self.fixture.app.test_request_context("/"):
            respuesta, codigo = ReporteController.listar_mecanicos_activos.__wrapped__()
        self.assertEqual(codigo, 200)
        self.assertEqual([m["id_usuario"] for m in respuesta.get_json()["mecanicos"]], [3])
        self.assertNotIn("password", respuesta.get_json()["mecanicos"][0])


if __name__ == "__main__":
    unittest.main()
