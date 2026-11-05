"""Comprobar números de tanque duplicados y agregar unicidad con --apply."""
import argparse
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL


def migrar(engine, aplicar=False):
    with engine.connect() as conn:
        inspector = inspect(conn)
        tabla = next((t for t in inspector.get_table_names() if t.lower() == "camion"), None)
        if tabla is None:
            raise ValueError("No existe la tabla Camion.")
        columnas = {c["name"].lower(): c["name"] for c in inspector.get_columns(tabla)}
        if "nrotanque" not in columnas or "id_camion" not in columnas:
            raise ValueError("Faltan las columnas nroTanque o id_camion en Camion.")
        q = conn.dialect.identifier_preparer.quote
        t, numero, identificador = q(tabla), q(columnas["nrotanque"]), q(columnas["id_camion"])
        repetidos = conn.execute(text(f"SELECT {numero} FROM {t} GROUP BY {numero} HAVING COUNT(*) > 1")).scalars().all()
        if repetidos:
            conflictos = []
            for valor in repetidos:
                ids = conn.execute(text(f"SELECT {identificador} FROM {t} WHERE {numero} = :numero ORDER BY {identificador}"), {"numero": valor}).scalars().all()
                conflictos.append(f"tanque {valor}: camiones {', '.join(map(str, ids))}")
            raise ValueError("Hay números de tanque repetidos. Corregilos en Admin > Camiones y reintentá. " + "; ".join(conflictos))
        indices = inspector.get_unique_constraints(tabla) + inspector.get_indexes(tabla)
        if any([c.lower() for c in (i.get("column_names") or [])] == ["nrotanque"]
               and i.get("unique", True) for i in indices):
            print("El número de tanque ya es único.")
            return
        if engine.dialect.name not in {"mysql", "sqlite"}:
            raise ValueError("Esta migración requiere MySQL, MariaDB o SQLite.")
        consulta = f"CREATE UNIQUE INDEX {q('uq_camion_nro_tanque')} ON {t} ({numero})"
        print("Cambio pendiente:", consulta)
        if aplicar:
            conn.execute(text(consulta))
            conn.commit()
            print("Unicidad del número de tanque aplicada.")
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
