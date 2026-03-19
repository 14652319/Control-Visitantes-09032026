"""
Migración: Alter tabla empresas_contratistas para soporte Persona Natural
Fecha: 2026-03-19
Checkpoint: 3.1.2A
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate():
    app = create_app()
    with app.app_context():
        print("Agregando soporte Persona Natural a empresas_contratistas...")

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD COLUMN IF NOT EXISTS tipo_persona VARCHAR(10) NOT NULL DEFAULT 'JURIDICA',
            ADD COLUMN IF NOT EXISTS tipo_identificacion VARCHAR(5),
            ADD COLUMN IF NOT EXISTS num_identificacion VARCHAR(20),
            ADD COLUMN IF NOT EXISTS primer_nombre VARCHAR(100),
            ADD COLUMN IF NOT EXISTS segundo_nombre VARCHAR(100),
            ADD COLUMN IF NOT EXISTS primer_apellido VARCHAR(100),
            ADD COLUMN IF NOT EXISTS segundo_apellido VARCHAR(100);
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS check_tipo_persona_empresa;
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD CONSTRAINT check_tipo_persona_empresa
            CHECK (tipo_persona IN ('JURIDICA', 'NATURAL'));
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS check_tipo_identificacion_empresa;
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD CONSTRAINT check_tipo_identificacion_empresa
            CHECK (
                tipo_identificacion IS NULL
                OR tipo_identificacion IN ('CC', 'CE', 'TI', 'NIT', 'PAS', 'PEP')
            );
        """))

        db.session.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_empresa_num_identificacion_unique
            ON empresas_contratistas(num_identificacion)
            WHERE num_identificacion IS NOT NULL;
        """))

        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_empresa_tipo_persona
            ON empresas_contratistas(tipo_persona);
        """))

        db.session.commit()
        print("✅ Soporte Persona Natural agregado")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP INDEX IF EXISTS idx_empresa_tipo_persona;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_empresa_num_identificacion_unique;"))
        db.session.execute(text("ALTER TABLE empresas_contratistas DROP CONSTRAINT IF EXISTS check_tipo_identificacion_empresa;"))
        db.session.execute(text("ALTER TABLE empresas_contratistas DROP CONSTRAINT IF EXISTS check_tipo_persona_empresa;"))
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP COLUMN IF EXISTS segundo_apellido,
            DROP COLUMN IF EXISTS primer_apellido,
            DROP COLUMN IF EXISTS segundo_nombre,
            DROP COLUMN IF EXISTS primer_nombre,
            DROP COLUMN IF EXISTS num_identificacion,
            DROP COLUMN IF EXISTS tipo_identificacion,
            DROP COLUMN IF EXISTS tipo_persona;
        """))
        db.session.commit()
        print("✅ Rollback ejecutado")


if __name__ == '__main__':
    migrate()