import logging
import os


def get_app_logger():
    logger = logging.getLogger("trukly")
    if logger.handlers:
        return logger

    # Arma la ruta absoluta de la carpeta logs
    logs_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "logs",
        )
    )

    # Crea la carpeta logs si no existe
    os.makedirs(logs_dir, exist_ok=True)

    # Define el archivo donde se van a guardar los logs
    archivo_log = os.path.join(logs_dir, "app.log")

    # Crea un handler para escribir logs en el archivo
    handler = logging.FileHandler(archivo_log, encoding="utf-8")

    # Define el formato de cada linea del log
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
