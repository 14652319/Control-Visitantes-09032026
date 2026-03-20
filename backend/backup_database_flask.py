"""
Backup de base de datos usando la conexión de Flask
Usa SQLAlchemy que ya funciona en la aplicación
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el path del backend al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def backup_database_flask():
    """Hacer backup usando la configuración de Flask"""
    from app import create_app
    from app.extensions import db
    
    # Crear app con contexto
    app = create_app()
    
    backup_dir = Path(r"D:\0.A. Proyectos\0.0. BackUp\BackUp 1.1. Control de Acceso Visitantes\database_backup")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f"control_visitantes_backup_{timestamp}.sql"
    
    with app.app_context():
        print("=" * 70)
        print("BACKUP DE BASE DE DATOS - Sistema Control de Visitantes")
        print("=" * 70)
        print()
        print(f"🔄 Iniciando backup usando conexión de Flask...")
        print(f"📦 Database: {db.engine.url.database}")
        print()
        
        try:
            # Obtener el engine de SQLAlchemy
            engine = db.engine
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                # Header
                f.write("-- PostgreSQL Database Backup\n")
                f.write(f"-- Database: {engine.url.database}\n")
                f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-- Generated via Flask SQLAlchemy\n\n")
                f.write("SET statement_timeout = 0;\n")
                f.write("SET lock_timeout = 0;\n")
                f.write("SET client_encoding = 'UTF8';\n")
                f.write("SET standard_conforming_strings = on;\n\n")
                
                # Obtener lista de tablas
                inspector = db.inspect(engine)
                tables = inspector.get_table_names()
                
                print(f"📋 Tablas encontradas: {len(tables)}")
                print()
                
                for table_name in tables:
                    print(f"   ├─ Exportando: {table_name}")
                    
                    # Obtener columnas
                    columns = inspector.get_columns(table_name)
                    column_names = [col['name'] for col in columns]
                    
                    # Obtener constraints
                    pk_constraint = inspector.get_pk_constraint(table_name)
                    fk_constraints = inspector.get_foreign_keys(table_name)
                    unique_constraints = inspector.get_unique_constraints(table_name)
                    indexes = inspector.get_indexes(table_name)
                    
                    # Escribir DROP TABLE
                    f.write(f"\n-- ============================================\n")
                    f.write(f"-- Table: {table_name}\n")
                    f.write(f"-- ============================================\n")
                    f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n\n")
                    
                    # Escribir CREATE TABLE
                    f.write(f"CREATE TABLE {table_name} (\n")
                    
                    # Columnas
                    col_defs = []
                    for col in columns:
                        col_def = f"    {col['name']} {col['type']}"
                        if not col['nullable']:
                            col_def += " NOT NULL"
                        if col.get('default'):
                            col_def += f" DEFAULT {col['default']}"
                        col_defs.append(col_def)
                    
                    # Primary key inline
                    if pk_constraint and pk_constraint['constrained_columns']:
                        pk_cols = ', '.join(pk_constraint['constrained_columns'])
                        col_defs.append(f"    PRIMARY KEY ({pk_cols})")
                    
                    # Foreign keys inline
                    for fk in fk_constraints:
                        fk_cols = ', '.join(fk['constrained_columns'])
                        ref_table = fk['referred_table']
                        ref_cols = ', '.join(fk['referred_columns'])
                        fk_name = fk.get('name', f"fk_{table_name}_{ref_table}")
                        col_defs.append(f"    CONSTRAINT {fk_name} FOREIGN KEY ({fk_cols}) REFERENCES {ref_table}({ref_cols})")
                    
                    # Unique constraints inline
                    for uc in unique_constraints:
                        uc_cols = ', '.join(uc['column_names'])
                        uc_name = uc.get('name', f"unique_{table_name}_{uc_cols.replace(', ', '_')}")
                        col_defs.append(f"    CONSTRAINT {uc_name} UNIQUE ({uc_cols})")
                    
                    f.write(',\n'.join(col_defs))
                    f.write("\n);\n\n")
                    
                    # Indexes (solo los que no son PK o UNIQUE)
                    for idx in indexes:
                        if not idx['unique']:  # Los unique ya los tenemos
                            idx_name = idx['name']
                            idx_cols = ', '.join(idx['column_names'])
                            f.write(f"CREATE INDEX {idx_name} ON {table_name} ({idx_cols});\n")
                    
                    if indexes:
                        f.write("\n")
                    
                    # Datos
                    with engine.connect() as conn:
                        result = conn.execute(db.text(f'SELECT * FROM "{table_name}"'))
                        rows = result.fetchall()
                        
                        if rows:
                            row_count = len(rows)
                            print(f"   │  └─ {row_count} registros")
                            
                            f.write(f"-- Data for {table_name} ({row_count} rows)\n")
                            
                            for row in rows:
                                # Construir INSERT
                                values = []
                                for val in row:
                                    if val is None:
                                        values.append('NULL')
                                    elif isinstance(val, str):
                                        # Escapar comillas simples
                                        escaped = val.replace("'", "''").replace("\\", "\\\\")
                                        values.append(f"'{escaped}'")
                                    elif isinstance(val, bool):
                                        values.append('true' if val else 'false')
                                    elif isinstance(val, (int, float)):
                                        values.append(str(val))
                                    elif isinstance(val, datetime):
                                        values.append(f"'{val.isoformat()}'")
                                    else:
                                        # Para otros tipos (date, time, etc.)
                                        values.append(f"'{str(val)}'")
                                
                                col_list = ', '.join(column_names)
                                val_list = ', '.join(values)
                                f.write(f"INSERT INTO {table_name} ({col_list}) VALUES ({val_list});\n")
                            
                            f.write("\n")
                        else:
                            print(f"   │  └─ (vacía)")
                
                # Actualizar sequences
                f.write("\n-- ============================================\n")
                f.write("-- Actualizar sequences\n")
                f.write("-- ============================================\n")
                for table_name in tables:
                    pk = inspector.get_pk_constraint(table_name)
                    if pk and pk['constrained_columns']:
                        pk_col = pk['constrained_columns'][0]
                        f.write(f"SELECT setval(pg_get_serial_sequence('{table_name}', '{pk_col}'), COALESCE((SELECT MAX({pk_col}) FROM {table_name}), 1), false);\n")
                
                f.write("\n")
            
            if backup_file.exists() and backup_file.stat().st_size > 0:
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                print()
                print("=" * 70)
                print(f"✅ BACKUP COMPLETADO EXITOSAMENTE")
                print("=" * 70)
                print(f"📁 Archivo: {backup_file.name}")
                print(f"📂 Ubicación: {backup_file.parent}")
                print(f"📊 Tamaño: {size_mb:.2f} MB")
                print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                return True
            else:
                print(f"\n❌ El archivo de backup está vacío")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = backup_database_flask()
    exit(0 if success else 1)
