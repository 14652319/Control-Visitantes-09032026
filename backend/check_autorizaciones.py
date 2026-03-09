"""Script para verificar autorizaciones en la base de datos"""
from app import create_app
from app.extensions import db
from app.models.autorizacion_ingreso import AutorizacionIngreso
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("VERIFICACIÓN DE AUTORIZACIONES EN BASE DE DATOS")
    print("="*60)
    
    # Contar total
    total = AutorizacionIngreso.query.count()
    print(f"\n📊 Total autorizaciones en DB: {total}")
    
    if total > 0:
        print("\n📋 Listado de autorizaciones:\n")
        auths = AutorizacionIngreso.query.order_by(AutorizacionIngreso.fecha_creacion.desc()).all()
        
        for a in auths:
            usuario = Usuario.query.get(a.usuario_id)
            print(f"  • ID: {a.id}")
            print(f"    Visitante: {a.num_identificacion} - {a.primer_nombre} {a.primer_apellido}")
            print(f"    Empresa: {a.empresa}")
            print(f"    Usuario creador: {usuario.usuario if usuario else 'N/A'} (ID: {a.usuario_id})")
            print(f"    Estado: {a.estado}")
            print(f"    Fecha vencimiento: {a.fecha_vencimiento}")
            print(f"    Fecha creación: {a.fecha_creacion}")
            print()
    else:
        print("\n⚠️  No hay autorizaciones en la base de datos")
    
    print("="*60 + "\n")
