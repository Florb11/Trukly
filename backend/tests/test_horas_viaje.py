import unittest
from datetime import datetime, date
from types import SimpleNamespace
from services.horas_viaje_service import tiempo_viaje, resumen_horas, limites_mes

AHORA = datetime(2026, 11, 1)


def viaje(registros=(), estado="finalizado", id_viaje=1, chofer=1):
    return SimpleNamespace(id_viaje=id_viaje, estado=estado, fecha_salida=date(2026, 9, 30),
        origen="A", destino="B", Chofer_Usuario_idUsuario=chofer,
        registros_horarios=[SimpleNamespace(tipo_registro=tipo, fecha_hora=datetime.fromisoformat(hora)) for tipo, hora in registros])


class HorasViajeTest(unittest.TestCase):
    def test_duracion_real_con_minutos(self):
        v = viaje([("ingreso", "2026-09-30T08:15"), ("salida", "2026-09-30T17:45")])
        self.assertEqual(tiempo_viaje(v, AHORA)["duracion"], "9 h 30 min")

    def test_cruce_mes_y_anio(self):
        for inicio, fin, mes1, mes2 in [
            ("2026-09-30T23:00", "2026-10-01T02:00", "2026-09", "2026-10"),
            ("2025-12-31T23:00", "2026-01-01T02:00", "2025-12", "2026-01")]:
            v = viaje([("ingreso", inicio), ("salida", fin)])
            self.assertEqual(resumen_horas([v], mes1, AHORA)["segundos_confirmados"], 3600)
            self.assertEqual(resumen_horas([v], mes2, AHORA)["segundos_confirmados"], 7200)

    def test_registros_historicos_salida_entrada(self):
        v = viaje([("salida", "2026-09-30T08:00"), ("entrada", "2026-09-30T10:00")])
        self.assertEqual(tiempo_viaje(v, AHORA)["duracion"], "2 h 00 min")
        self.assertEqual(resumen_horas([v], "2026-09", AHORA)["segundos_confirmados"], 7200)

    def test_esquemas_mezclados_no_suman(self):
        v = viaje([("ingreso", "2026-09-30T08:00"), ("entrada", "2026-09-30T09:00"), ("salida", "2026-09-30T10:00")])
        self.assertEqual(tiempo_viaje(v, AHORA)["estado"], "inconsistente")

    def test_promedio_de_la_captura(self):
        viajes = [viaje([("ingreso", f"2026-09-{dia}T08:00"), ("salida", f"2026-09-{dia}T{fin}")], id_viaje=i)
                  for i, (dia, fin) in enumerate([("20", "15:00"), ("21", "15:00"), ("22", "15:40")], 1)]
        r = resumen_horas(viajes, "2026-09", AHORA)
        self.assertEqual(r["duracion"], "21 h 40 min")
        self.assertEqual(r["promedio"], "7 h 13 min")
        self.assertEqual(len(r["historial"]), 3)

    def test_aceptar_no_inicia_horas_ni_marca_control_faltante(self):
        v = viaje([], "aceptado")
        r = resumen_horas([v], "2026-09", AHORA)
        self.assertEqual(r["segundos_confirmados"], 0)
        self.assertEqual(r["viajes_en_curso"], 0)
        self.assertEqual(r["viajes_sin_registro"], 0)
        self.assertEqual(r["viajes_aceptados"], 1)
        self.assertEqual(r["historial"][0]["estado"], "aceptado")

    def test_en_curso_separado_del_total(self):
        v = viaje([("ingreso", "2026-09-30T08:00")], "en curso")
        r = resumen_horas([v], "2026-09", datetime(2026, 9, 30, 10))
        self.assertEqual(r["segundos_confirmados"], 0)
        self.assertEqual(r["viajes_en_curso"], 1)
        self.assertEqual(r["historial"][0]["transcurrido"], "2 h 00 min")

    def test_incompletos_duplicados_invertidos_y_futuros(self):
        casos = [
            ([], "sin_registro"),
            ([("salida", "2026-09-30T10:00")], "incompleto"),
            ([("ingreso", "2026-09-30T08:00")], "incompleto"),
            ([("ingreso", "2026-09-30T10:00"), ("salida", "2026-09-30T08:00")], "inconsistente"),
            ([("ingreso", "2026-09-30T08:00"), ("ingreso", "2026-09-30T08:01"), ("salida", "2026-09-30T10:00")], "inconsistente"),
            ([("ingreso", "2027-09-30T08:00"), ("salida", "2027-09-30T10:00")], "inconsistente"),
            ([("otro", "2026-09-30T08:00")], "inconsistente"),
        ]
        for registros, estado in casos:
            with self.subTest(estado=estado, registros=registros):
                v = viaje(registros)
                self.assertEqual(tiempo_viaje(v, AHORA)["estado"], estado)
                self.assertEqual(resumen_horas([v], "2026-09", AHORA)["segundos_confirmados"], 0)

    def test_cancelado_no_suma(self):
        v = viaje([("ingreso", "2026-09-30T08:00"), ("salida", "2026-09-30T10:00")], "cancelado")
        self.assertEqual(resumen_horas([v], "2026-09", AHORA)["segundos_confirmados"], 0)

    def test_superpuestos_se_cuentan_una_vez(self):
        a = viaje([("ingreso", "2026-09-30T08:00"), ("salida", "2026-09-30T10:00")])
        b = viaje([("ingreso", "2026-09-30T09:00"), ("salida", "2026-09-30T11:00")], id_viaje=2)
        r = resumen_horas([a, b], "2026-09", AHORA)
        self.assertEqual(r["segundos_confirmados"], 10800)
        self.assertEqual(r["segundos_superpuestos"], 3600)

    def test_limites_y_periodo_vacio(self):
        for mes in ["2026-9", "otro", "2026-00", "9999-12"]:
            with self.assertRaises(ValueError):
                limites_mes(mes)
        r = resumen_horas([], "2026-09", AHORA)
        self.assertEqual(r["duracion"], "0 h 00 min")
        self.assertIsNone(r["promedio"])


class HorasIntegracionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_admin_estadisticas_mensuales import AdminEstadisticasMensualesTest
        cls.fixture = AdminEstadisticasMensualesTest
        cls.fixture.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDownClass()

    def test_persistencia_serializacion_resumen_y_aislamiento(self):
        from db_instance import db
        from models.viaje_model import ViajeModel
        from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
        from services.horas_viaje_service import horas_chofer, horas_por_chofer
        registros = [RegistroIngresoSalidaModel(Viaje_id_viaje=1, tipo_registro=tipo, fecha_hora=datetime(2026, 9, 30, hora)) for tipo, hora in [("ingreso", 8), ("salida", 10)]]
        db.session.add_all(registros)
        db.session.commit()
        try:
            v = db.session.get(ViajeModel, 1)
            self.assertEqual(v.to_dict()["tiempo_viaje"]["duracion"], "2 h 00 min")
            self.assertEqual(horas_chofer(1, "2026-09")["duracion"], "2 h 00 min")
            self.assertEqual(horas_chofer(999, "2026-09")["segundos_confirmados"], 0)
            self.assertEqual(horas_por_chofer("2026-09")[0]["nombre"], "Ana")
        finally:
            for registro in registros:
                db.session.delete(registro)
            db.session.commit()

    def test_ciclo_qr_rechaza_dobles_escaneos(self):
        from flask import g
        from db_instance import db
        from models.viaje_model import ViajeModel
        from models.registro_ingreso_salida_model import RegistroIngresoSalidaModel
        from controllers.chofer_controller import ChoferController
        v = ViajeModel(id_viaje=99, OperadorLogistico_Usuario_idUsuario=2,
            Chofer_Usuario_idUsuario=1, Camion_id_camion=1, fecha_salida=date.today(),
            origen="A", destino="B", estado="pendiente", recorrido=10)
        db.session.add(v)
        db.session.commit()
        otro_activo = db.session.get(ViajeModel, 2)
        estado_previo = otro_activo.estado
        def escanear(tipo, chofer=1):
            with self.fixture.app.test_request_context("/", method="POST", json={"tipo_registro": tipo}):
                g.chofer_actual = SimpleNamespace(id_usuario=chofer)
                return ChoferController.registrar_ingreso_salida.__wrapped__(99)
        try:
            self.assertEqual(escanear("ingreso", 999)[1], 404)
            self.assertEqual(escanear("ingreso")[1], 400)
            self.assertEqual(escanear("salida")[1], 400)
            self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=99).count(), 0)
            with self.fixture.app.test_request_context("/", method="PUT"):
                g.chofer_actual = SimpleNamespace(id_usuario=1, iniciar_viaje=lambda viaje: (viaje.aceptar(), None))
                respuesta, codigo = ChoferController.iniciar_viaje.__wrapped__(99)
                self.assertEqual(codigo, 200)
                self.assertEqual(respuesta.get_json()["viaje"]["estado"], "aceptado")
                self.assertIsNone(respuesta.get_json()["viaje"]["tiempo_viaje"]["segundos_confirmados"])
                self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=99).count(), 0)
                self.assertEqual(ChoferController.iniciar_viaje.__wrapped__(99)[1], 400)
            self.assertEqual(escanear("salida")[1], 400)
            self.assertEqual(escanear("ingreso")[1], 409)
            otro_activo.estado = "finalizado"
            db.session.commit()
            self.assertEqual(escanear("ingreso")[1], 201)
            with self.fixture.app.test_request_context("/", method="PUT"):
                g.chofer_actual = SimpleNamespace(id_usuario=1)
                self.assertEqual(ChoferController.finalizar_viaje.__wrapped__(99)[1], 409)
            self.assertEqual(escanear("ingreso")[1], 400)
            self.assertEqual(escanear("salida")[1], 201)
            self.assertEqual(escanear("salida")[1], 400)
            self.assertEqual(RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=99).count(), 2)
            self.assertEqual(db.session.get(ViajeModel, 99).to_dict()["tiempo_viaje"]["estado"], "confirmado")
        finally:
            otro_activo.estado = estado_previo
            RegistroIngresoSalidaModel.query.filter_by(Viaje_id_viaje=99).delete()
            db.session.delete(v)
            db.session.commit()

    def test_perfil_y_estadisticas_comparten_resumen(self):
        from flask import g
        from db_instance import db
        from models.usuario_model import UsuarioModel
        from controllers.perfil_controller import PerfilController
        from controllers.chofer_controller import ChoferController
        perfil = PerfilController._preparar_respuesta_perfil(db.session.get(UsuarioModel, 1))
        with self.fixture.app.test_request_context("/"):
            g.chofer_actual = SimpleNamespace(id_usuario=1)
            respuesta, codigo = ChoferController.obtener_estadisticas.__wrapped__()
        self.assertEqual(codigo, 200)
        horas = respuesta.get_json()["horas_viaje"]
        self.assertEqual(horas["duracion"], perfil["horas_viaje"]["duracion"])
        self.assertNotIn("historial", perfil["horas_viaje"])

    def test_mes_invalido_en_endpoint_chofer(self):
        from flask import g
        from controllers.chofer_controller import ChoferController
        with self.fixture.app.test_request_context("/?mes=2026-13"):
            g.chofer_actual = SimpleNamespace(id_usuario=1)
            respuesta, codigo = ChoferController.obtener_estadisticas.__wrapped__()
            self.assertEqual(codigo, 400)


if __name__ == "__main__":
    unittest.main()
