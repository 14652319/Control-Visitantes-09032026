"""
Script para exportar base de datos PostgreSQL
"""
import subprocess
import os
from datetime import datetime

# Configuracion
DB_NAME = "control_visitantes"
DB_USER = "postgres"
DB_PASSWORD = "G3st0radm$2025.@"
DB_HOST = "localhost"
DB_PORT = "5432"

fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = r"D:\0.A. Proyectos\0.0. BackUp\BackUp 1.1. Control de Acceso Visitantes\backup_control_visitantes_20260318_131901\database"
pg_dump_path = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

# Asegurar que existe el directorio
os.makedirs(backup_path, exist_ok=True)

# Configurar password en variable de entorno
os.environ['PGPASSWORD'] = DB_PASSWORD

print("Exportando base de datos...")
print(f"Database: {DB_NAME}")
print(f"Destino: {backup_path}")
print("")

# Export completo
archivo_sql = os.path.join(backup_path, f"backup_completo_{DB_NAME}_{fecha_hora}.sql")
print(f"1. Creando dump SQL completo...")

try:
    result = subprocess.run([
        pg_dump_path,
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-F", "p",  # Plain text
        "--no-owner",
        "--no-acl",
        "-f", archivo_sql
    ], capture_output=True, text=True, check=True)
    
    tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
    print(f"   OK Dump creado: {tamanio:.2f} MB")
except subprocess.CalledProcessError as e:
    print(f"   ERROR: {e.stderr}")
except Exception as e:
    print(f"   ERROR: {str(e)}")

# Export formato custom
archivo_custom = os.path.join(backup_path, f"backup_custom_{DB_NAME}_{fecha_hora}.backup")
print(f"2. Creando backup formato custom...")

try:
    result = subprocess.run([
        pg_dump_path,
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-F", "c",  # Custom format
        "-f", archivo_custom
    ], capture_output=True, text=True, check=True)
    
    tamanio = os.path.getsize(archivo_custom) / (1024 * 1024)
    print(f"   OK Backup custom creado: {tamanio:.2f} MB")
except subprocess.CalledProcessError as e:
    print(f"   ERROR: {e.stderr}")
except Exception as e:
    print(f"   ERROR: {str(e)}")

# Export solo esquema
archivo_esquema = os.path.join(backup_path, f"schema_only_{DB_NAME}_{fecha_hora}.sql")
print(f"3. Exportando solo esquema...")

try:
    result = subprocess.run([
        pg_dump_path,
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-F", "p",
        "--schema-only",
        "--no-owner",
        "--no-acl",
        "-f", archivo_esquema
    ], capture_output=True, text=True, check=True)
    
    tamanio = os.path.getsize(archivo_esquema) / (1024 * 1024)
    print(f"   OK Esquema exportado: {tamanio:.2f} MB")
except subprocess.CalledProcessError as e:
    print(f"   ERROR: {e.stderr}")
except Exception as e:
    print(f"   ERROR: {str(e)}")

# Limpiar password
del os.environ['PGPASSWORD']

print("")
print("================================================")
print("EXPORTACION DE BASE DE DATOS COMPLETADA")
print("================================================")
