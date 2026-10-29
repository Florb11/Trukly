"""Validar por defecto. Aplicar explícitamente con --apply (MySQL/MariaDB)."""
import argparse
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL


def migrar(engine, aplicar=False):
    with engine.connect() as conn:
        tabla = next((t for t in inspect(conn).get_table_names() if t.lower() == "reportefalla"), None)
        if not tabla:
            raise ValueError("No existe la tabla ReporteFalla")
        columnas = {c["name"] for c in inspect(conn).get_columns(tabla)}
        if "motivo_cancelacion" in columnas:
            print("El motivo de cancelación de reportes ya está configurado.")
            return
        identificador = conn.dialect.identifier_preparer.quote(tabla)
        consulta = f"ALTER TABLE {identificador} ADD COLUMN motivo_cancelacion VARCHAR(255) NULL"
        print("Cambio pendiente:", consulta)
        if aplicar:
            conn.execute(text(consulta))
            conn.commit()
            print("Migración de cancelación de reportes aplicada.")
        else:
            print("Solo comprobación. Usá --apply para aplicar.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = {**dotenv_values(Path(__file__).resolve().parents[2] / ".env"), **os.environ}
    try:
        if not all(config.get(campo) for campo in ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]):
            raise ValueError("Falta configurar la conexión de la base de datos")
        url = URL.create("mysql+pymysql", username=config["DB_USER"], password=config["DB_PASSWORD"], host=config["DB_HOST"], port=int(config.get("DB_PORT") or 3306), database=config["DB_NAME"])
        migrar(create_engine(url), args.apply)
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
