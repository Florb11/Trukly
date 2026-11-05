"""Crear historial de cambios de viajes. Sin --apply solo comprueba el esquema."""
import argparse
import os
from pathlib import Path
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.engine import URL


def migrar(engine, aplicar=False):
    tablas = {t.lower(): t for t in inspect(engine).get_table_names()}
    if 'viajecambio' in tablas:
        print('El historial de viajes ya está configurado.')
        return
    if not {'viaje', 'usuario'}.issubset(tablas):
        raise ValueError('Faltan las tablas Viaje o Usuario')
    print('Cambio pendiente: crear ViajeCambio, sin modificar viajes existentes.')
    if not aplicar:
        return
    meta = MetaData()
    Table(tablas['viaje'], meta, autoload_with=engine)
    Table(tablas['usuario'], meta, autoload_with=engine)
    tabla = Table('ViajeCambio', meta,
        Column('id_cambio', Integer, primary_key=True),
        Column('id_viaje', Integer, ForeignKey(f"{tablas['viaje']}.id_viaje"), nullable=False, index=True),
        Column('id_usuario', Integer, ForeignKey(f"{tablas['usuario']}.id_usuario"), nullable=False),
        Column('actor_nombre', String(201), nullable=False),
        Column('accion', String(45), nullable=False),
        Column('fecha_hora', DateTime, nullable=False),
        Column('datos', JSON, nullable=False))
    tabla.create(engine, checkfirst=True)
    print('Historial de viajes configurado.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    config = {**dotenv_values(Path(__file__).resolve().parents[2] / '.env'), **os.environ}
    if not all(config.get(c) for c in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']):
        raise SystemExit('Falta configurar la conexión de la base de datos')
    url = URL.create('mysql+pymysql', username=config['DB_USER'], password=config['DB_PASSWORD'],
        host=config['DB_HOST'], port=int(config.get('DB_PORT') or 3306), database=config['DB_NAME'])
    migrar(create_engine(url), args.apply)
