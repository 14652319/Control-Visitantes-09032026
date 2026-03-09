"""
========================================
MIGRACIÓN: Permitir sede_id NULL para usuarios Master
Sistema de Control de Visitantes
========================================

Este script modifica la columna sede_id en la tabla usuarios
para permitir valores NULL (usuarios Master tienen acceso global)

Autor: Sistema de Control de Visitantes
Fecha: Marzo 6, 2026
"""

import psycopg
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def conectar_db():
    """Conecta a la base de datos PostgreSQL"""
    # Usar DATABASE_URL si está disponible
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Convertir de formato SQLAlchemy a psycopg3
        if database_url.startswith('postgresql+psycopg://'):
            database_url = database_url.replace('postgresql+psycopg://', 'postgresql://')
        return psycopg.connect(database_url)
    
    # Fallback a conexiones individuales
    connection_string = (
        f"host={os.getenv('DB_HOST', 'localhost')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'control_visitantes')} "
        f"user={os.getenv('DB_USER', 'postgres')} "
        f"password={os.getenv('DB_PASSWORD', '')}"
    )
    return psycopg.connect(connection_string)

def ejecutar_migracion():
    """Ejecuta la migración de base de datos"""
    print("="*60)
    print("MIGRACIÓN: Permitir sede_id NULL para usuarios Master")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        print("✓ Conexión establecida con la base de datos")
        print()
        
        # 1. Modificar columna sede_id para permitir NULL
        print("1. Modificando columna sede_id para permitir NULL...")
        cursor.execute("""
            ALTER TABLE usuarios 
            ALTER COLUMN sede_id DROP NOT NULL;
        """)
        print("   ✓ Columna sede_id ahora permite valores NULL")
        print()
        
        # 2. Actualizar usuarios Master existentes con alguna sede asignada
        # (opcional: puedes decidir dejarlos con su sede o ponerlos en NULL)
        print("2. Verificando usuarios Master existentes...")
        cursor.execute("""
            SELECT id, usuario, sede_id 
            FROM usuarios 
            WHERE rol = 'usuario_master';
        """)
        masters = cursor.fetchall()
        
        if masters:
            print(f"   Encontrados {len(masters)} usuarios Master:")
            for master_id, usuario, sede_id in masters:
                print(f"   - {usuario} (ID: {master_id}, Sede actual: {sede_id})")
            
            print()
            print("   NOTA: Se mantienen las sedes actuales de los Master.")
            print("   Puedes cambiarlas a NULL desde el panel admin si lo deseas.")
        else:
            print("   No se encontraron usuarios Master en el sistema.")
        print()
        
        # 3. Guardar cambios
        conn.commit()
        print("✓ Migración completada exitosamente")
        print()
        
        # 4. Verificar el cambio
        print("4. Verificando cambio en la estructura...")
        cursor.execute("""
            SELECT column_name, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'usuarios' AND column_name = 'sede_id';
        """)
        resultado = cursor.fetchone()
        
        if resultado:
            columna, nullable, tipo = resultado
            print(f"   Columna: {columna}")
            print(f"   Tipo: {tipo}")
            print(f"   Permite NULL: {nullable}")
            
            if nullable == 'YES':
                print()
                print("✓ VERIFICACIÓN EXITOSA: La columna sede_id ahora permite NULL")
            else:
                print()
                print("⚠ ADVERTENCIA: La columna aún no permite NULL")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("MIGRACIÓN COMPLETADA")
        print("="*60)
        print()
        print("CAMBIOS REALIZADOS:")
        print("- ✓ Columna usuarios.sede_id ahora permite valores NULL")
        print("- ✓ Usuarios Master pueden tener sede_id = NULL (acceso global)")
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Reiniciar el servidor backend")
        print("2. Desde el panel admin, puedes editar usuarios Master")
        print("3. El campo Sede será opcional para usuarios Master")
        print()
        
    except Exception as e:
        print()
        print("❌ ERROR durante la migración:")
        print(f"   {str(e)}")
        print()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
    
    return True

if __name__ == "__main__":
    exito = ejecutar_migracion()
    
    if not exito:
        print("La migración falló. Por favor revisa los errores anteriores.")
        exit(1)
    else:
        print("Migración completada con éxito.")
        exit(0)
