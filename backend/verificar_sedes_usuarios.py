"""
Verificar sedes de usuarios
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import Usuario, Sede

app = create_app()

with app.app_context():
    usuarios = Usuario.query.all()
    
    print("=" * 80)
    print("USUARIOS Y SUS SEDES ASIGNADAS")
    print("=" * 80)
    
    for user in usuarios:
        print(f"\n{'='*80}")
        print(f"ID: {user.id}")
        print(f"Usuario: {user.usuario}")
        print(f"Nombre: {user.primer_nombre} {user.primer_apellido}")
        print(f"Rol: {user.rol}")
        print(f"Sede ID: {user.sede_id}")
        
        if user.sede:
            print(f"Sede: {user.sede.descripcion_sede} ({user.sede.codigo_sede})")
        else:
            print(f"Sede: N/A (Acceso Global)")
        
        print(f"Estado: {user.estado}")
    
    print(f"\n{'='*80}")
    print("\nSEDES DISPONIBLES EN LA BASE DE DATOS:")
    print("=" * 80)
    
    sedes = Sede.query.all()
    for sede in sedes:
        print(f"ID: {sede.id} - Código: {sede.codigo_sede} - Descripción: {sede.descripcion_sede}")
    
    print("\n" + "=" * 80)
