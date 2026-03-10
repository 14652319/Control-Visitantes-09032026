from app import create_app
from app.models import Dependencia, Sede

app = create_app()

with app.app_context():
    print('\n=== TODAS LAS DEPENDENCIAS ===')
    todas_deps = Dependencia.query.all()
    for d in todas_deps:
        print(f'{d.id}: {d.prefijo_dependencia} - {d.descripcion_dependencia} (Estado: {d.estado})')
    
    print(f'\n\nTotal dependencias en sistema: {len(todas_deps)}')
    
    print('\n\n=== DEPENDENCIAS POR SEDE ===')
    sedes = Sede.query.all()
    for s in sedes:
        print(f'\n{"="*70}')
        print(f'Sede {s.id}: {s.codigo_sede} - {s.descripcion_sede}')
        print(f'Total dependencias asignadas: {s.dependencias.count()}')
        
        deps_sede = s.dependencias.all()
        if deps_sede:
            for d in deps_sede:
                print(f'  - {d.prefijo_dependencia}: {d.descripcion_dependencia} (Estado: {d.estado})')
        else:
            print('  ⚠️  NO HAY DEPENDENCIAS ASIGNADAS A ESTA SEDE')
    
    print(f'\n\n{"="*70}')
    print('=== RESUMEN ===')
    for s in sedes:
        deps_activas = s.dependencias.filter_by(estado='ACTIVO').count()
        print(f'Sede {s.codigo_sede}: {deps_activas} dependencias ACTIVAS')
