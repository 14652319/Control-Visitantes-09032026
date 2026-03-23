"""
Migración: Agrega columna tipo_tercero a empresas_contratistas

Valores posibles:
  CONTRATISTA          — empresa o persona que tiene un contrato de servicios
  EMPLEADO_CONTRATISTA — personal de apoyo bajo un contratista
  MERCADERISTA         — mercaderista / impulsador en punto de venta
  VISITANTE_REGISTRO   — visitante registrado como tercero frecuente
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrar():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'empresas_contratistas'
                  AND column_name = 'tipo_tercero'
            """))
            if result.fetchone():
                print("ℹ️  La columna tipo_tercero ya existe. Nada que hacer.")
                return

            conn.execute(text("""
                ALTER TABLE empresas_contratistas
                ADD COLUMN tipo_tercero VARCHAR(30) NOT NULL DEFAULT 'CONTRATISTA'
            """))
            conn.commit()
            print("✅ Columna tipo_tercero agregada con default 'CONTRATISTA'.")
            print("   Todos los registros existentes quedan como CONTRATISTA.")


if __name__ == '__main__':
    migrar()
