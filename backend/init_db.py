"""
========================================
SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS
Crea la base de datos y las tablas necesarias
========================================
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import Usuario, Sede, Dependencia, Visitante, LogVisitante, LogEvento
from datetime import datetime


def init_database():
    """Inicializa la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Eliminando tablas existentes...")
        db.drop_all()
        
        print("🏗️  Creando tablas...")
        db.create_all()
        
        print("✅ Base de datos inicializada correctamente")
        print("\n📊 Tablas creadas:")
        print("  - usuarios")
        print("  - sedes")
        print("  - dependencias")
        print("  - sede_dependencia")
        print("  - visitantes")
        print("  - log_visitantes")
        print("  - log_eventos")


def seed_data():
    """Inserta datos iniciales de prueba"""
    app = create_app()
    
    with app.app_context():
        print("\n🌱 Insertando datos de prueba...")
        
        # Crear sede principal
        sede_principal = Sede(
            codigo_sede='SEDE001',
            descripcion_sede='SEDE PRINCIPAL CAÑAVERAL',
            direccion_sede='Calle 123 # 45-67, Cali, Valle del Cauca',
            estado='ACTIVO'
        )
        db.session.add(sede_principal)
        db.session.flush()
        
        # Crear usuario master
        usuario_master = Usuario(
            tipo_identificacion='CC',
            num_identificacion='1234567890',
            primer_nombre='ADMINISTRADOR',
            segundo_nombre='',
            primer_apellido='SISTEMA',
            segundo_apellido='',
            num_telefono='3001234567',
            dir_correo='admin@supertiendascañaveral.com',
            sede_id=sede_principal.id,
            rol='usuario_master',
            estado='ACTIVO',
            usuario='admin'
        )
        usuario_master.set_password('Admin@2025')
        db.session.add(usuario_master)
        
        # Crear usuario operador
        usuario_operador = Usuario(
            tipo_identificacion='CC',
            num_identificacion='9876543210',
            primer_nombre='OPERADOR',
            segundo_nombre='DE',
            primer_apellido='PRUEBA',
            segundo_apellido='',
            num_telefono='3009876543',
            dir_correo='operador@supertiendascañaveral.com',
            sede_id=sede_principal.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='operador'
        )
        usuario_operador.set_password('Oper@2025')
        db.session.add(usuario_operador)
        
        # Crear dependencias
        dependencias_data = [
            {'prefijo': 'ADM', 'descripcion': 'ADMINISTRACIÓN'},
            {'prefijo': 'RRHH', 'descripcion': 'RECURSOS HUMANOS'},
            {'prefijo': 'CONT', 'descripcion': 'CONTABILIDAD'},
            {'prefijo': 'SIS', 'descripcion': 'SISTEMAS'},
            {'prefijo': 'LOG', 'descripcion': 'LOGÍSTICA'},
            {'prefijo': 'VEN', 'descripcion': 'VENTAS'},
            {'prefijo': 'MKT', 'descripcion': 'MARKETING'},
            {'prefijo': 'MAN', 'descripcion': 'MANTENIMIENTO'}
        ]
        
        for dep_data in dependencias_data:
            dependencia = Dependencia(
                prefijo_dependencia=dep_data['prefijo'],
                descripcion_dependencia=dep_data['descripcion'],
                estado='ACTIVO'
            )
            dependencia.sedes.append(sede_principal)
            db.session.add(dependencia)
        
        # Registrar evento de inicialización
        LogEvento.registrar_evento(
            tipo_evento='SISTEMA_INICIALIZADO',
            descripcion='Base de datos inicializada con datos de prueba',
            nivel='INFO'
        )
        
        db.session.commit()
        
        print("✅ Datos de prueba insertados correctamente")
        print("\n👤 Usuarios creados:")
        print(f"  Master - Usuario: admin | Contraseña: Admin@2025")
        print(f"  Operador - Usuario: operador | Contraseña: Oper@2025")
        print("\n🏢 Sede creada:")
        print(f"  {sede_principal.codigo_sede} - {sede_principal.descripcion_sede}")
        print(f"\n🏛️  {len(dependencias_data)} dependencias creadas")


if __name__ == '__main__':
    print("="*60)
    print("INICIALIZACIÓN DE BASE DE DATOS")
    print("Sistema de Control de Visitantes")
    print("Supertiendas Cañaveral SAS")
    print("="*60)
    
    try:
        init_database()
        seed_data()
        print("\n" + "="*60)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
