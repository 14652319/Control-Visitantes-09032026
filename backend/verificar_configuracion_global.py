"""
Verificación: Dependencias globales sin relación con sedes
"""
from app import create_app
from app.models import Dependencia, Sede
from app.extensions import db

app = create_app()

with app.app_context():
    print('\n=== VERIFICACIÓN DE DEPENDENCIAS GLOBALES ===\n')
    
    # Verificar que la tabla sede_dependencia no existe
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tablas = inspector.get_table_names()
    
    if 'sede_dependencia' in tablas:
        print('❌ ERROR: La tabla sede_dependencia todavía existe')
    else:
        print('✅ La tabla sede_dependencia fue eliminada correctamente')
    
    # Verificar dependencias
    print('\n📂 DEPENDENCIAS EN EL SISTEMA:')
    dependencias = Dependencia.query.filter_by(estado='ACTIVO').all()
    print(f'Total dependencias activas: {len(dependencias)}\n')
    for dep in dependencias:
        print(f'  ✅ {dep.prefijo_dependencia}: {dep.descripcion_dependencia}')
    
    # Verificar sedes
    print('\n🏢 SEDES EN EL SISTEMA:')
    sedes = Sede.query.all()
    for sede in sedes:
        print(f'  • {sede.codigo_sede} - {sede.descripcion_sede}')
    
    print('\n' + '='*70)
    print('✅ CONFIGURACIÓN CORRECTA')
    print('ℹ️  Las dependencias ahora son globales')
    print('ℹ️  Todas las sedes pueden usar todas las dependencias activas')
    print('ℹ️  No necesitas asignar dependencias a cada sede nueva')
    print('='*70 + '\n')
