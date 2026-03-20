"""
Migración: Hacer nit nullable en empresas_contratistas para Persona Natural
Fecha: 2026-03-19
Checkpoint: 3.1.5A
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate():
    app = create_app()
    with app.app_context():
        print("Ajustando nit en empresas_contratistas para Persona Natural...")

        # 1. Quitar NOT NULL a nit
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ALTER COLUMN nit DROP NOT NULL;
        """))

        # 2. Eliminar el UNIQUE global de nit (no funciona con valores NULL)
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS empresas_contratistas_nit_key;
        """))

        # 3. Índice único parcial: nit único solo para Persona Jurídica
        db.session.execute(text("""
            DROP INDEX IF EXISTS idx_empresa_nit_juridica;
        """))
        db.session.execute(text("""
            CREATE UNIQUE INDEX idx_empresa_nit_juridica
            ON empresas_contratistas(nit)
            WHERE tipo_persona = 'JURIDICA'
              AND nit IS NOT NULL;
        """))

        # 4. Constraint: Persona Jurídica DEBE tener nit,
        #               Persona Natural DEBE tener num_identificacion
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS check_identificacion_por_tipo_persona;
        """))
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD CONSTRAINT check_identificacion_por_tipo_persona CHECK (
                (tipo_persona = 'JURIDICA' AND nit IS NOT NULL)
                OR
                (tipo_persona = 'NATURAL' AND num_identificacion IS NOT NULL)
            );
        """))

        db.session.commit()
        print("✅ nit ahora nullable con índice parcial para Persona Jurídica")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("ALTER TABLE empresas_contratistas DROP CONSTRAINT IF EXISTS check_identificacion_por_tipo_persona;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_empresa_nit_juridica;"))
        db.session.execute(text("ALTER TABLE empresas_contratistas ADD CONSTRAINT empresas_contratistas_nit_key UNIQUE (nit);"))
        db.session.execute(text("ALTER TABLE empresas_contratistas ALTER COLUMN nit SET NOT NULL;"))
        db.session.commit()
        print("✅ Rollback ejecutado")


if __name__ == '__main__':
    migrate()
