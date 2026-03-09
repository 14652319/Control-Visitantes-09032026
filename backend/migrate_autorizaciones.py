"""
========================================
SCRIPT DE MIGRACIÓN - SISTEMA DE AUTORIZACIONES
Agrega la tabla autorizaciones_ingreso y campos relacionados
========================================
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text
from datetime import datetime


def migrate_database():
    """Ejecuta la migración de base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración del sistema de autorizaciones...")
        print("=" * 60)
        
        try:
            # 1. Crear tabla autorizaciones_ingreso
            print("\n📋 Paso 1: Creando tabla autorizaciones_ingreso...")
            
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS autorizaciones_ingreso (
                    id SERIAL PRIMARY KEY,
                    tipo_identificacion VARCHAR(50) NOT NULL,
                    num_identificacion VARCHAR(50) NOT NULL,
                    primer_nombre VARCHAR(50) NOT NULL,
                    segundo_nombre VARCHAR(50),
                    primer_apellido VARCHAR(50) NOT NULL,
                    segundo_apellido VARCHAR(50),
                    empresa VARCHAR(200) NOT NULL,
                    nit_empresa VARCHAR(50),
                    prefijo_dependencia VARCHAR(50) NOT NULL,
                    descripcion_dependencia VARCHAR(200) NOT NULL,
                    funcionario_autoriza VARCHAR(200) NOT NULL,
                    observaciones TEXT,
                    estado VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE',
                    fecha_vencimiento TIMESTAMP NOT NULL,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                    sede_id INTEGER NOT NULL REFERENCES sedes(id),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_utilizacion TIMESTAMP,
                    utilizada_en_log_id INTEGER
                )
            """)
            
            db.session.execute(create_table_query)
            db.session.commit()
            print("   ✅ Tabla autorizaciones_ingreso creada exitosamente")
            
            # 2. Agregar índices a la tabla autorizaciones_ingreso
            print("\n📋 Paso 2: Creando índices en autorizaciones_ingreso...")
            
            indices_queries = [
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_estado ON autorizaciones_ingreso(estado)",
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_num_identificacion ON autorizaciones_ingreso(num_identificacion)",
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_fecha_vencimiento ON autorizaciones_ingreso(fecha_vencimiento)",
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_sede_id ON autorizaciones_ingreso(sede_id)",
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_usuario_id ON autorizaciones_ingreso(usuario_id)"
            ]
            
            for idx_query in indices_queries:
                db.session.execute(text(idx_query))
            
            db.session.commit()
            print("   ✅ Índices creados exitosamente")
            
            # 3. Agregar columna funcionario_autoriza a log_visitantes
            print("\n📋 Paso 3: Agregando columna funcionario_autoriza a log_visitantes...")
            
            # Verificar si la columna ya existe
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='log_visitantes' AND column_name='funcionario_autoriza'
            """)
            
            result = db.session.execute(check_column_query).fetchone()
            
            if result is None:
                add_column_query = text("""
                    ALTER TABLE log_visitantes 
                    ADD COLUMN funcionario_autoriza VARCHAR(200) NOT NULL DEFAULT ''
                """)
                db.session.execute(add_column_query)
                db.session.commit()
                print("   ✅ Columna funcionario_autoriza agregada exitosamente")
            else:
                print("   ⚠️  Columna funcionario_autoriza ya existe, omitiendo...")
            
            # 4. Agregar columna autorizacion_previa_id a log_visitantes
            print("\n📋 Paso 4: Agregando columna autorizacion_previa_id a log_visitantes...")
            
            # Verificar si la columna ya existe
            check_column_query2 = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='log_visitantes' AND column_name='autorizacion_previa_id'
            """)
            
            result2 = db.session.execute(check_column_query2).fetchone()
            
            if result2 is None:
                add_column_query2 = text("""
                    ALTER TABLE log_visitantes 
                    ADD COLUMN autorizacion_previa_id INTEGER REFERENCES autorizaciones_ingreso(id)
                """)
                db.session.execute(add_column_query2)
                db.session.commit()
                print("   ✅ Columna autorizacion_previa_id agregada exitosamente")
            else:
                print("   ⚠️  Columna autorizacion_previa_id ya existe, omitiendo...")
            
            # 5. Agregar FK de utilizada_en_log_id (después de que log_visitantes tenga la columna)
            print("\n📋 Paso 5: Agregando FK utilizada_en_log_id a autorizaciones_ingreso...")
            
            # Verificar si el constraint ya existe
            check_fk_query = text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name='autorizaciones_ingreso' 
                AND constraint_name='autorizaciones_ingreso_utilizada_en_log_id_fkey'
            """)
            
            fk_result = db.session.execute(check_fk_query).fetchone()
            
            if fk_result is None:
                add_fk_query = text("""
                    ALTER TABLE autorizaciones_ingreso
                    ADD CONSTRAINT autorizaciones_ingreso_utilizada_en_log_id_fkey
                    FOREIGN KEY (utilizada_en_log_id) REFERENCES log_visitantes(id)
                """)
                db.session.execute(add_fk_query)
                db.session.commit()
                print("   ✅ FK utilizada_en_log_id agregada exitosamente")
            else:
                print("   ⚠️  FK ya existe, omitiendo...")
            
            # 6. Crear índice en autorizacion_previa_id de log_visitantes
            print("\n📋 Paso 6: Creando índice en log_visitantes.autorizacion_previa_id...")
            
            create_idx_log = text("""
                CREATE INDEX IF NOT EXISTS idx_log_visitantes_autorizacion_previa 
                ON log_visitantes(autorizacion_previa_id)
            """)
            db.session.execute(create_idx_log)
            db.session.commit()
            print("   ✅ Índice creado exitosamente")
            
            print("\n" + "=" * 60)
            print("✅ Migración completada exitosamente!")
            print("\n📊 Cambios aplicados:")
            print("  ✓ Tabla autorizaciones_ingreso creada")
            print("  ✓ 5 índices en autorizaciones_ingreso creados")
            print("  ✓ Campo funcionario_autoriza agregado a log_visitantes")
            print("  ✓ Campo autorizacion_previa_id agregado a log_visitantes")
            print("  ✓ Foreign keys configuradas correctamente")
            print("  ✓ Índices de rendimiento creados")
            print("\n🎉 El sistema de autorizaciones está listo para usar!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la migración: {str(e)}")
            print("La migración se ha revertido.")
            raise


def verify_migration():
    """Verifica que la migración se haya ejecutado correctamente"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verificando migración...")
        
        try:
            # Verificar tabla autorizaciones_ingreso
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'autorizaciones_ingreso'
                )
            """)
            table_exists = db.session.execute(check_table).scalar()
            
            if table_exists:
                print("  ✅ Tabla autorizaciones_ingreso existe")
                
                # Contar columnas
                count_columns = text("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = 'autorizaciones_ingreso'
                """)
                column_count = db.session.execute(count_columns).scalar()
                print(f"  ✅ Tabla tiene {column_count} columnas")
            else:
                print("  ❌ Tabla autorizaciones_ingreso NO existe")
            
            # Verificar columnas en log_visitantes
            check_columns = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'log_visitantes' 
                AND column_name IN ('funcionario_autoriza', 'autorizacion_previa_id')
                ORDER BY column_name
            """)
            columns = db.session.execute(check_columns).fetchall()
            
            if len(columns) == 2:
                print(f"  ✅ Columnas nuevas en log_visitantes: {', '.join([c[0] for c in columns])}")
            else:
                print(f"  ⚠️  Solo {len(columns)} de 2 columnas encontradas en log_visitantes")
            
            print("\n✅ Verificación completada")
            
        except Exception as e:
            print(f"\n❌ Error durante la verificación: {str(e)}")


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║   MIGRACIÓN: SISTEMA DE AUTORIZACIONES DE INGRESO         ║
║   Versión: 1.0                                             ║
║   Fecha: """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """                                    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        migrate_database()
        verify_migration()
    except Exception as e:
        print("\n💥 La migración falló. Por favor revise los errores anteriores.")
        sys.exit(1)
