"""
========================================
SCRIPT PARA AGREGAR USUARIO FUNCIONARIO
Crea un usuario con rol usuario_funcionario para pruebas
========================================
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import Usuario, Sede

def crear_usuario_funcionario():
    """Crea un usuario funcionario de prueba"""
    app = create_app()
    
    with app.app_context():
        print("🔑 Creando usuario funcionario de prueba...")
        
        # Obtener la primera sede
        sede = Sede.query.first()
        if not sede:
            print("❌ Error: No hay sedes en la base de datos")
            return
        
        # Verificar si ya existe
        existe = Usuario.query.filter_by(usuario='funcionario').first()
        if existe:
            print("⚠️  El usuario 'funcionario' ya existe")
            print(f"   Rol: {existe.rol}")
            print(f"   Estado: {existe.estado}")
            print(f"   Sede: {existe.sede.descripcion_sede}")
            
            # Preguntar si desea actualizar
            respuesta = input("¿Desea actualizar su contraseña? (s/n): ")
            if respuesta.lower() == 's':
                existe.set_password('Func@2025')
                db.session.commit()
                print("✅ Contraseña actualizada: Func@2025")
            return
        
        # Crear nuevo usuario
        usuario = Usuario(
            usuario='funcionario',
            rol='usuario_funcionario',
            sede_id=sede.id,
            tipo_identificacion='CC',
            num_identificacion='999999999',
            primer_nombre='FUNCIONARIO',
            segundo_nombre='DE',
            primer_apellido='PRUEBA',
            segundo_apellido='TEST',
            num_telefono='3001234567',
            dir_correo='funcionario@test.com',
            estado='ACTIVO'
        )
        usuario.set_password('Func@2025')
        
        db.session.add(usuario)
        db.session.commit()
        
        print("✅ Usuario funcionario creado exitosamente")
        print("\n📋 Datos de acceso:")
        print(f"   Usuario: funcionario")
        print(f"   Contraseña: Func@2025")
        print(f"   Rol: usuario_funcionario")
        print(f"   Sede: {sede.descripcion_sede}")
        print("\n🌐 Puede acceder en: http://localhost:3000")


if __name__ == '__main__':
    crear_usuario_funcionario()
