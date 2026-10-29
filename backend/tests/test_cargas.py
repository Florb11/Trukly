import unittest
from decimal import Decimal
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch
from sqlalchemy.exc import OperationalError
from flask import g
from db_instance import db
from models.carga_model import CargaModel
from models.camion_model import CamionModel
from models.viaje_model import ViajeModel
from controllers.carga_controller import CargaController
from services.carga_service import peso_decimal, validar_datos, comprobar_capacidad, comprobar_reduccion_capacidad, ErrorCarga


def datos(peso="100", **extra):
    return {"descripcion": "Bolsas de cemento", "tipo": "Construcción", "peso": peso, **extra}


class PesosCargaTest(unittest.TestCase):
    def test_precision_decimal(self):
        self.assertEqual(peso_decimal("0.1") + peso_decimal("0.2"), Decimal("0.3"))
        self.assertEqual(peso_decimal("10000.125"), Decimal("10000.125"))

    def test_pesos_invalidos(self):
        for valor in [None, True, 0, -1, "kg", "NaN", "Infinity", "0.0001", "1000000000", ""]:
            with self.subTest(valor=valor), self.assertRaises(ErrorCarga):
                peso_decimal(valor)

    def test_opcionales_y_limites(self):
        self.assertIsNone(validar_datos(datos())["bultos"])
        self.assertEqual(validar_datos(datos(bultos="200", remito=" REM-1 "))["bultos"], 200)
        self.assertEqual(validar_datos(datos(remito=" REM-1 "))["remito"], "REM-1")
        for extra in [{"bultos": -1}, {"bultos": 1.5}, {"bultos": True}, {"remito": "x" * 81}, {"descripcion": " "}, {"tipo": "x" * 46}]:
            with self.subTest(extra=extra), self.assertRaises(ErrorCarga):
                validar_datos(datos(**extra))


class CargasApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()
        db.session.add(CamionModel(id_camion=10, matricula="CHICO", marca="Marca", modelo="Menor", capacidad_carga=500, estado="disponible", nroTanque=10))
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def setUp(self):
        db.session.add(ViajeModel(id_viaje=50, OperadorLogistico_Usuario_idUsuario=2, Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date.today(), origen="A", destino="B", estado="pendiente", recorrido=10))
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        CargaModel.query.filter_by(Viaje_id_viaje=50).delete()
        ViajeModel.query.filter_by(id_viaje=50).delete()
        db.session.get(CamionModel, 10).estado = "disponible"
        db.session.commit()

    def pedir(self, metodo="GET", cuerpo=None, carga=None, operador=2):
        with self.fixture.app.test_request_context("/", method=metodo, json=cuerpo):
            g.operador_actual = SimpleNamespace(id_usuario=operador)
            respuesta, codigo = CargaController.gestionar.__wrapped__(50, carga)
            return respuesta.get_json(), codigo

    def test_error_de_esquema_informa_migracion_y_referencia(self):
        fallo = OperationalError("consulta", {}, Exception(1054, "detalle interno"))
        with patch("controllers.carga_controller.carga_service.resumen", side_effect=fallo), patch("controllers.carga_controller.get_app_logger") as logger:
            respuesta, codigo = self.pedir()
        self.assertEqual(codigo, 500)
        self.assertIn("migración", respuesta["mensaje"])
        self.assertEqual(len(respuesta["referencia"]), 12)
        self.assertNotIn("detalle interno", respuesta["mensaje"])
        logger.return_value.exception.assert_called_once()

    def test_error_de_guardado_hace_rollback_y_da_referencia(self):
        with patch.object(db.session, "commit", side_effect=RuntimeError("fallo interno")), patch("controllers.carga_controller.get_app_logger"):
            respuesta, codigo = self.pedir("POST", datos())
        self.assertEqual(codigo, 500)
        self.assertEqual(len(respuesta["referencia"]), 12)
        self.assertEqual(CargaModel.query.filter_by(Viaje_id_viaje=50).count(), 0)

    def consultar(self, rol, id_usuario):
        with self.fixture.app.test_request_context("/"), patch("controllers.carga_controller.AuthService.obtener_rol_actual", return_value=rol), patch("controllers.carga_controller.AuthService.obtener_id_usuario_actual", return_value=id_usuario):
            respuesta, codigo = CargaController.consultar.__wrapped__(50)
            return respuesta.get_json(), codigo

    def test_detalle_para_operador_chofer_y_admin(self):
        self.pedir("POST", datos("400.125", bultos=20, remito="R-1"))
        for rol, id_usuario in [("operador", 2), ("chofer", 1), ("admin", 100)]:
            with self.subTest(rol=rol):
                r, codigo = self.consultar(rol, id_usuario)
                self.assertEqual(codigo, 200)
                self.assertFalse(r["editable"])
                self.assertEqual(r["peso_total_kg"], 400.125)
                self.assertEqual(r["disponible_kg"], 599.875)
                self.assertEqual(r["cargas"][0]["bultos"], 20)
                self.assertEqual(r["cargas"][0]["remito"], "R-1")

    def test_detalle_no_expone_cargas_de_viajes_ajenos(self):
        for rol in ["operador", "chofer"]:
            self.assertEqual(self.consultar(rol, 999)[1], 404)
        self.assertEqual(self.consultar("mecanico", 3)[1], 403)

    def test_detalle_vacio_y_finalizado(self):
        r, codigo = self.consultar("chofer", 1)
        self.assertEqual(codigo, 200)
        self.assertEqual(r["cargas"], [])
        self.assertEqual(r["peso_total_kg"], 0)
        self.pedir("POST", datos("300"))
        db.session.get(ViajeModel, 50).estado = "finalizado"
        db.session.commit()
        r, codigo = self.consultar("chofer", 1)
        self.assertEqual(codigo, 200)
        self.assertEqual(r["peso_total_kg"], 300)
        self.assertFalse(r["editable"])

    def test_ruta_de_consulta_no_admite_escrituras(self):
        from flask import Flask
        from routes.viaje_routes import viaje_routes
        app = Flask("consulta")
        app.register_blueprint(viaje_routes)
        for metodo in ["POST", "PUT", "DELETE"]:
            self.assertEqual(app.test_client().open("/api/viaje/50/cargas", method=metodo).status_code, 405)

    def test_suma_edicion_y_eliminacion_recalculan(self):
        r, codigo = self.pedir("POST", datos("400", bultos=20, remito="R-1"))
        self.assertEqual(codigo, 201)
        id_carga = r["cargas"][0]["id_carga"]
        r, _ = self.pedir("POST", datos("300"))
        self.assertEqual(r["peso_total_kg"], 700)
        self.assertEqual(r["disponible_kg"], 300)
        r, codigo = self.pedir("PUT", datos("600"), id_carga)
        self.assertEqual(codigo, 200)
        self.assertEqual(r["peso_total_kg"], 900)
        r, codigo = self.pedir("DELETE", carga=id_carga)
        self.assertEqual(codigo, 200)
        self.assertEqual(r["peso_total_kg"], 300)
        self.assertEqual(r["disponible_kg"], 700)

    def test_acepta_capacidad_exacta_y_rechaza_exceso(self):
        self.assertEqual(self.pedir("POST", datos("1000"))[1], 201)
        self.assertEqual(self.pedir("POST", datos("0.001"))[1], 409)
        self.assertEqual(self.pedir()[0]["peso_total_kg"], 1000)
        self.assertEqual(CargaModel.query.filter_by(Viaje_id_viaje=50).count(), 1)

    def test_edicion_rechazada_no_altera_la_carga(self):
        r, _ = self.pedir("POST", datos("500"))
        id_carga = r["cargas"][0]["id_carga"]
        self.assertEqual(self.pedir("PUT", datos("1000.001"), id_carga)[1], 409)
        self.assertEqual(self.pedir()[0]["peso_total_kg"], 500)

    def test_aislamiento_entre_operadores_y_viajes(self):
        self.assertEqual(self.pedir("POST", datos(), operador=999)[1], 404)
        self.assertEqual(self.pedir(operador=999)[1], 404)
        self.assertEqual(self.pedir("PUT", datos(), carga=999)[1], 404)
        self.assertEqual(self.pedir("DELETE", carga=999)[1], 404)

    def test_bloqueo_al_iniciar_y_solo_lectura_al_finalizar(self):
        r, _ = self.pedir("POST", datos())
        id_carga = r["cargas"][0]["id_carga"]
        for estado in ["en curso", "finalizado", "cancelado"]:
            v = db.session.get(ViajeModel, 50)
            v.estado = estado
            db.session.commit()
            self.assertEqual(self.pedir("POST", datos())[1], 409)
            self.assertEqual(self.pedir("PUT", datos(), id_carga)[1], 409)
            self.assertEqual(self.pedir("DELETE", carga=id_carga)[1], 409)
            self.assertFalse(self.pedir()[0]["editable"])

    def test_qr_no_inicia_un_viaje_con_sobrecarga(self):
        from controllers.chofer_controller import ChoferController
        v = db.session.get(ViajeModel, 50)
        v.estado = "aceptado"
        db.session.add(CargaModel(Viaje_id_viaje=50, descripcion="Dato histórico", tipo="Mercadería", peso=Decimal("1001"), estado="registrada"))
        db.session.commit()
        with self.fixture.app.test_request_context("/", method="POST", json={"tipo_registro": "ingreso"}):
            g.chofer_actual = SimpleNamespace(id_usuario=1)
            _, codigo = ChoferController.registrar_ingreso_salida.__wrapped__(50)
        self.assertEqual(codigo, 409)
        self.assertEqual(db.session.get(ViajeModel, 50).estado, "aceptado")

    def test_aceptado_sigue_permitiendo_cargas(self):
        db.session.get(ViajeModel, 50).estado = "aceptado"
        db.session.commit()
        self.assertEqual(self.pedir("POST", datos())[1], 201)

    def test_decimales_y_campos_opcionales_persistidos(self):
        self.pedir("POST", datos("0.1", bultos=2, remito="R-123"))
        r, _ = self.pedir("POST", datos("0.2"))
        self.assertEqual(r["peso_total_kg"], 0.3)
        self.assertEqual(r["cargas"][0]["bultos"], 2)
        self.assertEqual(r["cargas"][0]["remito"], "R-123")

    def test_endpoint_impide_cambiar_a_camion_menor(self):
        from controllers.operador_controller import OperadorController
        from src.OperadorLogistico import OperadorLogistico
        self.pedir("POST", datos("700"))
        operador = OperadorLogistico.__new__(OperadorLogistico)
        operador.id_usuario = 2
        with self.fixture.app.test_request_context("/", method="PUT", json={"Camion_id_camion": 10}):
            g.operador_actual = operador
            _, codigo = OperadorController.editar_viaje.__wrapped__(50)
        self.assertEqual(codigo, 409)
        self.assertEqual(db.session.get(ViajeModel, 50).Camion_id_camion, 1)

    def test_endpoint_permite_cambiar_si_alcanza_y_reserva_camion(self):
        from controllers.operador_controller import OperadorController
        from src.OperadorLogistico import OperadorLogistico
        self.pedir("POST", datos("400"))
        operador = OperadorLogistico.__new__(OperadorLogistico)
        operador.id_usuario = 2
        with self.fixture.app.test_request_context("/", method="PUT", json={"Camion_id_camion": 10}):
            g.operador_actual = operador
            respuesta, codigo = OperadorController.editar_viaje.__wrapped__(50)
        self.assertEqual(codigo, 200, respuesta.get_json())
        self.assertEqual(db.session.get(ViajeModel, 50).Camion_id_camion, 10)
        self.assertEqual(db.session.get(CamionModel, 10).estado, "en viaje")
        self.assertEqual(self.pedir()[0]["disponible_kg"], 100)

    def test_cambio_de_camion_y_reduccion_de_capacidad(self):
        self.pedir("POST", datos("700"))
        with self.assertRaises(ErrorCarga):
            comprobar_capacidad(50, db.session.get(CamionModel, 10))
        with self.assertRaises(ErrorCarga):
            comprobar_reduccion_capacidad(1, 699)
        comprobar_reduccion_capacidad(1, 700)
        self.assertEqual(db.session.get(ViajeModel, 50).Camion_id_camion, 1)


if __name__ == "__main__":
    unittest.main()
