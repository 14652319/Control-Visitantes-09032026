"""
Verificar usuarios en la base de datos
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
    cursor.execute("SELECT id, usuario, rol, estado FROM usuarios")
    usuarios = cursor.fetchall()
    
    print("Usuarios en la base de datos:")
    print("-" * 60)
    for user in usuarios:
        print(f"ID: {user[0]}, Usuario: '{user[1]}', Rol: {user[2]}, Estado: {user[3]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
