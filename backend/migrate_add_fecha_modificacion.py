"""
========================================
MIGRACIÓN: Agregar fecha_modificacion a autorizaciones_ingreso
Sistema de Control de Visitantes
========================================
"""

import psycopg
import os
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()


def conectar_db():
    """Conecta a la base de datos PostgreSQL"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgresql+psycopg://'):
            database_url = database_url.replace('postgresql+psycopg://', 'postgresql://')
        return psycopg.connect(database_url)
    
    connection_string = (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', '')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'control_visitantes')}"
    )
    return psycopg.connect(connection_string)


def migrate():
    """Ejecuta la migración para agregar fecha_modificacion"""
    
    try:
        with conectar_db() as conn:
            with conn.cursor() as cur:
                print("="*60)
                print("MIGRACIÓN: Agregar fecha_modificacion a autorizaciones_ingreso")
                print("="*60)
                
                # 1. Verificar si la columna ya existe
                print("\n📋 Paso 1: Verificando si fecha_modificacion existe...")
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='autorizaciones_ingreso' 
                    AND column_name='fecha_modificacion'
                """)
                
                existe = cur.fetchone()
                
                if existe:
                    print("   ⚠️  La columna fecha_modificacion ya existe")
                    print("\n✅ No se requieren cambios")
                    return
                
                print("   La columna no existe, procediendo a agregarla...")
                
                # 2. Agregar la columna fecha_modificacion
                print("\n📋 Paso 2: Agregando columna fecha_modificacion...")
                cur.execute("""
                    ALTER TABLE autorizaciones_ingreso
                    ADD COLUMN fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                
                print("   ✅ Columna fecha_modificacion agregada exitosamente")
                
                # 3. Actualizar registros existentes
                print("\n📋 Paso 3: Actualizando registros existentes...")
                cur.execute("""
                    UPDATE autorizaciones_ingreso
                    SET fecha_modificacion = fecha_creacion
                    WHERE fecha_modificacion IS NULL
                """)
                
                filas_actualizadas = cur.rowcount
                print(f"   ✅ {filas_actualizadas} registros actualizados")
                
                # Commit de los cambios
                conn.commit()
                
                # 4. Verificar los cambios
                print("\n📋 Paso 4: Verificando estructura final...")
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name='autorizaciones_ingreso' 
                    AND column_name IN ('fecha_creacion', 'fecha_modificacion')
                    ORDER BY column_name
                """)
                
                print("\n   Campos de timestamp en autorizaciones_ingreso:")
                for row in cur.fetchall():
                    print(f"   - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3] or 'N/A'})")
                
                print("\n" + "="*60)
                print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
                print("="*60)
                print("\nResumen:")
                print("  ✓ Columna fecha_modificacion agregada")
                print(f"  ✓ {filas_actualizadas} registros existentes actualizados")
                print("\n💡 La columna se actualiza automáticamente en cada modificación")
                print("="*60)
                
    except psycopg.Error as e:
        print(f"\n❌ ERROR DE BASE DE DATOS:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("\n🚀 Iniciando migración de fecha_modificacion...")
    migrate()
    print("\n✅ Proceso completado.\n")
