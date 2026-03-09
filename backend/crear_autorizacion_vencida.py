"""Script para crear una autorización vencida de prueba"""
from app import create_app
from app.extensions import db
from app.models.autorizacion_ingreso import AutorizacionIngreso
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    try:
        print("\n" + "="*60)
        print("CREAR AUTORIZACIÓN VENCIDA PARA PRUEBAS")
        print("="*60)
        
        # Crear autorización con fecha de vencimiento ayer
        ayer = (datetime.now() - timedelta(days=1)).date()
        
        auth_vencida = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='98765432',
            primer_nombre='VISITANTE',
            segundo_nombre='DE',
            primer_apellido='PRUEBA',
            segundo_apellido='VENCIDA',
            empresa='EMPRESA PRUEBA',
            nit_empresa='900123456',
            prefijo_dependencia='TEST',
            descripcion_dependencia='DEPARTAMENTO TEST',
            funcionario_autoriza='FUNCIONARIO TEST',
            observaciones='Autorización de prueba para testing',
            estado='PENDIENTE',
            usuario_id=4,  # Usuario funcionario
            sede_id=2,
            fecha_vencimiento=ayer  # Fecha de ayer - está vencida
        )
        
        db.session.add(auth_vencida)
        db.session.commit()
        
        print(f"\n✅ Autorización vencida creada:")
        print(f"   ID: {auth_vencida.id}")
        print(f"   Visitante: {auth_vencida.primer_nombre} {auth_vencida.primer_apellido}")
        print(f"   Fecha vencimiento: {auth_vencida.fecha_vencimiento}")
        print(f"   Estado: {auth_vencida.estado}")
        print(f"   Hoy: {datetime.now().date()}")
        print(f"   ¿Está vencida?: {auth_vencida.fecha_vencimiento < datetime.now().date()}")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.session.rollback()
