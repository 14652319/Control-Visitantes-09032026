"""
Migración: Crear tablas empleados_contratistas y certificados_trabajo
Fecha: 2026-03-19
Checkpoint: 3.1.3
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("[1/2] Creando tabla empleados_contratistas...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS empleados_contratistas (
                id              SERIAL PRIMARY KEY,
                empresa_id      INTEGER NOT NULL REFERENCES empresas_contratistas(id),
                tipo_id         VARCHAR(5)   NOT NULL,
                num_id          VARCHAR(20)  NOT NULL,
                nombres         VARCHAR(100) NOT NULL,
                apellidos       VARCHAR(100) NOT NULL,
                cargo           VARCHAR(100),
                eps_id          INTEGER REFERENCES operadores_aportes(id),
                afp_id          INTEGER REFERENCES operadores_aportes(id),
                arl_id          INTEGER REFERENCES operadores_aportes(id),
                estado          VARCHAR(20)  NOT NULL DEFAULT 'activo',
                created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                CONSTRAINT check_tipo_id_empleado CHECK (tipo_id IN ('CC', 'CE', 'PA', 'PEP')),
                CONSTRAINT check_estado_empleado CHECK (estado IN ('activo', 'inactivo')),
                CONSTRAINT unique_empleado_empresa UNIQUE (empresa_id, tipo_id, num_id)
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_empleado_empresa_estado
                ON empleados_contratistas(empresa_id, estado);
            CREATE INDEX IF NOT EXISTS idx_empleado_identificacion
                ON empleados_contratistas(tipo_id, num_id);
        """))

        print("[2/2] Creando tabla certificados_trabajo...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS certificados_trabajo (
                id                  SERIAL PRIMARY KEY,
                empleado_id         INTEGER NOT NULL REFERENCES empleados_contratistas(id),
                tipo_certificado    VARCHAR(50)  NOT NULL,
                nombre_certificado  VARCHAR(200) NOT NULL,
                fecha_expedicion    DATE         NOT NULL,
                fecha_vencimiento   DATE,
                archivo_nombre      VARCHAR(200),
                archivo_ruta        VARCHAR(500),
                verificado          BOOLEAN      NOT NULL DEFAULT FALSE,
                created_at          TIMESTAMP    NOT NULL DEFAULT NOW()
            );
        """))
        db.session.commit()
        print("✅ Tablas empleados y certificados creadas")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS certificados_trabajo CASCADE;"))
        db.session.execute(text("DROP TABLE IF EXISTS empleados_contratistas CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
