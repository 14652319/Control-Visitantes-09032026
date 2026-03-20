"""
Script de backup para CHECKPOINT 2.1 - Pre-SST
Usa las mismas credenciales de conexión que el backend principal
"""
import subprocess
from datetime import datetime
import os
import sys

def crear_backup():
    """Crea backup completo de la base de datos"""
    print("=" * 70)
    print("CHECKPOINT 2.1: BACKUP PRE-SST")
    print("=" * 70)
    
    # Configuración
    backup_dir = r"D:\0.A. Proyectos\0.0. BackUp\control-visitantes-pre-sst"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.sql")
    
    # Credenciales de PostgreSQL (mismas que backend/.env)
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'control_visitantes'
    db_user = 'postgres'
    db_password = 'G3st0radm$2025.@'
    
    # Path a pg_dump
    pg_dump_path = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
    
    # Comando pg_dump
    cmd = [
        pg_dump_path,
        '-h', db_host,
        '-p', db_port,
        '-U', db_user,
        '-d', db_name,
        '-F', 'p',  # Formato plain SQL
        '--inserts',  # Usar INSERT statements
        '--column-inserts',  # Incluir nombres de columnas
        '-f', backup_file
    ]
    
    # Configurar variable de entorno PGPASSWORD
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    print(f"\n📦 Creando backup de: {db_name}")
    print(f"📁 Destino: {backup_file}")
    print("\n🔄 Ejecutando pg_dump...")
    
    try:
        # Ejecutar pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            # Verificar tamaño del archivo
            if os.path.exists(backup_file):
                size_bytes = os.path.getsize(backup_file)
                size_kb = size_bytes / 1024
                size_mb = size_kb / 1024
                
                print(f"\n✅ BACKUP COMPLETADO EXITOSAMENTE")
                print(f"\n📊 Detalles:")
                print(f"   - Archivo: db_backup_{timestamp}.sql")
                print(f"   - Tamaño: {size_kb:.2f} KB ({size_mb:.2f} MB)")
                print(f"   - Ubicación: {backup_dir}")
                
                if size_kb < 100:
                    print(f"\n⚠️  ADVERTENCIA: Tamaño menor a 100 KB (base de datos vacía?)")
                    return False
                
                return True
            else:
                print(f"\n❌ ERROR: Archivo no creado: {backup_file}")
                return False
        else:
            print(f"\n❌ ERROR en pg_dump:")
            print(f"STDERR: {result.stderr}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n❌ TIMEOUT: El backup tomó más de 5 minutos")
        return False
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        return False

if __name__ == "__main__":
    exito = crear_backup()
    sys.exit(0 if exito else 1)
