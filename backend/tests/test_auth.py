"""
========================================
TESTS - AUTENTICACIÓN
Tests para login, logout y seguridad
========================================
"""

import pytest
import json
from flask import session


class TestAuth:
    """Tests para autenticación"""
    
    def test_login_exitoso(self, client, usuario_master, db_session):
        """Test: Login exitoso con credenciales correctas"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'admin_test',
                'password': 'Test@123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'usuario' in data
        assert data['usuario']['usuario'] == 'admin_test'
        assert data['usuario']['rol'] == 'usuario_master'
    
    def test_login_usuario_inexistente(self, client):
        """Test: Login fallido con usuario inexistente"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'usuario_no_existe',
                'password': 'cualquier_password'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'incorrectos' in data['message'].lower()
    
    def test_login_password_incorrecta(self, client, usuario_master):
        """Test: Login fallido con contraseña incorrecta"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'admin_test',
                'password': 'PasswordIncorrecta@123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_usuario_bloqueado(self, client, usuario_operador, db_session):
        """Test: Login denegado para usuario bloqueado"""
        # Bloquear el usuario
        usuario_operador.estado = 'BLOQUEADO'
        db_session.session.commit()
        
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'operador_test',
                'password': 'Test@123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'bloqueado' in data['message'].lower()
    
    def test_login_case_insensitive(self, client, usuario_master):
        """Test: Login es case-insensitive"""
        # Probar con mayúsculas
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'ADMIN_TEST',
                'password': 'Test@123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_login_campos_requeridos(self, client):
        """Test: Login requiere usuario y contraseña"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'admin_test'
                # Sin password
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'requeridos' in data['message'].lower()
    
    def test_incremento_intentos_fallidos(self, client, usuario_operador, db_session):
        """Test: Los intentos fallidos se incrementan correctamente"""
        intentos_iniciales = usuario_operador.intentos_fallidos
        
        # Intentar login con password incorrecta
        client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'operador_test',
                'password': 'PasswordIncorrecta'
            }),
            content_type='application/json'
        )
        
        db_session.session.refresh(usuario_operador)
        assert usuario_operador.intentos_fallidos == intentos_iniciales + 1
    
    def test_bloqueo_automatico_despues_de_intentos(self, client, usuario_operador, db_session):
        """Test: Usuario se bloquea automáticamente después de múltiples intentos"""
        # Hacer 10 intentos fallidos
        for _ in range(10):
            client.post('/api/auth/login',
                data=json.dumps({
                    'usuario': 'operador_test',
                    'password': 'PasswordIncorrecta'
                }),
                content_type='application/json'
            )
        
        db_session.session.refresh(usuario_operador)
        assert usuario_operador.estado == 'BLOQUEADO'
        assert usuario_operador.intentos_fallidos >= 10
    
    def test_reseteo_intentos_en_login_exitoso(self, client, usuario_operador, db_session):
        """Test: Los intentos fallidos se resetean en login exitoso"""
        # Simular intentos fallidos
        usuario_operador.intentos_fallidos = 3
        db_session.session.commit()
        
        # Login exitoso
        response = client.post('/api/auth/login',
            data=json.dumps({
                'usuario': 'operador_test',
                'password': 'Test@123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        db_session.session.refresh(usuario_operador)
        assert usuario_operador.intentos_fallidos == 0


class TestAuthorizationRoles:
    """Tests para control de acceso por roles"""
    
    def test_usuario_master_acceso_completo(self, usuario_master, sede_test):
        """Test: Usuario master tiene acceso a todas las sedes"""
        assert usuario_master.rol == 'usuario_master'
        assert usuario_master.tiene_acceso_sede(sede_test.id) is True
        assert usuario_master.tiene_acceso_sede(999) is True  # Cualquier sede
    
    def test_usuario_operador_acceso_limitado(self, usuario_operador, sede_test, db_session):
        """Test: Usuario operador solo accede a su sede"""
        from app.models import Sede
        
        # Crear otra sede
        otra_sede = Sede(
            codigo_sede='OTRA',
            descripcion_sede='OTRA SEDE',
            direccion_sede='Otra dirección',
            estado='ACTIVO'
        )
        db_session.session.add(otra_sede)
        db_session.session.commit()
        
        assert usuario_operador.rol == 'usuario_operador'
        assert usuario_operador.tiene_acceso_sede(sede_test.id) is True
        assert usuario_operador.tiene_acceso_sede(otra_sede.id) is False


class TestPasswordSecurity:
    """Tests para seguridad de contraseñas"""
    
    def test_password_hash_es_diferente(self, usuario_master):
        """Test: El hash es diferente a la contraseña original"""
        assert usuario_master.password_hash != 'Test@123'
        assert len(usuario_master.password_hash) > 20  # Bcrypt hash es largo
    
    def test_mismo_password_diferente_hash(self, db_session, sede_test):
        """Test: Mismo password genera diferentes hashes"""
        password = 'MismoPassword@123'
        
        usuario1 = Usuario(
            tipo_identificacion='CC',
            num_identificacion='1111111111',
            primer_nombre='USER1',
            primer_apellido='TEST',
            num_telefono='3001111111',
            dir_correo='user1@test.com',
            sede_id=sede_test.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='user1'
        )
        usuario1.set_password(password)
        
        usuario2 = Usuario(
            tipo_identificacion='CC',
            num_identificacion='2222222222',
            primer_nombre='USER2',
            primer_apellido='TEST',
            num_telefono='3002222222',
            dir_correo='user2@test.com',
            sede_id=sede_test.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='user2'
        )
        usuario2.set_password(password)
        
        # Los hashes deben ser diferentes (sal diferente)
        assert usuario1.password_hash != usuario2.password_hash
        
        # Pero ambos deben validar el password correctamente
        assert usuario1.check_password(password) is True
        assert usuario2.check_password(password) is True
    
    def test_password_vacio_no_valida(self, usuario_master):
        """Test: Password vacío no valida"""
        assert usuario_master.check_password('') is False
    
    def test_cambio_de_password(self, usuario_master):
        """Test: Cambiar password funciona correctamente"""
        # Password original
        assert usuario_master.check_password('Test@123') is True
        
        # Cambiar password
        nuevo_password = 'NuevoPassword@456'
        usuario_master.set_password(nuevo_password)
        
        # Password anterior no funciona
        assert usuario_master.check_password('Test@123') is False
        # Nuevo password funciona
        assert usuario_master.check_password(nuevo_password) is True
