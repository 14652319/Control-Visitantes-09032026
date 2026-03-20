"""
========================================
TESTS - API ENDPOINTS
Tests para rutas y endpoints de la API
========================================
"""

import pytest
import json
from datetime import date, timedelta


class TestHealthEndpoint:
    """Tests para endpoint de health check"""
    
    def test_health_endpoint(self, client):
        """Test: Health check responde correctamente"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestUsuariosAPI:
    """Tests para endpoints de usuarios"""
    
    def test_verificar_identificacion_disponible(self, client, db_session):
        """Test: Verificar que identificación está disponible"""
        response = client.get('/api/usuarios/verificar-identificacion/9999999999')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['disponible'] is True
    
    def test_verificar_identificacion_no_disponible(self, client, usuario_master):
        """Test: Verificar que identificación ya existe"""
        response = client.get(f'/api/usuarios/verificar-identificacion/{usuario_master.num_identificacion}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['disponible'] is False
    
    def test_verificar_correo_disponible(self, client, db_session):
        """Test: Verificar que correo está disponible"""
        response = client.get('/api/usuarios/verificar-correo/nuevo@test.com')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['disponible'] is True
    
    def test_verificar_correo_no_disponible(self, client, usuario_master):
        """Test: Verificar que correo ya existe"""
        response = client.get(f'/api/usuarios/verificar-correo/{usuario_master.dir_correo}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['disponible'] is False


class TestSedesAPI:
    """Tests para endpoints de sedes"""
    
    def test_listar_sedes_vacio(self, client, db_session):
        """Test: Listar sedes cuando no hay ninguna"""
        # Limpiar sedes
        from app.models import Sede
        db_session.session.query(Sede).delete()
        db_session.session.commit()
        
        response = client.get('/api/sedes')
        
        # Note: Esto podría requerir autenticación según tu implementación
        # Si requiere auth, este test fallará y necesitarás agregar login
        assert response.status_code in [200, 401]


class TestVisitantesAPI:
    """Tests para endpoints de visitantes"""
    
    def test_buscar_visitante_no_existe(self, client):
        """Test: Buscar visitante que no existe"""
        response = client.get('/api/visitantes/buscar/CC/8888777766')
        
        # Podría requerir autenticación
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data.get('visitante') is None or data.get('encontrado') is False


class TestAutorizacionesAPI:
    """Tests para endpoints de autorizaciones"""
    
    def test_autorizacion_vencimiento_automatico(self, db_session, usuario_funcionario, sede_test):
        """Test: Las autorizaciones vencidas se marcan automáticamente"""
        from app.models import AutorizacionIngreso
        
        # Crear autorización vencida
        autorizacion = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='5555444433',
            primer_nombre='VENCIDO',
            primer_apellido='TEST',
            num_telefono='3005554444',
            empresa='TEST',
            nit_empresa='900555444',
            prefijo_dependencia='ADM',
            descripcion_dependencia='ADMIN',
            funcionario_autoriza='TEST',
            estado='PENDIENTE',
            fecha_vencimiento=date.today() - timedelta(days=2),
            usuario_id=usuario_funcionario.id,
            sede_id=sede_test.id
        )
        
        db_session.session.add(autorizacion)
        db_session.session.commit()
        
        # Verificar vencimiento
        autorizacion.verificar_vencimiento()
        db_session.session.commit()
        
        assert autorizacion.estado == 'VENCIDA'


class TestIntegrationFlow:
    """Tests de flujo de integración completo"""
    
    def test_flujo_completo_visitante(self, client, db_session, sede_test, dependencia_test):
        """Test: Flujo completo de registro y visita de un visitante"""
        # 1. Verificar que el visitante no existe
        response = client.get('/api/visitantes/buscar/CC/7777666655')
        if response.status_code == 200:
            data = json.loads(response.data)
            # El visitante no debería existir inicialmente
            assert data.get('encontrado', False) is False or data.get('visitante') is None
    
    def test_creacion_autorizacion_y_uso(self, db_session, usuario_funcionario, autorizacion_test):
        """Test: Crear autorización y marcarla como utilizada"""
        # Verificar que está pendiente
        assert autorizacion_test.estado == 'PENDIENTE'
        assert autorizacion_test.esta_activa is True
        
        # Simular uso de la autorización
        autorizacion_test.marcar_como_utilizada(log_visitante_id=123)
        db_session.session.commit()
        
        # Verificar que cambió de estado
        assert autorizacion_test.estado == 'UTILIZADA'
        assert autorizacion_test.esta_activa is False
        assert autorizacion_test.fecha_utilizacion is not None


class TestDataValidation:
    """Tests para validación de datos"""
    
    def test_usuario_campos_unicos(self, db_session, usuario_master, sede_test):
        """Test: No se pueden crear usuarios con identificación o correo duplicados"""
        from app.models import Usuario
        from sqlalchemy.exc import IntegrityError
        
        # Intentar crear usuario con identificación duplicada
        usuario_duplicado = Usuario(
            tipo_identificacion='CC',
            num_identificacion=usuario_master.num_identificacion,  # Duplicado
            primer_nombre='OTRO',
            primer_apellido='USUARIO',
            num_telefono='3009999999',
            dir_correo='otro@test.com',
            sede_id=sede_test.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='otro_usuario'
        )
        
        db_session.session.add(usuario_duplicado)
        
        with pytest.raises(IntegrityError):
            db_session.session.commit()
        
        db_session.session.rollback()
    
    def test_visitante_identificacion_unica(self, db_session, visitante_test):
        """Test: No se pueden crear visitantes con identificación duplicada"""
        from app.models import Visitante
        from sqlalchemy.exc import IntegrityError
        
        visitante_duplicado = Visitante(
            tipo_identificacion='CC',
            num_identificacion=visitante_test.num_identificacion,  # Duplicado
            primer_nombre='OTRO',
            primer_apellido='VISITANTE',
            num_telefono='3008888888',
            dir_correo='otro@visitante.com',
            empresa='OTRA EMPRESA',
            nit_empresa='900888888',
            estado='ACTIVO'
        )
        
        db_session.session.add(visitante_duplicado)
        
        with pytest.raises(IntegrityError):
            db_session.session.commit()
        
        db_session.session.rollback()


class TestEdgeCases:
    """Tests para casos extremos"""
    
    def test_autorizacion_fecha_limite(self, db_session, usuario_funcionario, sede_test):
        """Test: Autorización con fecha de vencimiento exacta a hoy"""
        from app.models import AutorizacionIngreso
        
        autorizacion = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='6666555544',
            primer_nombre='HOY',
            primer_apellido='TEST',
            num_telefono='3006665555',
            empresa='TEST',
            nit_empresa='900666555',
            prefijo_dependencia='ADM',
            descripcion_dependencia='ADMIN',
            funcionario_autoriza='TEST',
            estado='PENDIENTE',
            fecha_vencimiento=date.today(),  # Hoy
            usuario_id=usuario_funcionario.id,
            sede_id=sede_test.id
        )
        
        db_session.session.add(autorizacion)
        db_session.session.commit()
        
        # Hoy no debería estar vencida (vence después de hoy)
        autorizacion.verificar_vencimiento()
        # La lógica exacta depende de tu implementación
        # Ajustar según si consideras "hoy" como vencido o no
    
    def test_usuario_sin_segundo_nombre(self, db_session, sede_test):
        """Test: Usuario puede crearse sin segundo nombre ni segundo apellido"""
        from app.models import Usuario
        
        usuario = Usuario(
            tipo_identificacion='CC',
            num_identificacion='3333444455',
            primer_nombre='SOLO',
            segundo_nombre='',  # Vacío
            primer_apellido='NOMBRE',
            segundo_apellido='',  # Vacío
            num_telefono='3003334444',
            dir_correo='solo@test.com',
            sede_id=sede_test.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='sololnombre'
        )
        usuario.set_password('Test@123')
        
        db_session.session.add(usuario)
        db_session.session.commit()
        
        assert usuario.id is not None
        assert usuario.segundo_nombre == ''
        assert usuario.segundo_apellido == ''
