"""
Migración: Agregar operadores PILA a operadores_aportes
Fecha: 2026-03-22

- Amplía el CHECK constraint para incluir tipo 'PILA'
- Inserta los 7 operadores PILA autorizados por la UGPP en Colombia
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

PILA_OPERADORES = [
    {'nombre': 'APORTES EN LÍNEA S.A.',         'nit': '9001472381'},
    {'nombre': 'CENET S.A. (MIPLANILLA.COM)',    'nit': '8002198768'},
    {'nombre': 'ACH COLOMBIA S.A. (SOI)',        'nit': '8300537006'},
    {'nombre': 'SIMPLE S.A.',                    'nit': '9000973338'},
    {'nombre': 'ENLACE OPERATIVO S.A. (SUAPORTE)', 'nit': '8909305340'},
    {'nombre': 'ASOPAGOS S.A.',                  'nit': '9001233004'},
    {'nombre': 'FEDECAJAS',                      'nit': '8605055728'},
]


def migrate():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("MIGRACIÓN: Operadores PILA")
        print("=" * 60)

        # 1) Ampliar CHECK constraint para incluir 'PILA'
        print("\n1. Modificando constraint check_tipo_operador...")
        db.session.execute(text(
            "ALTER TABLE operadores_aportes "
            "DROP CONSTRAINT IF EXISTS check_tipo_operador"
        ))
        db.session.execute(text(
            "ALTER TABLE operadores_aportes "
            "ADD CONSTRAINT check_tipo_operador "
            "CHECK (tipo IN ('EPS', 'AFP', 'ARL', 'PILA'))"
        ))
        db.session.commit()
        print("   ✅ Constraint actualizado")

        # 2) Insertar operadores PILA (solo si no existen)
        print(f"\n2. Insertando {len(PILA_OPERADORES)} operadores PILA...")
        insertados = 0
        for op in PILA_OPERADORES:
            existe = db.session.execute(text(
                "SELECT id FROM operadores_aportes WHERE nit = :nit AND tipo = 'PILA'"
            ), {'nit': op['nit']}).fetchone()

            if not existe:
                db.session.execute(text(
                    "INSERT INTO operadores_aportes (nombre, tipo, nit, activo) "
                    "VALUES (:nombre, 'PILA', :nit, TRUE)"
                ), {'nombre': op['nombre'], 'nit': op['nit']})
                print(f"   ✅ {op['nombre']}")
                insertados += 1
            else:
                print(f"   ⏭️  {op['nombre']} (ya existe)")

        db.session.commit()
        print(f"\n✅ MIGRACIÓN COMPLETADA — {insertados} operadores PILA insertados")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text(
            "DELETE FROM operadores_aportes WHERE tipo = 'PILA'"
        ))
        db.session.execute(text(
            "ALTER TABLE operadores_aportes "
            "DROP CONSTRAINT IF EXISTS check_tipo_operador"
        ))
        db.session.execute(text(
            "ALTER TABLE operadores_aportes "
            "ADD CONSTRAINT check_tipo_operador "
            "CHECK (tipo IN ('EPS', 'AFP', 'ARL'))"
        ))
        db.session.commit()
        print("✅ Rollback ejecutado")


if __name__ == '__main__':
    migrate()
