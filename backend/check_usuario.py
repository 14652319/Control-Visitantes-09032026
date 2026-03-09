"""Script para verificar usuario funcionario"""
from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    u = Usuario.query.filter_by(usuario='14652319').first()
    if u:
        print(f"\nUsuario: {u.usuario}")
        print(f"ID: {u.id}")
        print(f"Rol: {u.rol}")
        print(f"Sede ID: {u.sede_id}")
        print(f"Nombre: {u.primer_nombre} {u.primer_apellido}")
    else:
        print("\n❌ Usuario no encontrado")
