"""
Migración: Corrección de hallazgos detectados en FASE 3.1
Checkpoint: 3.2.0
Hallazgos: CP313-01, CP314-01, CP314-02, CP313-03, CP314-04
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate():
    app = create_app()
    with app.app_context():
        print("Aplicando correcciones de hallazgos FASE 3.1...")

        # CP313-01: CHECK constraint para tipo_certificado
        db.session.execute(text("""
            ALTER TABLE certificados_trabajo
            DROP CONSTRAINT IF EXISTS check_tipo_certificado;
        """))
        db.session.execute(text("""
            ALTER TABLE certificados_trabajo
            ADD CONSTRAINT check_tipo_certificado CHECK (
                tipo_certificado IN ('ALTURAS', 'ELECTRICO', 'ESPACIOS_CONFINADOS', 'MANEJO_QUIMICOS', 'PRIMEROS_AUXILIOS', 'OTRO')
            );
        """))
        print("  ✅ CP313-01: CHECK type_certificado aplicado")

        # CP314-02: CHECK fecha_fin >= fecha_inicio en autorizaciones_sst
        db.session.execute(text("""
            ALTER TABLE autorizaciones_sst
            DROP CONSTRAINT IF EXISTS check_vigencia_autorizacion;
        """))
        db.session.execute(text("""
            ALTER TABLE autorizaciones_sst
            ADD CONSTRAINT check_vigencia_autorizacion CHECK (
                fecha_fin >= fecha_inicio
            );
        """))
        print("  ✅ CP314-02: CHECK fecha_fin >= fecha_inicio aplicado")

        # CP314-01: Agregar columna numero_autorizacion para consecutivo SST-{AÑO}-{0001}
        db.session.execute(text("""
            ALTER TABLE autorizaciones_sst
            ADD COLUMN IF NOT EXISTS numero_autorizacion VARCHAR(20) UNIQUE;
        """))
        db.session.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_autorizacion_numero
            ON autorizaciones_sst(numero_autorizacion);
        """))
        print("  ✅ CP314-01: Columna numero_autorizacion añadida con índice único")

        # CP313-03: Índice empleado_id en certificados_trabajo
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_certificado_empleado
            ON certificados_trabajo(empleado_id);
        """))
        print("  ✅ CP313-03: Índice idx_certificado_empleado creado")

        # CP314-04: Índice empleado_id en log_ingresos_contratistas
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_log_ingreso_empleado
            ON log_ingresos_contratistas(empleado_id);
        """))
        print("  ✅ CP314-04: Índice idx_log_ingreso_empleado creado")

        db.session.commit()
        print("\n✅ Todos los hallazgos de FASE 3.1 corregidos")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("ALTER TABLE certificados_trabajo DROP CONSTRAINT IF EXISTS check_tipo_certificado;"))
        db.session.execute(text("ALTER TABLE autorizaciones_sst DROP CONSTRAINT IF EXISTS check_vigencia_autorizacion;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_autorizacion_numero;"))
        db.session.execute(text("ALTER TABLE autorizaciones_sst DROP COLUMN IF EXISTS numero_autorizacion;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_certificado_empleado;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_log_ingreso_empleado;"))
        db.session.commit()
        print("✅ Rollback 3.2.0 ejecutado")


if __name__ == '__main__':
    migrate()
