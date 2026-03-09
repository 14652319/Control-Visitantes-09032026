"""
Script para validar la conexión a PostgreSQL
"""
import psycopg

# Diferentes variantes de la contraseña para probar
passwords_to_test = [
    "G3st0radm$2025.",      # Original
    "G3st0radm$2025",       # Sin punto final
    "G3st0radm$$2025.",     # $ duplicado
    "G3st0radm$$2025",      # $ duplicado sin punto
]

host = "localhost"
port = 5432
user = "postgres"
dbname = "postgres"  # Conectar a la BD por defecto

print("="*60)
print("VALIDANDO CONEXIÓN A POSTGRESQL")
print("="*60)

for idx, password in enumerate(passwords_to_test, 1):
    try:
        print(f"\n[{idx}] Probando: '{password[:8]}***' ", end="")
        
        conn = psycopg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=3
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        
        print("✅ ¡CONEXIÓN EXITOSA!")
        print(f"    PostgreSQL Version: {version[0][:50]}...")
        print(f"    Contraseña correcta: {password}")
        
        # Verificar si existe la base de datos control_visitantes
        cursor.execute("""
            SELECT datname FROM pg_database 
            WHERE datname = 'control_visitantes'
        """)
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"    ✅ Base de datos 'control_visitantes' existe")
        else:
            print(f"    ⚠️  Base de datos 'control_visitantes' NO existe (se debe crear)")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"CONTRASEÑA VÁLIDA: {password}")
        print(f"{'='*60}")
        break
        
    except psycopg.OperationalError as e:
        print(f"❌ Falló")
        error_msg = str(e)
        if "password" in error_msg.lower() or "autentificaci" in error_msg.lower():
            print(f"    Motivo: Contraseña incorrecta")
        else:
            print(f"    Motivo: {error_msg[:100]}")
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
else:
    print("\n" + "="*60)
    print("❌ NINGUNA CONTRASEÑA FUNCIONÓ")
    print("="*60)
    print("\nPosibles soluciones:")
    print("1. Verifica la contraseña en pgAdmin")
    print("2. Usa este comando en psql para cambiarla:")
    print("   ALTER USER postgres PASSWORD 'G3st0radm$2025.';")
