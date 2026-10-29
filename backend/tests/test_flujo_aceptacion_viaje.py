import unittest
from src.Viaje import Viaje
from src.OperadorLogistico import OperadorLogistico


def viaje(estado="pendiente"):
    return Viaje.crear_desde_datos({"estado": estado, "fecha_salida": "2026-10-29", "origen": "A", "destino": "B", "id_chofer": 1, "id_operador": 2, "id_camion": 1})


class FlujoAceptacionTest(unittest.TestCase):
    def test_aceptar_e_iniciar_son_transiciones_distintas(self):
        v = viaje()
        self.assertFalse(v.iniciar())
        self.assertTrue(v.aceptar())
        self.assertEqual(v.estado, "aceptado")
        self.assertFalse(v.aceptar())
        self.assertFalse(v.finalizar())
        self.assertTrue(v.iniciar())
        self.assertEqual(v.estado, "en curso")
        self.assertTrue(v.finalizar())
        self.assertEqual(v.estado, "finalizado")

    def test_no_acepta_estados_incorrectos(self):
        for estado in ["aceptado", "en curso", "finalizado", "cancelado"]:
            v = viaje(estado)
            self.assertFalse(v.aceptar())
            self.assertEqual(v.estado, estado)

    def test_reasignacion_requiere_nueva_aceptacion(self):
        operador = OperadorLogistico.__new__(OperadorLogistico)
        operador.id_usuario = 2
        v = viaje("aceptado")
        self.assertTrue(operador.editar_viaje(v, {"Chofer_Usuario_idUsuario": 3})[0])
        self.assertEqual(v.id_chofer, 3)
        self.assertEqual(v.estado, "pendiente")

    def test_no_reasigna_un_viaje_en_curso(self):
        operador = OperadorLogistico.__new__(OperadorLogistico)
        operador.id_usuario = 2
        v = viaje("en curso")
        self.assertFalse(operador.editar_viaje(v, {"Chofer_Usuario_idUsuario": 3})[0])
        self.assertEqual(v.id_chofer, 1)
        self.assertEqual(v.estado, "en curso")


if __name__ == "__main__":
    unittest.main()
