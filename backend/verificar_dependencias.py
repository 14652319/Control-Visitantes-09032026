"""Verificar sedes, usuarios y dependencias"""
from app import create_app
from app.models import Dependencia, Usuario, Sede
from app.extensions import db

app = create_app()
with app.app_context():
    print('\n=== SEDES ===')
    for s in Sede.query.all():
        print(f'ID: {s.id}, Código: {s.codigo_sede}, Nombre: {s.descripcion_sede}')
    
    print('\n=== USUARIOS OPERADORES ===')
    for u in Usuario.query.filter_by(rol='usuario_operador').all():
        sede_nombre = u.sede.descripcion_sede if u.sede else "Sin sede"
        print(f'{u.usuario} - Sede ID: {u.sede_id} ({sede_nombre})')
    
    print('\n=== DEPENDENCIAS POR SEDE ===')
    for s in Sede.query.all():
        deps = Dependencia.query.filter_by(sede_id=s.id).all()
        print(f'\nSede {s.id} ({s.codigo_sede} - {s.descripcion_sede}):')
        if deps:
            for d in deps:
                print(f'  - {d.prefijo_dependencia}: {d.descripcion_dependencia}')
        else:
            print('  ⚠️ Sin dependencias')
