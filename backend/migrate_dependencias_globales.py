"""
Migración: Eliminar tabla sede_dependencia
Las dependencias ahora son globales para todas las sedes.
"""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print('\n=== MIGRACION: ELIMINAR RELACION SEDE-DEPENDENCIA ===\n')
    
    try:
        # Dropar la tabla sede_dependencia
        print('📋 Eliminando tabla sede_dependencia...')
        db.session.execute(db.text('DROP TABLE IF EXISTS sede_dependencia CASCADE'))
        db.session.commit()
        print('✅ Tabla sede_dependencia eliminada correctamente')
        
        print('\n✅ MIGRACION COMPLETADA')
        print('ℹ️  Las dependencias ahora son globales para todas las sedes')
        print('ℹ️  Cualquier sede puede usar cualquier dependencia activa')
        
    except Exception as e:
        print(f'\n❌ ERROR en la migración: {str(e)}')
        db.session.rollback()
        raise
