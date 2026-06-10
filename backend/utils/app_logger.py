import logging
import os


def get_app_logger():
    logger = logging.getLogger("trukly")

    if logger.handlers:
        return logger

    logs_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "logs",
        )
    )
    os.makedirs(logs_dir, exist_ok=True)

    archivo_log = os.path.join(logs_dir, "app.log")

    handler = logging.FileHandler(archivo_log, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
