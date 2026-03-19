"""
Migración: Crear tabla operadores_aportes
Fecha: 2026-03-19
Checkpoint: 3.1.1
Tabla para EPS, AFP y ARL registradas en Colombia
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Creando tabla operadores_aportes...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS operadores_aportes (
                id          SERIAL PRIMARY KEY,
                nombre      VARCHAR(100) NOT NULL,
                tipo        VARCHAR(10)  NOT NULL,
                nit         VARCHAR(20)  NOT NULL,
                activo      BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
                CONSTRAINT check_tipo_operador CHECK (tipo IN ('EPS', 'AFP', 'ARL')),
                CONSTRAINT unique_nit_tipo UNIQUE (nit, tipo)
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_operador_tipo
                ON operadores_aportes(tipo);
        """))
        db.session.commit()
        print("✅ Tabla operadores_aportes creada")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS operadores_aportes CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
