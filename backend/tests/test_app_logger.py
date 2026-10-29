import io
import logging
import unittest
from unittest.mock import patch
from utils.app_logger import get_app_logger


class AppLoggerTest(unittest.TestCase):
    def test_traceback_en_consola_sin_duplicar_handlers(self):
        salida = io.StringIO()
        logger = logging.Logger("prueba")
        with patch("utils.app_logger.logging.getLogger", return_value=logger), patch("utils.app_logger.sys.stderr", salida), patch("utils.app_logger.os.makedirs"), patch("utils.app_logger.logging.FileHandler", return_value=logging.NullHandler()):
            get_app_logger()
            get_app_logger()
            try:
                raise RuntimeError("Error de prueba")
            except RuntimeError:
                get_app_logger().exception("Fallo controlado")
        self.assertEqual(salida.getvalue().count("Fallo controlado"), 1)
        self.assertIn("RuntimeError: Error de prueba", salida.getvalue())
        self.assertEqual(len(logger.handlers), 2)

    def test_sigue_funcionando_sin_archivo(self):
        salida = io.StringIO()
        logger = logging.Logger("prueba")
        with patch("utils.app_logger.logging.getLogger", return_value=logger), patch("utils.app_logger.sys.stderr", salida), patch("utils.app_logger.os.makedirs", side_effect=PermissionError("No disponible")):
            get_app_logger().error("Error visible")
        self.assertIn("Error visible", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
