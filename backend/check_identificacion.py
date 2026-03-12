"""Script para verificar si existe un usuario con identificación específica"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    # Buscar usuario con identificación 14652319
    identificacion = '14652319'
    usuario = Usuario.query.filter_by(num_identificacion=identificacion).first()
    
    if usuario:
        print(f"\n✅ USUARIO ENCONTRADO:")
        print(f"   ID: {usuario.id}")
        print(f"   Usuario (login): {usuario.usuario}")
        print(f"   Tipo ID: {usuario.tipo_identificacion}")
        print(f"   Número ID: {usuario.num_identificacion}")
        print(f"   Nombre: {usuario.primer_nombre} {usuario.primer_apellido}")
        print(f"   Estado: {usuario.estado}")
        print(f"   Rol: {usuario.rol}")
        print(f"   Correo: {usuario.dir_correo}")
    else:
        print(f"\n❌ NO se encontró usuario con identificación: {identificacion}")
    
    # Listar todos los usuarios
    print(f"\n\n📋 TODOS LOS USUARIOS EN LA BASE DE DATOS:")
    print("-" * 80)
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f"   ID: {u.id:2d} | Usuario: {u.usuario:20s} | Identificación: {u.num_identificacion:15s} | Estado: {u.estado}")
