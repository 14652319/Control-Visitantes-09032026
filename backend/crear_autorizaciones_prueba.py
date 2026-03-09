"""Script para crear autorizaciones de prueba válidas en Sede 2"""
from app import create_app
from app.models import AutorizacionIngreso, Usuario
from app.extensions import db
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Obtener funcionario
    func = Usuario.query.filter_by(usuario='14652319').first()
    
    # Crear 2 autorizaciones válidas
    empresas = [
        ('LA GALERIA Y CIA SAS', '805019853'),
        ('SUPERTIENDAS CAÑAVERAL SAS', '805028041')
    ]
    
    for i, (empresa, nit) in enumerate(empresas, 1):
        nueva = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='14652319',
            primer_nombre='RICARDO',
            segundo_nombre='',
            primer_apellido='RIASCOS',
            segundo_apellido='BURGOS',
            num_telefono='3163508997',
            dir_correo='ricardoriascos07@gmail.com',
            empresa=empresa,
            nit_empresa=nit,
            prefijo_dependencia='CONT',
            descripcion_dependencia='CONTABILIDAD',
            funcionario_autoriza='MARGERY',
            observaciones='CAPACITACION',
            estado='PENDIENTE',
            fecha_vencimiento=(datetime.now() + timedelta(days=5)).date(),
            usuario_id=func.id if func else 3,
            sede_id=2  # Cañaveral
        )
        db.session.add(nueva)
        db.session.flush()
        print(f'{i}. Autorización {nueva.id} creada: {empresa[:30]} - Vence {nueva.fecha_vencimiento}')
    
    db.session.commit()
    print('\n✅ Autorizaciones creadas en Sede 2 (Cañaveral)')
