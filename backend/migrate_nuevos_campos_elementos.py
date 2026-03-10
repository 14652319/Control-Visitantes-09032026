"""
Migración: Agregar nuevos campos para elementos que ingresa y número de visitantes
"""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print('\n=== MIGRACIÓN: NUEVOS CAMPOS ELEMENTOS Y VISITANTES ===\n')
    
    try:
        # Agregar nuevos campos a log_visitantes
        print('📋 Agregando campos nuevos a log_visitantes...')
        
        sqls = [
            # Checkbox principal para elementos
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS ingresa_elementos BOOLEAN DEFAULT FALSE",
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS elementos_observacion VARCHAR(500)",
            
            # Sub-checkboxes para tipos de elementos
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS elemento_portatil BOOLEAN DEFAULT FALSE",
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS elemento_celular BOOLEAN DEFAULT FALSE",
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS elemento_herramientas BOOLEAN DEFAULT FALSE",
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS elemento_otros BOOLEAN DEFAULT FALSE",
            
            # Número de visitantes y adicionales
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS numero_visitantes INTEGER DEFAULT 1",
            "ALTER TABLE log_visitantes ADD COLUMN IF NOT EXISTS visitantes_adicionales TEXT"
        ]
        
        for sql in sqls:
            db.session.execute(db.text(sql))
            print(f'  ✅ {sql[:50]}...')
        
        db.session.commit()
        print('\n✅ MIGRACIÓN COMPLETADA')
        print('ℹ️  Se agregaron los siguientes campos:')
        print('   - ingresa_elementos (Boolean)')
        print('   - elementos_observacion (String)')
        print('   - elemento_portatil (Boolean)')
        print('   - elemento_celular (Boolean)')
        print('   - elemento_herramientas (Boolean)')
        print('   - elemento_otros (Boolean)')
        print('   - numero_visitantes (Integer, default 1)')
        print('   - visitantes_adicionales (Text)')
        print('\nℹ️  Los campos antiguos (check1, check2, etc.) se mantienen para compatibilidad')
        
    except Exception as e:
        print(f'\n❌ ERROR en la migración: {str(e)}')
        db.session.rollback()
        raise
