import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch
from flask import g
from db_instance import db
from models.notificacion_model import NotificacionModel
from models.usuario_model import UsuarioModel
from models.viaje_model import ViajeModel
from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
from services.admin_notificacion_service import AdminNotificacionService as Avisos
from controllers.notificacion_controller import NotificacionController


class AdminNotificacionesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        for id_usuario, estado in [(100, "activo"), (101, "activo"), (102, "inactivo")]:
            db.session.add(UsuarioModel(id_usuario=id_usuario, username=f"admin{id_usuario}", password="x", nombre="Admin", apellido=str(id_usuario), rol="admin", estado=estado))
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def tearDown(self):
        db.session.rollback()
        db.session.info.pop("push_pendientes", None)

    def reporte(self):
        return SimpleNamespace(id_reporte=99, Camion_id_camion=1, Chofer_Usuario_idUsuario=1, descripcion="Ruido en el motor")

    def test_nueva_falla_solo_admins_activos_y_sin_duplicados(self):
        Avisos.nueva_falla(self.reporte())
        Avisos.nueva_falla(self.reporte())
        filas = NotificacionModel.query.all()
        self.assertEqual({fila.Usuario_idUsuario for fila in filas}, {100, 101})
        self.assertEqual(len(filas), 2)
        self.assertIn("Ana García", filas[0].mensaje)
        self.assertIn("AAA111", filas[0].mensaje)
        self.assertEqual(Avisos.enlace(filas[0].tipo), "/dashboardAdmin/reportes?reporte=99")
        filas[0].leida = True
        Avisos.nueva_falla(self.reporte())
        self.assertEqual(NotificacionModel.query.count(), 2)

    def test_cancelacion_incluye_motivo_y_enlace(self):
        v = db.session.get(ViajeModel, 1)
        Avisos.viaje_cancelado(v, "Camión averiado")
        fila = NotificacionModel.query.first()
        self.assertIn("Camión averiado", fila.mensaje)
        self.assertEqual(Avisos.enlace(fila.tipo), "/dashboardAdmin/viajes?viaje=1")

    def test_rollback_descarta_avisos(self):
        Avisos.nueva_falla(self.reporte())
        db.session.flush()
        self.assertEqual(NotificacionModel.query.count(), 2)
        db.session.rollback()
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_cierre_sin_controles_avisa_una_vez(self):
        v = db.session.get(ViajeModel, 1)
        Avisos.revisar_controles(v)
        Avisos.revisar_controles(v)
        filas = NotificacionModel.query.all()
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[0].tipo, "admin_control:1")

    def test_controles_validos_y_viaje_pendiente_no_avisan(self):
        v = db.session.get(ViajeModel, 1)
        for tipo, hora in [("ingreso", 8), ("salida", 10)]:
            db.session.add(RegistroIngresoSalidaModel(Viaje_id_viaje=1, tipo_registro=tipo, fecha_hora=datetime(2026, 9, 15, hora)))
        Avisos.revisar_controles(v)
        v.estado = "pendiente"
        RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=1).delete()
        Avisos.revisar_controles(v)
        self.assertEqual(NotificacionModel.query.count(), 0)

    def test_control_duplicado_genera_alerta(self):
        v = db.session.get(ViajeModel, 1)
        for hora in [8, 9]:
            db.session.add(RegistroIngresoSalidaModel(Viaje_id_viaje=1, tipo_registro="ingreso", fecha_hora=datetime(2026, 9, 15, hora)))
        Avisos.revisar_controles(v)
        self.assertEqual(NotificacionModel.query.count(), 2)

    def test_api_lista_solo_avisos_del_admin_actual(self):
        Avisos.nueva_falla(self.reporte())
        with self.fixture.app.test_request_context("/"):
            g.usuario_actual = db.session.get(UsuarioModel, 100)
            respuesta, codigo = NotificacionController.listar_mis_notificaciones.__wrapped__()
        filas = respuesta.get_json()["notificaciones"]
        self.assertEqual(codigo, 200)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["accion_url"], "/dashboardAdmin/reportes?reporte=99")
        self.assertEqual(filas[0]["Usuario_idUsuario"], 100)

    def test_enlaces_desconocidos_no_navegan(self):
        for tipo in [None, "viaje_asignado", "admin_falla:https://otro.com", "admin_control:../1"]:
            self.assertIsNone(Avisos.enlace(tipo))

    def test_cancelacion_admin_crea_aviso_en_la_operacion(self):
        from controllers.viaje_controller import ViajeController
        dominio = SimpleNamespace(cancelar=lambda motivo: True, estado="cancelado")
        def actualizar(modelo, _dominio):
            modelo.estado = "cancelado"
        with self.fixture.app.test_request_context("/", method="PUT", json={"motivo": "Avería"}), patch.object(ViajeController, "crear_objeto_viaje", return_value=dominio), patch.object(ViajeController, "actualizar_modelo_viaje", side_effect=actualizar), patch("controllers.viaje_controller.actualizar_camion_tras_cancelacion"), patch("services.notificacion_service.NotificacionService.enviar_push_pendientes"), patch.object(db.session, "commit", side_effect=db.session.flush):
            respuesta, codigo = ViajeController.cancelar_viaje_admin.__wrapped__(1)
        self.assertEqual(codigo, 200)
        self.assertEqual(NotificacionModel.query.filter_by(tipo="admin_cancelacion:1").count(), 2)


if __name__ == "__main__":
    unittest.main()
