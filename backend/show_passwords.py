"""
Mostrar contraseñas de los usuarios
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import Usuario

app = create_app()

with app.app_context():
    usuarios = Usuario.query.all()
    
    print("=" * 60)
    print("USUARIOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    for user in usuarios:
        print(f"\nID: {user.id}")
        print(f"Usuario: {user.usuario}")
        print(f"Nombre: {user.primer_nombre} {user.primer_apellido}")
        print(f"Rol: {user.rol}")
        print(f"Estado: {user.estado}")
        print(f"Intentos fallidos: {user.intentos_fallidos}")
        
        # Verificar contraseñas
        passwords_to_test = ["Admin@2025", "Oper@2025", "Operador@2025"]
        
        for pwd in passwords_to_test:
            if user.check_password(pwd):
                print(f"✅ Contraseña correcta: {pwd}")
                break
        else:
            print("⚠️  Contraseña no coincide con los valores de prueba")
    
    print("\n" + "=" * 60)
