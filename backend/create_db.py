"""
Script para crear la base de datos PostgreSQL
"""
import psycopg
from urllib.parse import urlparse

# Conectar a PostgreSQL (base de datos por defecto 'postgres')
conn_url = "postgresql+psycopg://postgres:G3st0radm%242025.@localhost:5432/postgres"
parsed = urlparse(conn_url.replace('postgresql+psycopg', 'postgresql'))

try:
    # Extraer info de conexión
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    
    # Conectar a la base de datos postgres (por defecto)
    conn = psycopg.connect(
        f"host={host} port={port} user={user} password={password} dbname=postgres",
        autocommit=True
    )
    cursor = conn.cursor()
    
    # Crear la base de datos
    cursor.execute("DROP DATABASE IF EXISTS control_visitantes")
    cursor.execute("CREATE DATABASE control_visitantes")
    
    print("✅ Base de datos 'control_visitantes' creada exitosamente")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
