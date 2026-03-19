"""
Migración: Crear tablas planillas_ss, autorizaciones_sst, log_ingresos_contratistas
Fecha: 2026-03-19
Checkpoint: 3.1.4
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("[1/3] Creando tabla planillas_ss...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS planillas_ss (
                id              SERIAL PRIMARY KEY,
                empresa_id      INTEGER NOT NULL REFERENCES empresas_contratistas(id),
                periodo         VARCHAR(7)   NOT NULL,
                fecha_pago      DATE         NOT NULL,
                vigencia_fin    DATE         NOT NULL,
                archivo_nombre  VARCHAR(200),
                archivo_ruta    VARCHAR(500),
                estado          VARCHAR(20)  NOT NULL DEFAULT 'pendiente',
                created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                verificado_por  INTEGER REFERENCES usuarios(id),
                verificado_at   TIMESTAMP,
                CONSTRAINT check_estado_planilla CHECK (estado IN ('pendiente', 'verificada', 'rechazada')),
                CONSTRAINT unique_empresa_periodo UNIQUE (empresa_id, periodo)
            );
        """))

        print("[2/3] Creando tabla autorizaciones_sst...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS autorizaciones_sst (
                id              SERIAL PRIMARY KEY,
                empresa_id      INTEGER NOT NULL REFERENCES empresas_contratistas(id),
                sede_id         INTEGER REFERENCES sedes(id),
                labor           VARCHAR(300) NOT NULL,
                fecha_inicio    DATE         NOT NULL,
                fecha_fin       DATE         NOT NULL,
                estado          VARCHAR(20)  NOT NULL DEFAULT 'borrador',
                pdf_ruta        VARCHAR(500),
                created_by      INTEGER NOT NULL REFERENCES usuarios(id),
                aprobado_by     INTEGER REFERENCES usuarios(id),
                created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                CONSTRAINT check_estado_autorizacion_sst
                    CHECK (estado IN ('borrador', 'revision', 'aprobada', 'vencida', 'anulada'))
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_autorizacion_sst_empresa
                ON autorizaciones_sst(empresa_id, estado);
            CREATE INDEX IF NOT EXISTS idx_autorizacion_sst_vigencia
                ON autorizaciones_sst(fecha_fin) WHERE estado = 'aprobada';
        """))

        print("[3/3] Creando tabla log_ingresos_contratistas...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS log_ingresos_contratistas (
                id                  SERIAL PRIMARY KEY,
                empleado_id         INTEGER NOT NULL REFERENCES empleados_contratistas(id),
                autorizacion_sst_id INTEGER NOT NULL REFERENCES autorizaciones_sst(id),
                sede_id             INTEGER REFERENCES sedes(id),
                tipo_evento         VARCHAR(10)  NOT NULL,
                timestamp_evento    TIMESTAMP    NOT NULL DEFAULT NOW(),
                registrado_por      INTEGER REFERENCES usuarios(id),
                observaciones       VARCHAR(500),
                CONSTRAINT check_tipo_evento_contratista CHECK (tipo_evento IN ('ingreso', 'salida'))
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_log_contratista_fecha
                ON log_ingresos_contratistas(timestamp_evento, sede_id);
        """))

        db.session.commit()
        print("✅ 3 tablas principales SST creadas")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS log_ingresos_contratistas CASCADE;"))
        db.session.execute(text("DROP TABLE IF EXISTS autorizaciones_sst CASCADE;"))
        db.session.execute(text("DROP TABLE IF EXISTS planillas_ss CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
