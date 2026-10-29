import logging
import os
import sys


def get_app_logger():
    logger = logging.getLogger("trukly")
    formato = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Railway/Gunicorn recoge stderr; el archivo solo no aparece en Deploy Logs.
    if not any(getattr(handler, "_trukly_console", False) for handler in logger.handlers):
        consola = logging.StreamHandler(sys.stderr)
        consola.setFormatter(formato)
        consola._trukly_console = True
        logger.addHandler(consola)

    if not any(getattr(handler, "_trukly_file", False) or hasattr(handler, "baseFilename") for handler in logger.handlers):
        try:
            carpeta = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
            os.makedirs(carpeta, exist_ok=True)
            archivo = logging.FileHandler(os.path.join(carpeta, "app.log"), encoding="utf-8")
            archivo.setFormatter(formato)
            archivo._trukly_file = True
            logger.addHandler(archivo)
        except OSError:
            logger.warning("No se pudo abrir el archivo de logs; se registrará en consola")
    return logger
