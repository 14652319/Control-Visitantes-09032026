"""
Verificar estructura de tablas en la base de datos
"""
import psycopg

try:
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="G3st0radm$2025.",
        dbname="control_visitantes"
    )
    
    cursor = conn.cursor()
    
    # Ver todas las tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tablas = cursor.fetchall()
    
    print("=" * 60)
    print("TABLAS EN LA BASE DE DATOS")
    print("=" * 60)
    for tabla in tablas:
        print(f"  - {tabla[0]}")
    
    # Ver columnas de la tabla usuarios
    print("\n" + "=" * 60)
    print("COLUMNAS DE LA TABLA USUARIOS")
    print("=" * 60)
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'usuarios'
        ORDER BY ordinal_position
    """)
    
    columnas = cursor.fetchall()
    for col in columnas:
        nullable = "NULL" if col[3] == 'YES' else "NOT NULL"
        length = f"({col[2]})" if col[2] else ""
        print(f"  {col[0]:25} {col[1]}{length:20} {nullable}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"Error: {e}")
