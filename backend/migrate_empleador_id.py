"""Migración: agregar columna empleador_id a empresas_contratistas"""
import sys
sys.path.insert(0, '.')
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text(
            'ALTER TABLE empresas_contratistas '
            'ADD COLUMN IF NOT EXISTS empleador_id INTEGER '
            'REFERENCES empresas_contratistas(id)'
        ))
        conn.commit()
        r = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='empresas_contratistas' AND column_name='empleador_id'"
        )).fetchall()
        if r:
            print('OK - columna empleador_id creada correctamente')
        else:
            print('ERROR - columna no encontrada tras el ALTER')
