"""
========================================
MIGRACIÓN: Crear tabla configuracion_sistema
Sistema de Control de Visitantes
========================================

Este script crea la tabla de configuración del sistema
y establece los valores por defecto

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
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgresql+psycopg://'):
            database_url = database_url.replace('postgresql+psycopg://', 'postgresql://')
        return psycopg.connect(database_url)
    
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
    print("MIGRACIÓN: Tabla configuracion_sistema")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        print("✓ Conexión establecida con la base de datos")
        print()
        
        # 1. Crear tabla configuracion_sistema
        print("1. Creando tabla configuracion_sistema...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id SERIAL PRIMARY KEY,
                clave VARCHAR(100) NOT NULL UNIQUE,
                valor VARCHAR(500) NOT NULL,
                descripcion TEXT,
                tipo_dato VARCHAR(50) NOT NULL DEFAULT 'string',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✓ Tabla configuracion_sistema creada")
        print()
        
        # 2. Crear índice en clave
        print("2. Creando índice en columna clave...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_configuracion_clave 
            ON configuracion_sistema(clave);
        """)
        print("   ✓ Índice creado")
        print()
        
        # 3. Insertar configuraciones por defecto
        print("3. Insertando configuraciones por defecto...")
        
        configuraciones = [
            ('dias_vigencia_autorizacion', '1', 'Días de vigencia de las autorizaciones de ingreso (24 horas = 1 día)', 'int'),
            ('max_intentos_login', '10', 'Máximo número de intentos fallidos de login antes de bloquear', 'int'),
            ('tiempo_sesion_minutos', '45', 'Tiempo de sesión en minutos antes de expirar', 'int'),
            ('nombre_empresa', 'Supertiendas Cañaveral SAS', 'Nombre de la empresa', 'string'),
        ]
        
        for clave, valor, descripcion, tipo_dato in configuraciones:
            cursor.execute("""
                INSERT INTO configuracion_sistema (clave, valor, descripcion, tipo_dato)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (clave) DO UPDATE 
                SET descripcion = EXCLUDED.descripcion,
                    tipo_dato = EXCLUDED.tipo_dato;
            """, (clave, valor, descripcion, tipo_dato))
            print(f"   ✓ {clave} = {valor}")
        
        print()
        
        # 4. Guardar cambios
        conn.commit()
        print("✓ Migración completada exitosamente")
        print()
        
        # 5. Verificar configuraciones
        print("4. Verificando configuraciones insertadas...")
        cursor.execute("SELECT clave, valor, tipo_dato FROM configuracion_sistema ORDER BY clave;")
        configs = cursor.fetchall()
        
        if configs:
            print(f"   Total de configuraciones: {len(configs)}")
            for clave, valor, tipo_dato in configs:
                print(f"   - {clave}: {valor} ({tipo_dato})")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("MIGRACIÓN COMPLETADA")
        print("="*60)
        print()
        print("CAMBIOS REALIZADOS:")
        print("- ✓ Tabla configuracion_sistema creada")
        print("- ✓ Configuraciones por defecto insertadas")
        print("- ✓ Vigencia de autorizaciones: 1 día (24 horas)")
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Reiniciar el servidor backend")
        print("2. El admin puede cambiar la configuración desde el panel")
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
