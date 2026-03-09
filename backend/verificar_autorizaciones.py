"""
Verificar autorizaciones pendientes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import AutorizacionIngreso
from datetime import datetime

app = create_app()

with app.app_context():
    num_id = '14652319'
    
    print("=" * 80)
    print(f"BUSCANDO AUTORIZACIONES PARA: {num_id}")
    print("=" * 80)
    
    # Buscar todas las autorizaciones
    todas = AutorizacionIngreso.query.filter_by(num_identificacion=num_id).all()
    print(f"\n📋 Total autorizaciones encontradas: {len(todas)}")
    
    for auth in todas:
        print(f"\n{'='*80}")
        print(f"ID: {auth.id}")
        print(f"Visitante: {auth.primer_nombre} {auth.primer_apellido}")
        print(f"Estado: {auth.estado}")
        print(f"Fecha Creación: {auth.fecha_creacion}")
        print(f"Fecha Vencimiento: {auth.fecha_vencimiento}")
        print(f"Vencida: {'SÍ' if auth.fecha_vencimiento < datetime.now().date() else 'NO'}")
        print(f"Sede ID: {auth.sede_id}")
        print(f"Empresa: {auth.empresa}")
        print(f"Dependencia: {auth.prefijo_dependencia} - {auth.descripcion_dependencia}")
        print(f"Autoriza: {auth.funcionario_autoriza}")
    
    # Buscar pendientes y no vencidas
    pendientes = AutorizacionIngreso.query.filter_by(
        num_identificacion=num_id,
        estado='PENDIENTE'
    ).filter(
        AutorizacionIngreso.fecha_vencimiento > datetime.now().date()
    ).all()
    
    print(f"\n{'='*80}")
    print(f"✅ AUTORIZACIONES PENDIENTES Y NO VENCIDAS: {len(pendientes)}")
    print("=" * 80)
    
    if len(pendientes) == 0:
        print("\n⚠️ NO HAY AUTORIZACIONES PENDIENTES Y VIGENTES")
        print("Razones posibles:")
        print("  - Estado diferente a 'PENDIENTE'")
        print("  - Fecha de vencimiento ya pasó")
        print("  - No existe autorización para este visitante")
