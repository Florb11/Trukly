import unittest
from datetime import date, datetime

from flask import Flask

from controllers.admin_estadisticas_controller import AdminEstadisticasController
from db_instance import db
from models.camion_model import CamionModel
from models.chofer_model import ChoferModel
from models.mecanico_model import MecanicoModel
from models.operador_model import OperadorModel
from models.reporte_model import ReporteModel
from models.usuario_model import UsuarioModel
from models.viaje_model import ViajeModel


class AdminEstadisticasMensualesTest(unittest.TestCase):
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
            UsuarioModel(id_usuario=2, username="operador", password="x", nombre="Juan", apellido="Pérez", rol="operador"),
            UsuarioModel(id_usuario=3, username="mecanico", password="x", nombre="Sol", apellido="Díaz", rol="mecanico"),
            ChoferModel(Usuario_idUsuario=1, licencia="L1", vencimientoLicencia=date(2028, 1, 1), legajo="C1"),
            OperadorModel(Usuario_idUsuario=2, legajo="O1", sector="Rutas"),
            MecanicoModel(Usuario_idUsuario=3, legajo="M1", especialidad="Motor"),
            CamionModel(id_camion=1, matricula="AAA111", marca="Marca", modelo="Modelo", capacidad_carga=1000, estado="disponible", nroTanque=1),
            ViajeModel(id_viaje=1, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date(2026, 9, 1), origen="A", destino="B", estado="finalizado", recorrido=10),
            ViajeModel(id_viaje=2, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date(2026, 9, 30), origen="B", destino="C", estado="en curso", recorrido=20),
            ViajeModel(id_viaje=3, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date(2026, 10, 1), origen="C", destino="D", estado="cancelado", recorrido=30),
            ReporteModel(id_reporte=1, fecha_hora=datetime(2026, 9, 30, 23, 59, 59), descripcion="Falla septiembre", estado="pendiente", Camion_id_camion=1, Chofer_Usuario_idUsuario=1),
            ReporteModel(id_reporte=2, fecha_hora=datetime(2026, 10, 1, 0, 0), descripcion="Falla octubre", estado="resuelto", Camion_id_camion=1, Chofer_Usuario_idUsuario=1, Mecanico_Usuario_idUsuario=3),
        ])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.contexto.pop()

    def test_rechaza_meses_invalidos(self):
        for valor in ("2026-9", "2026-00", "2026-13", "otro", "9999-12"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                AdminEstadisticasController._limites_mes(valor)

    def test_septiembre_no_incluye_el_primer_dia_de_octubre(self):
        inicio, fin = AdminEstadisticasController._limites_mes("2026-09")
        resumen = AdminEstadisticasController._obtener_resumen(inicio, fin)
        viajes, reportes = AdminEstadisticasController._obtener_ultimos_movimientos(inicio, fin)

        self.assertEqual(resumen["total_viajes"], 2)
        self.assertEqual(resumen["viajes_finalizados"], 1)
        self.assertEqual(resumen["total_reportes"], 1)
        self.assertEqual(resumen["reportes_activos"], 1)
        self.assertEqual([viaje.id_viaje for viaje in viajes], [2, 1])
        self.assertEqual([reporte.id_reporte for reporte in reportes], [1])

        ranking = AdminEstadisticasController._obtener_ranking_viajes_por_usuario(ViajeModel.Chofer_Usuario_idUsuario, inicio, fin)
        self.assertEqual(ranking[0]["total_viajes"], 2)
        self.assertEqual(AdminEstadisticasController._obtener_camiones_mas_reportes(inicio, fin)[0]["total_reportes"], 1)

    def test_octubre_es_un_periodo_distinto(self):
        inicio, fin = AdminEstadisticasController._limites_mes("2026-10")
        resumen = AdminEstadisticasController._obtener_resumen(inicio, fin)
        viajes, reportes = AdminEstadisticasController._obtener_ultimos_movimientos(inicio, fin)

        self.assertEqual(resumen["total_viajes"], 1)
        self.assertEqual(resumen["viajes_cancelados"], 1)
        self.assertEqual(resumen["total_reportes"], 1)
        self.assertEqual(resumen["reportes_resueltos"], 1)
        self.assertEqual([viaje.id_viaje for viaje in viajes], [3])
        self.assertEqual([reporte.id_reporte for reporte in reportes], [2])

    def test_respuesta_completa_usa_un_solo_mes(self):
        with self.app.test_request_context("/api/admin/estadisticas?mes=2026-09"):
            respuesta, codigo = AdminEstadisticasController.obtener_estadisticas.__wrapped__()
        datos = respuesta.get_json()

        self.assertEqual(codigo, 200)
        self.assertEqual(datos["mes"], "2026-09")
        self.assertEqual(datos["resumen"]["total_viajes"], 2)
        self.assertEqual(datos["resumen"]["total_reportes"], 1)
        self.assertEqual(len(datos["ultimos_viajes"]), 2)
        self.assertEqual(len(datos["ultimos_reportes"]), 1)
        self.assertEqual(datos["choferes_mas_viajes"][0]["total_viajes"], 2)
        self.assertEqual(datos["operadores_mas_viajes"][0]["total_viajes"], 2)
        self.assertEqual(datos["choferes_mas_reportes"][0]["total_reportes"], 1)
        self.assertEqual(datos["camiones_mas_reportes"][0]["total_reportes"], 1)

    def test_mes_invalido_devuelve_400(self):
        with self.app.test_request_context("/api/admin/estadisticas?mes=2026-13"):
            respuesta, codigo = AdminEstadisticasController.obtener_estadisticas.__wrapped__()
        self.assertEqual(codigo, 400)
        self.assertIn("formato", respuesta.get_json()["mensaje"])

    def test_historial_del_mes_no_se_recorta_a_diez(self):
        nuevos_viajes = [
            ViajeModel(id_viaje=numero, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date(2026, 9, 15), origen="A", destino="B", estado="pendiente", recorrido=10)
            for numero in range(4, 15)
        ]
        db.session.add_all(nuevos_viajes)
        db.session.commit()
        try:
            inicio, fin = AdminEstadisticasController._limites_mes("2026-09")
            viajes, _ = AdminEstadisticasController._obtener_ultimos_movimientos(inicio, fin)
            self.assertEqual(len(viajes), 13)
        finally:
            for viaje in nuevos_viajes:
                db.session.delete(viaje)
            db.session.commit()


if __name__ == "__main__":
    unittest.main()
