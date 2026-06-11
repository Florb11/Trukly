import logging
import os


def get_app_logger():
    # Devuelve el logger principal 
    logger = logging.getLogger("trukly")

    # Si ya tiene handlers, lo devuelve para no duplicar logs
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

    # Guarda logs desde nivel INFO 
    logger.setLevel(logging.INFO)

    # Agrega el handler al logger
    logger.addHandler(handler)

    # Evita que el log se repita en otros loggers
    logger.propagate = False

    # Devuelve el logger listo para usar
    return logger
