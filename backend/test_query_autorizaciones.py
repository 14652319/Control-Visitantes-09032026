"""Script para simular la petición GET /autorizaciones/ para el usuario funcionario"""
from app import create_app
from app.extensions import db
from app.models.autorizacion_ingreso import AutorizacionIngreso
from app.models.usuario import Usuario
from datetime import datetime
from sqlalchemy import or_

app = create_app()

with app.app_context():
    # Simular el usuario actual (funcionario)
    current_user = Usuario.query.filter_by(usuario='14652319').first()
    print(f"\n👤 Usuario actual: {current_user.usuario} (ID: {current_user.id}, Rol: {current_user.rol})")
    
    # Parámetros de filtro (igual que el frontend envia por defecto)
    estado = None  # ''  en el frontend se convierte en None
    incluir_vencidas = False
    
    print(f"\n🔍 Filtros:")
    print(f"   estado: {estado}")
    print(f"   incluir_vencidas: {incluir_vencidas}")
    
    # Query base
    query = AutorizacionIngreso.query
    
    # Filtrar según el rol (usuario_funcionario)
    print(f"\n📝 Aplicando filtro de rol...")
    if current_user.rol == 'usuario_funcionario':
        query = query.filter_by(usuario_id=current_user.id)
        print(f"   → Filtrado por usuario_id={current_user.id}")
    
    # Aplicar filtros adicionales
    if estado:
        query = query.filter_by(estado=estado)
        print(f"   → Filtrado por estado={estado}")
    
    # Filtrar vencidas
    print(f"\n📅 Verificando filtro de vencidas...")
    print(f"   incluir_vencidas={incluir_vencidas}, estado={estado}")
    
    if not incluir_vencidas and estado != 'VENCIDA':
        print(f"   → Aplicando filtro de fecha_vencimiento")
        hoy = datetime.now().date()
        print(f"   → Fecha hoy: {hoy}")
        
        # Antes del filtro
        antes = query.all()
        print(f"   → Autorizaciones antes del filtro de fecha: {len(antes)}")
        for a in antes:
            print(f"      • ID:{a.id} Estado:{a.estado} Venc:{a.fecha_vencimiento} {'>'if a.fecha_vencimiento > hoy else '<='} {hoy}")
        
        query = query.filter(or_(
            AutorizacionIngreso.estado != 'PENDIENTE',
            AutorizacionIngreso.fecha_vencimiento > hoy
        ))
    
    # Ordenar
    autorizaciones = query.order_by(AutorizacionIngreso.fecha_creacion.desc()).all()
    
    print(f"\n✅ RESULTADO FINAL: {len(autorizaciones)} autorizaciones")
    for auth in autorizaciones:
        print(f"   • ID: {auth.id}")
        print(f"     Visitante: {auth.num_identificacion} - {auth.primer_nombre} {auth.primer_apellido}")
        print(f"     Estado: {auth.estado}")
        print(f"     Fecha vencimiento: {auth.fecha_vencimiento}")
        print(f"     Creado por usuario_id: {auth.usuario_id}")
        print()
