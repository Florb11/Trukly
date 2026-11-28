"""Comprobar la configuración de acceso. Usá --apply para migrar antes del despliegue."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from firebase_admin import auth
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))
from services.firebase_service import FirebaseAuthService


def vinculos_google(uids):
    if not uids:
        return set()
    FirebaseAuthService.inicializar()
    vinculados = set()
    for inicio in range(0, len(uids), 100):
        resultado = auth.get_users([auth.UidIdentifier(uid) for uid in uids[inicio:inicio + 100]])
        vinculados.update(
            cuenta.uid for cuenta in resultado.users
            if any(proveedor.provider_id == "google.com" for proveedor in cuenta.provider_data)
        )
    return vinculados


def migrar(engine, aplicar=False):
    with engine.connect() as conexion:
        tabla = next((nombre for nombre in inspect(conexion).get_table_names() if nombre.lower() == "usuario"), None)
        if not tabla:
            raise ValueError("No existe la tabla Usuario.")
        columnas = {columna["name"] for columna in inspect(conexion).get_columns(tabla)}
        if "firebase_uid" not in columnas:
            raise ValueError("La tabla Usuario necesita la columna firebase_uid.")
        identificador = conexion.dialect.identifier_preparer.quote(tabla)
        falta_columna = "google_autorizado" not in columnas
        filtro = "" if falta_columna else " WHERE google_autorizado IS NULL"
        usuarios = conexion.execute(text(f"SELECT id_usuario, firebase_uid FROM {identificador}{filtro}")).all()

    if not aplicar:
        print(f"Columna google_autorizado: {'pendiente' if falta_columna else 'disponible'}.")
        print(f"Cuentas pendientes de clasificar: {len(usuarios)}.")
        return

    uids = [usuario.firebase_uid for usuario in usuarios if usuario.firebase_uid]
    vinculados = vinculos_google(uids)
    with engine.begin() as conexion:
        if falta_columna:
            conexion.execute(text(f"ALTER TABLE {identificador} ADD COLUMN google_autorizado BOOLEAN NULL"))

        for usuario in usuarios:
            conexion.execute(text(f"""
                UPDATE {identificador} SET google_autorizado = :google
                WHERE id_usuario = :id AND google_autorizado IS NULL
                AND (firebase_uid = :uid OR (firebase_uid IS NULL AND :uid IS NULL))
            """), {"google": usuario.firebase_uid in vinculados, "id": usuario.id_usuario, "uid": usuario.firebase_uid})
    print(f"Migración aplicada. Vínculos existentes de Google encontrados: {len(vinculados)}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    load_dotenv(BACKEND / ".env")
    try:
        if not all(os.getenv(campo) for campo in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")):
            raise ValueError("Falta configurar la conexión de la base de datos.")
        url = URL.create("mysql+pymysql", username=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
                         host=os.environ["DB_HOST"], port=int(os.getenv("DB_PORT") or 3306), database=os.environ["DB_NAME"])
        migrar(create_engine(url), args.apply)
    except ValueError as error:
        sys.exit(str(error))
