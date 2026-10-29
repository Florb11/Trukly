"""Validar por defecto. Aplicar explícitamente con --apply (MySQL/MariaDB)."""
import argparse
import os
import sys
from pathlib import Path
from decimal import Decimal, InvalidOperation
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL


def migrar(engine, aplicar=False):
    with engine.connect() as conn:
        tablas = inspect(conn).get_table_names()
        tabla = next((tabla for tabla in tablas if tabla.lower() == "carga"), None)
        if tabla is None:
            raise ValueError("No existe la tabla Carga. Creá primero el esquema base.")
        identificador = conn.dialect.identifier_preparer.quote(tabla)
        columnas = {columna["name"]: columna for columna in inspect(conn).get_columns(tabla)}
        invalidos = []
        for fila in conn.execute(text(f"SELECT id_carga, peso FROM {identificador}")):
            try:
                peso = Decimal(str(fila.peso))
                valido = peso.is_finite() and 0 < peso <= Decimal("999999999.999") and peso == peso.quantize(Decimal("0.001"))
            except (InvalidOperation, ValueError):
                valido = False
            if not valido:
                invalidos.append(fila.id_carga)
        if invalidos:
            raise ValueError(f"Corregí los pesos inválidos antes de migrar. IDs: {invalidos[:20]}")
        cambios = []
        tipo = columnas["peso"]["type"]
        if getattr(tipo, "precision", None) != 12 or getattr(tipo, "scale", None) != 3:
            cambios.append("MODIFY COLUMN peso DECIMAL(12,3) NOT NULL")
        if (getattr(columnas["descripcion"]["type"], "length", 0) or 0) < 255:
            cambios.append("MODIFY COLUMN descripcion VARCHAR(255) NOT NULL")
        if "bultos" not in columnas:
            cambios.append("ADD COLUMN bultos INT NULL")
        if "remito" not in columnas:
            cambios.append("ADD COLUMN remito VARCHAR(80) NULL")
        if not cambios:
            print("El esquema de cargas ya está actualizado.")
            return
        if engine.dialect.name != "mysql":
            raise ValueError("Esta migración requiere MySQL o MariaDB")
        consulta = f"ALTER TABLE {identificador} " + ", ".join(cambios)
        print("Validación correcta. Cambios pendientes:", consulta)
        if aplicar:
            conn.execute(text(consulta))
            conn.commit()
            print("Migración aplicada.")
        else:
            print("Solo comprobación. Usá --apply para modificar el esquema.")


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
