"""
Verificar datos del usuario funcionario
"""
from app.extensions import db
from app.models.usuario import Usuario
from app import create_app

app = create_app()

with app.app_context():
    # Buscar por rol
    funcionarios = Usuario.query.filter_by(rol='usuario_funcionario').all()
    
    if funcionarios:
        print("=" * 50)
        print(f"Usuarios con rol funcionario: {len(funcionarios)}")
        for func in funcionarios:
            print("-" * 50)
            print(f"  Usuario: {func.usuario}")
            print(f"  Rol: [{func.rol}]")
            print(f"  Rol length: {len(func.rol)}")
            print(f"  Rol repr: {repr(func.rol)}")
            print(f"  Sede ID: {func.sede_id}")
            print(f"  Estado: {func.estado}")
        print("=" * 50)
    else:
        print("No se encontraron usuarios con rol usuario_funcionario")
        print("\nBuscando todos los usuarios:")
        todos = Usuario.query.all()
        for u in todos:
            print(f"  - {u.usuario} ({u.rol})")

