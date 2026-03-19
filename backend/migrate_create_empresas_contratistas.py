"""
Migración: Crear tabla empresas_contratistas
Fecha: 2026-03-19
Checkpoint: 3.1.2
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Creando tabla empresas_contratistas...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS empresas_contratistas (
                id                  SERIAL PRIMARY KEY,
                razon_social        VARCHAR(200) NOT NULL,
                nit                 VARCHAR(20)  NOT NULL UNIQUE,
                digito_verificacion VARCHAR(1)   NOT NULL,
                representante_legal VARCHAR(150) NOT NULL,
                telefono            VARCHAR(20),
                email               VARCHAR(100),
                direccion           VARCHAR(200),
                ciudad              VARCHAR(100),
                estado              VARCHAR(20)  NOT NULL DEFAULT 'activa',
                created_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
                updated_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
                created_by          INTEGER REFERENCES usuarios(id),
                CONSTRAINT check_estado_empresa CHECK (estado IN ('activa', 'inactiva', 'suspendida'))
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_empresa_nit
                ON empresas_contratistas(nit);
            CREATE INDEX IF NOT EXISTS idx_empresa_estado
                ON empresas_contratistas(estado);
        """))
        db.session.commit()
        print("✅ Tabla empresas_contratistas creada")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS empresas_contratistas CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
