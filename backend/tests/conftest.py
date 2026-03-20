"""
========================================
TESTS DE CONFIGURACIÓN (PYTEST)
Sistema de Control de Visitantes
========================================
"""

import pytest
import sys
import os
from datetime import datetime

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app
from app.extensions import db
from app.models import Usuario, Sede, Dependencia, Visitante, AutorizacionIngreso, LogVisitante, LogEvento


@pytest.fixture(scope='session')
def app():
    """Crea una instancia de la aplicación para tests"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Base de datos en memoria
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de prueba para hacer requests"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos limpia para cada test"""
    with app.app_context():
        # Limpiar todas las tablas (orden por dependencias FK)
        db.session.query(LogEvento).delete()
        db.session.query(LogVisitante).delete()
        db.session.query(AutorizacionIngreso).delete()
        db.session.query(Visitante).delete()
        db.session.query(Usuario).delete()
        db.session.query(Dependencia).delete()
        db.session.query(Sede).delete()
        db.session.commit()
        
        yield db
        
        # Limpiar después del test
        db.session.rollback()


@pytest.fixture
def sede_test(db_session):
    """Crea una sede de prueba"""
    sede = Sede(
        codigo_sede='TEST001',
        descripcion_sede='SEDE DE PRUEBA',
        direccion_sede='Calle Test 123',
        estado='ACTIVO'
    )
    db_session.session.add(sede)
    db_session.session.commit()
    return sede


@pytest.fixture
def usuario_master(db_session, sede_test):
    """Crea un usuario master de prueba"""
    usuario = Usuario(
        tipo_identificacion='CC',
        num_identificacion='1234567890',
        primer_nombre='ADMIN',
        segundo_nombre='',
        primer_apellido='SISTEMA',
        segundo_apellido='',
        num_telefono='3001234567',
        dir_correo='admin@test.com',
        sede_id=sede_test.id,
        rol='usuario_master',
        estado='ACTIVO',
        usuario='admin_test'
    )
    usuario.set_password('Test@123')
    db_session.session.add(usuario)
    db_session.session.commit()
    return usuario


@pytest.fixture
def usuario_operador(db_session, sede_test):
    """Crea un usuario operador de prueba"""
    usuario = Usuario(
        tipo_identificacion='CC',
        num_identificacion='9876543210',
        primer_nombre='OPERADOR',
        segundo_nombre='',
        primer_apellido='PRUEBA',
        segundo_apellido='',
        num_telefono='3009876543',
        dir_correo='operador@test.com',
        sede_id=sede_test.id,
        rol='usuario_operador',
        estado='ACTIVO',
        usuario='operador_test'
    )
    usuario.set_password('Test@123')
    db_session.session.add(usuario)
    db_session.session.commit()
    return usuario


@pytest.fixture
def usuario_funcionario(db_session, sede_test):
    """Crea un usuario funcionario de prueba"""
    usuario = Usuario(
        tipo_identificacion='CC',
        num_identificacion='1122334455',
        primer_nombre='FUNCIONARIO',
        segundo_nombre='',
        primer_apellido='PRUEBA',
        segundo_apellido='',
        num_telefono='3001112233',
        dir_correo='funcionario@test.com',
        sede_id=sede_test.id,
        rol='usuario_funcionario',
        estado='ACTIVO',
        usuario='funcionario_test'
    )
    usuario.set_password('Test@123')
    db_session.session.add(usuario)
    db_session.session.commit()
    return usuario


@pytest.fixture
def dependencia_test(db_session, sede_test):
    """Crea una dependencia de prueba"""
    dependencia = Dependencia(
        prefijo_dependencia='TEST',
        descripcion_dependencia='DEPENDENCIA DE PRUEBA'
    )
    db_session.session.add(dependencia)
    db_session.session.commit()
    return dependencia


@pytest.fixture
def visitante_test(db_session):
    """Crea un visitante de prueba"""
    visitante = Visitante(
        tipo_identificacion='CC',
        num_identificacion='1111222233',
        primer_nombre='JUAN',
        segundo_nombre='',
        primer_apellido='PEREZ',
        segundo_apellido='GOMEZ',
        num_telefono='3001234567',
        dir_correo='juan.perez@test.com',
        empresa='EMPRESA TEST SAS',
        nit_empresa='900123456',
        estado='ACTIVO'
    )
    db_session.session.add(visitante)
    db_session.session.commit()
    return visitante


@pytest.fixture
def autorizacion_test(db_session, usuario_funcionario, sede_test):
    """Crea una autorización de prueba"""
    from datetime import date, timedelta
    
    autorizacion = AutorizacionIngreso(
        tipo_identificacion='CC',
        num_identificacion='9999888877',
        primer_nombre='VISITANTE',
        segundo_nombre='',
        primer_apellido='AUTORIZADO',
        segundo_apellido='',
        num_telefono='3009998888',
        dir_correo='visitante@test.com',
        empresa='EMPRESA XYZ',
        nit_empresa='900999888',
        prefijo_dependencia='ADM',
        descripcion_dependencia='ADMINISTRACION',
        funcionario_autoriza='JUAN PEREZ',
        estado='PENDIENTE',
        fecha_vencimiento=date.today() + timedelta(days=1),
        usuario_id=usuario_funcionario.id,
        sede_id=sede_test.id
    )
    db_session.session.add(autorizacion)
    db_session.session.commit()
    return autorizacion
