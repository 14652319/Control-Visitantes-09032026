import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        r = conn.execute(text(
            "SELECT column_name, column_default FROM information_schema.columns "
            "WHERE table_name='empresas_contratistas' AND column_name='tipo_tercero'"
        ))
        row = r.fetchone()
        if row:
            print("OK — tipo_tercero existe, default:", row[1])
        else:
            print("FALTA — agregando columna...")
            conn.execute(text(
                "ALTER TABLE empresas_contratistas "
                "ADD COLUMN tipo_tercero VARCHAR(30) NOT NULL DEFAULT 'CONTRATISTA'"
            ))
            conn.commit()
            print("LISTO — columna agregada")
