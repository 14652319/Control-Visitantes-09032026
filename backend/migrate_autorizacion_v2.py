"""
========================================
MIGRACIÓN: Autorizaciones SST v2
========================================
Agrega nuevos campos a:
  - autorizaciones_sst: numero_autorizacion, planilla_ss_id, observaciones,
                        carta_presentacion_ruta, fecha_autorizacion
  - planillas_ss: operador_id, numero_planilla, tipo_planilla
  - Nueva tabla: empleados_por_autorizacion

Ejecutar: python migrate_autorizacion_v2.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import app
from app.extensions import db
from sqlalchemy import text


def run_migration():
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        try:
            # ─── autorizaciones_sst ────────────────────────────────────────────────
            cols_sst = {
                r[0] for r in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='autorizaciones_sst'"
                ))
            }

            if 'numero_autorizacion' not in cols_sst:
                conn.execute(text(
                    "ALTER TABLE autorizaciones_sst "
                    "ADD COLUMN numero_autorizacion VARCHAR(20) UNIQUE"
                ))
                print("✅ autorizaciones_sst.numero_autorizacion — agregado")

            if 'planilla_ss_id' not in cols_sst:
                conn.execute(text(
                    "ALTER TABLE autorizaciones_sst "
                    "ADD COLUMN planilla_ss_id INTEGER REFERENCES planillas_ss(id)"
                ))
                print("✅ autorizaciones_sst.planilla_ss_id — agregado")

            if 'observaciones' not in cols_sst:
                conn.execute(text(
                    "ALTER TABLE autorizaciones_sst "
                    "ADD COLUMN observaciones VARCHAR(1000)"
                ))
                print("✅ autorizaciones_sst.observaciones — agregado")

            if 'carta_presentacion_ruta' not in cols_sst:
                conn.execute(text(
                    "ALTER TABLE autorizaciones_sst "
                    "ADD COLUMN carta_presentacion_ruta VARCHAR(500)"
                ))
                print("✅ autorizaciones_sst.carta_presentacion_ruta — agregado")

            if 'fecha_autorizacion' not in cols_sst:
                conn.execute(text(
                    "ALTER TABLE autorizaciones_sst "
                    "ADD COLUMN fecha_autorizacion DATE"
                ))
                print("✅ autorizaciones_sst.fecha_autorizacion — agregado")

            # Rellenar numero_autorizacion en registros existentes
            conn.execute(text(
                "UPDATE autorizaciones_sst "
                "SET numero_autorizacion = 'AC-' || LPAD(id::text, 8, '0') "
                "WHERE numero_autorizacion IS NULL"
            ))
            print("✅ autorizaciones_sst.numero_autorizacion — backfill completado")

            # ─── planillas_ss ──────────────────────────────────────────────────────
            cols_plan = {
                r[0] for r in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='planillas_ss'"
                ))
            }

            if 'operador_id' not in cols_plan:
                conn.execute(text(
                    "ALTER TABLE planillas_ss "
                    "ADD COLUMN operador_id INTEGER REFERENCES operadores_aportes(id)"
                ))
                print("✅ planillas_ss.operador_id — agregado")

            if 'numero_planilla' not in cols_plan:
                conn.execute(text(
                    "ALTER TABLE planillas_ss "
                    "ADD COLUMN numero_planilla VARCHAR(50)"
                ))
                print("✅ planillas_ss.numero_planilla — agregado")

            if 'tipo_planilla' not in cols_plan:
                conn.execute(text(
                    "ALTER TABLE planillas_ss "
                    "ADD COLUMN tipo_planilla CHAR(1)"
                ))
                print("✅ planillas_ss.tipo_planilla — agregado")

            # ─── empleados_por_autorizacion ────────────────────────────────────────
            tablas = {
                r[0] for r in conn.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public'"
                ))
            }

            if 'empleados_por_autorizacion' not in tablas:
                conn.execute(text("""
                    CREATE TABLE empleados_por_autorizacion (
                        id                          SERIAL PRIMARY KEY,
                        autorizacion_id             INTEGER NOT NULL REFERENCES autorizaciones_sst(id) ON DELETE CASCADE,
                        empleado_id                 INTEGER NOT NULL REFERENCES empleados_contratistas(id),
                        trabajo_altura              BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_energias_peligrosas BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_espacios_confinados BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_caliente            BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_izaje_cargas        BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_excavacion          BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_sustancias_quimicas BOOLEAN NOT NULL DEFAULT FALSE,
                        trabajo_otro                VARCHAR(100),
                        documentos_json             TEXT,
                        created_at                  TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
                print("✅ Tabla empleados_por_autorizacion — creada")
            else:
                print("ℹ️  Tabla empleados_por_autorizacion ya existe — omitida")

            trans.commit()
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ ERROR en migración: {e}")
            raise
        finally:
            conn.close()


if __name__ == '__main__':
    run_migration()
