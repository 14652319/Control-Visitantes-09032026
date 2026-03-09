"""
Script para crear la base de datos control_visitantes
"""
import psycopg

print("="*60)
print("CREANDO BASE DE DATOS")
print("="*60)

try:
    # Conectar a PostgreSQL
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="G3st0radm$2025.",
        dbname="postgres",
        autocommit=True
    )
    
    cursor = conn.cursor()
    
    # Verificar si la base de datos existe
    cursor.execute("""
        SELECT datname FROM pg_database 
        WHERE datname = 'control_visitantes'
    """)
    
    if cursor.fetchone():
        print("⚠️  La base de datos 'control_visitantes' ya existe")
        print("   Eliminándola...")
        cursor.execute("DROP DATABASE control_visitantes")
        print("   ✅ Base de datos eliminada")
    
    # Crear la base de datos
    cursor.execute("CREATE DATABASE control_visitantes")
    print("✅ Base de datos 'control_visitantes' creada exitosamente")
    
    cursor.close()
    conn.close()
    
    print("="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
