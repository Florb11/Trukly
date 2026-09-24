import unittest
from datetime import date, datetime
from types import SimpleNamespace

from flask import Flask, g

from controllers.operador_controller import OperadorController
from db_instance import db
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from models.operador_model import OperadorModel
from models.reporte_model import ReporteModel
from models.usuario_model import UsuarioModel
from models.viaje_model import ViajeModel


class OperadorEstadisticasMensualesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config.update(
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(cls.app)
        cls.contexto = cls.app.app_context()
        cls.contexto.push()
        db.create_all()

        db.session.add_all([
            UsuarioModel(id_usuario=1, username="chofer", password="x", nombre="Ana", apellido="García", rol="chofer"),
            UsuarioModel(id_usuario=2, username="operador1", password="x", nombre="Juan", apellido="Pérez", rol="operador"),
            UsuarioModel(id_usuario=3, username="operador2", password="x", nombre="Sol", apellido="Díaz", rol="operador"),
            ChoferModel(Usuario_idUsuario=1, licencia="L1", vencimientoLicencia=date(2028, 1, 1), legajo="C1"),
            OperadorModel(Usuario_idUsuario=2, legajo="O1", sector="Rutas"),
            OperadorModel(Usuario_idUsuario=3, legajo="O2", sector="Rutas"),
            CamionModel(id_camion=1, matricula="AAA111", marca="Marca", modelo="Uno", capacidad_carga=1000, estado="disponible", nroTanque=1),
            CamionModel(id_camion=2, matricula="BBB222", marca="Marca", modelo="Dos", capacidad_carga=1000, estado="disponible", nroTanque=2),
            ViajeModel(id_viaje=1, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date(2026, 9, 30), origen="A", destino="B", estado="finalizado", recorrido=10),
            ViajeModel(id_viaje=2, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date(2026, 10, 1), origen="B", destino="C", estado="pendiente", recorrido=20),
            ViajeModel(id_viaje=3, OperadorLogistico_Usuario_idUsuario=3, Chofer_Usuario_idUsuario=1, Camion_id_camion=2, fecha_salida=date(2026, 9, 1), origen="C", destino="D", estado="en curso", recorrido=30),
            ReporteModel(id_reporte=1, fecha_hora=datetime(2026, 9, 30, 23, 59, 59), descripcion="Falla septiembre", estado="pendiente", Camion_id_camion=1, Chofer_Usuario_idUsuario=1),
            ReporteModel(id_reporte=2, fecha_hora=datetime(2026, 10, 1), descripcion="Falla octubre", estado="resuelto", Camion_id_camion=1, Chofer_Usuario_idUsuario=1),
            ReporteModel(id_reporte=3, fecha_hora=datetime(2026, 9, 15), descripcion="Otro operador", estado="pendiente", Camion_id_camion=2, Chofer_Usuario_idUsuario=1),
        ])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.contexto.pop()

    def consultar(self, mes):
        with self.app.test_request_context(f"/api/operador/estadisticas?mes={mes}"):
            g.operador_actual = SimpleNamespace(id_usuario=2)
            respuesta, codigo = OperadorController.obtener_estadisticas.__wrapped__()
            return respuesta.get_json(), codigo

    def test_septiembre_filtra_por_mes_y_operador(self):
        datos, codigo = self.consultar("2026-09")
        self.assertEqual(codigo, 200)
        self.assertEqual(datos["mes"], "2026-09")
        self.assertEqual(datos["resumen"]["total_viajes"], 1)
        self.assertEqual(datos["resumen"]["reportes_pendientes"], 1)
        self.assertEqual([viaje["id_viaje"] for viaje in datos["ultimos_viajes"]], [1])
        self.assertEqual([reporte["id_reporte"] for reporte in datos["ultimos_reportes"]], [1])
        self.assertEqual(datos["choferes_mas_usados"][0]["total_viajes"], 1)

    def test_octubre_es_otro_periodo(self):
        datos, codigo = self.consultar("2026-10")
        self.assertEqual(codigo, 200)
        self.assertEqual(datos["resumen"]["total_viajes"], 1)
        self.assertEqual(datos["resumen"]["reportes_resueltos"], 1)
        self.assertEqual([viaje["id_viaje"] for viaje in datos["ultimos_viajes"]], [2])
        self.assertEqual([reporte["id_reporte"] for reporte in datos["ultimos_reportes"]], [2])

    def test_mes_invalido_devuelve_400(self):
        datos, codigo = self.consultar("2026-13")
        self.assertEqual(codigo, 400)
        self.assertIn("formato", datos["mensaje"])

    def test_historial_mensual_no_se_recorta_a_cinco(self):
        nuevos_viajes = [
            ViajeModel(id_viaje=numero, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1,
                       Camion_id_camion=1, fecha_salida=date(2026, 9, 15), origen="A", destino="B",
                       estado="pendiente", recorrido=10)
            for numero in range(4, 15)
        ]
        db.session.add_all(nuevos_viajes)
        db.session.commit()
        try:
            datos, codigo = self.consultar("2026-09")
            self.assertEqual(codigo, 200)
            self.assertEqual(datos["resumen"]["total_viajes"], 12)
            self.assertEqual(len(datos["ultimos_viajes"]), 12)
        finally:
            for viaje in nuevos_viajes:
                db.session.delete(viaje)
            db.session.commit()


if __name__ == "__main__":
    unittest.main()
