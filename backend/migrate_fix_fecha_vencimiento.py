"""
Migración: Convertir fecha_vencimiento de TIMESTAMP a DATE
"""
from app import create_app
from app.extensions import db

def migrar():
    app = create_app()
    
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("MIGRACIÓN: Convertir fecha_vencimiento a DATE")
            print("="*60)
            
            # Verificar tipo actual
            print("\n1️⃣ Verificando tipo actual de fecha_vencimiento...")
            result = db.session.execute(db.text("""
                SELECT data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'autorizaciones_ingreso'
                AND column_name = 'fecha_vencimiento';
            """))
            
            row = result.fetchone()
            if row:
                tipo_actual, nullable, default = row
                print(f"   Tipo actual: {tipo_actual}")
                print(f"   Nullable: {nullable}")
                print(f"   Default: {default}")
            
            # Convertir la columna a DATE
            print("\n2️⃣ Convirtiendo columna a DATE...")
            db.session.execute(db.text("""
                ALTER TABLE autorizaciones_ingreso
                ALTER COLUMN fecha_vencimiento TYPE DATE
                USING fecha_vencimiento::DATE;
            """))
            
            db.session.commit()
            print("   ✅ Columna convertida exitosamente")
            
            # Verificar el cambio
            print("\n3️⃣ Verificando cambio...")
            result = db.session.execute(db.text("""
                SELECT data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'autorizaciones_ingreso'
                AND column_name = 'fecha_vencimiento';
            """))
            
            row = result.fetchone()
            if row:
                tipo_nuevo, nullable, default = row
                print(f"   Nuevo tipo: {tipo_nuevo}")
                print(f"   Nullable: {nullable}")
                print(f"   Default: {default}")
            
            # Mostrar algunas autorizaciones
            print("\n4️⃣ Verificando registros existentes...")
            result = db.session.execute(db.text("""
                SELECT id, num_identificacion, fecha_vencimiento, estado
                FROM autorizaciones_ingreso
                ORDER BY fecha_creacion DESC
                LIMIT 5;
            """))
            
            registros = result.fetchall()
            print(f"   {len(registros)} registros recientes:")
            for r in registros:
                print(f"      • ID: {r[0]}, NumID: {r[1]}, Venc: {r[2]}, Estado: {r[3]}")
            
            print("\n" + "="*60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrar()
