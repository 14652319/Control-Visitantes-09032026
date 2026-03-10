"""
Script para asignar dependencias a la Sede 3 (PALMIRA CENTRO)
"""
from app import create_app
from app.models import Dependencia, Sede
from app.extensions import db
from datetime import datetime

app = create_app()

with app.app_context():
    print('\n=== ASIGNANDO DEPENDENCIAS A SEDE PALMIRA ===\n')
    
    # Obtener la Sede 3 (PALMIRA)
    sede_palmira = Sede.query.filter_by(codigo_sede='001').first()
    
    if not sede_palmira:
        print('❌ No se encontró la Sede PALMIRA (código 001)')
        exit(1)
    
    print(f'✅ Sede encontrada: {sede_palmira.codigo_sede} - {sede_palmira.descripcion_sede}')
    
    # Obtener todas las dependencias activas
    dependencias = Dependencia.query.filter_by(estado='ACTIVO').all()
    
    print(f'\n📂 Dependencias activas en el sistema: {len(dependencias)}\n')
    
    # Asignar cada dependencia a la sede
    asignadas = 0
    for dep in dependencias:
        # Verificar si ya está asignada
        if dep not in sede_palmira.dependencias:
            sede_palmira.dependencias.append(dep)
            asignadas += 1
            print(f'  ✅ Asignada: {dep.prefijo_dependencia} - {dep.descripcion_dependencia}')
        else:
            print(f'  ⚠️  Ya asignada: {dep.prefijo_dependencia} - {dep.descripcion_dependencia}')
    
    # Guardar cambios
    if asignadas > 0:
        db.session.commit()
        print(f'\n✅ ¡Éxito! Se asignaron {asignadas} dependencias a la Sede PALMIRA')
    else:
        print('\n⚠️  No había dependencias nuevas para asignar')
    
    # Verificar
    print(f'\n=== VERIFICACIÓN ===')
    print(f'Total dependencias en Sede PALMIRA: {sede_palmira.dependencias.count()}')
    print('\nDependencias asignadas:')
    for dep in sede_palmira.dependencias.all():
        print(f'  - {dep.prefijo_dependencia}: {dep.descripcion_dependencia}')
