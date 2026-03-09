"""
========================================
MIGRACIÓN: Agregar campos de contacto a autorizaciones_ingreso
Agrega num_telefono y dir_correo a la tabla autorizaciones_ingreso
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
    """Ejecuta la migración para agregar campos de contacto"""
    
    try:
        with conectar_db() as conn:
            with conn.cursor() as cur:
                print("="*60)
                print("MIGRACIÓN: Agregar campos de contacto a autorizaciones_ingreso")
                print("="*60)
                
                # 1. Verificar si los campos ya existen
                print("\n📋 Paso 1: Verificando campos existentes...")
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='autorizaciones_ingreso' 
                    AND column_name IN ('num_telefono', 'dir_correo')
                """)
                
                campos_existentes = [row[0] for row in cur.fetchall()]
                print(f"   Campos existentes: {campos_existentes if campos_existentes else 'Ninguno'}")
                
                # 2. Agregar num_telefono si no existe
                if 'num_telefono' not in campos_existentes:
                    print("\n📋 Paso 2: Agregando campo num_telefono...")
                    cur.execute("""
                        ALTER TABLE autorizaciones_ingreso
                        ADD COLUMN num_telefono VARCHAR(100)
                    """)
                    print("   ✅ Campo num_telefono agregado exitosamente")
                else:
                    print("\n📋 Paso 2: Campo num_telefono ya existe, omitiendo...")
                
                # 3. Agregar dir_correo si no existe
                if 'dir_correo' not in campos_existentes:
                    print("\n📋 Paso 3: Agregando campo dir_correo...")
                    cur.execute("""
                        ALTER TABLE autorizaciones_ingreso
                        ADD COLUMN dir_correo VARCHAR(100)
                    """)
                    print("   ✅ Campo dir_correo agregado exitosamente")
                else:
                    print("\n📋 Paso 3: Campo dir_correo ya existe, omitiendo...")
                
                # Commit de los cambios
                conn.commit()
                
                # 4. Verificar los cambios
                print("\n📋 Paso 4: Verificando estructura final...")
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='autorizaciones_ingreso' 
                    AND column_name IN ('num_telefono', 'dir_correo')
                    ORDER BY column_name
                """)
                
                print("\n   Campos de contacto en autorizaciones_ingreso:")
                for row in cur.fetchall():
                    print(f"   - {row[0]}: {row[1]} (nullable: {row[2]})")
                
                print("\n" + "="*60)
                print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
                print("="*60)
                print("\nResumen de cambios:")
                
                if 'num_telefono' not in campos_existentes:
                    print("  ✓ Campo num_telefono agregado")
                else:
                    print("  • Campo num_telefono ya existía")
                    
                if 'dir_correo' not in campos_existentes:
                    print("  ✓ Campo dir_correo agregado")
                else:
                    print("  • Campo dir_correo ya existía")
                
                print("\n💡 Los campos son opcionales (nullable)")
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
    print("\n🚀 Iniciando migración de campos de contacto...")
    migrate()
    print("\n✅ Proceso completado. Los campos num_telefono y dir_correo están disponibles.\n")
