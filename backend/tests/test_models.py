"""
========================================
TESTS - MODELOS
Tests para modelos de base de datos
========================================
"""

import pytest
from datetime import datetime, date, timedelta
from app.models import Usuario, Sede, Dependencia, Visitante, AutorizacionIngreso


class TestUsuario:
    """Tests para el modelo Usuario"""
    
    def test_crear_usuario(self, db_session, sede_test):
        """Test: Crear un usuario correctamente"""
        usuario = Usuario(
            tipo_identificacion='CC',
            num_identificacion='5555666677',
            primer_nombre='TEST',
            segundo_nombre='',
            primer_apellido='USER',
            segundo_apellido='',
            num_telefono='3005556666',
            dir_correo='test@example.com',
            sede_id=sede_test.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='testuser'
        )
        usuario.set_password('Password@123')
        
        db_session.session.add(usuario)
        db_session.session.commit()
        
        assert usuario.id is not None
        assert usuario.usuario == 'testuser'
        assert usuario.rol == 'usuario_operador'
        assert usuario.estado == 'ACTIVO'
    
    def test_password_hash(self, db_session, sede_test):
        """Test: Verificar que las contraseñas se hashean correctamente"""
        usuario = Usuario(
            tipo_identificacion='CC',
            num_identificacion='7777888899',
            primer_nombre='PASS',
            segundo_nombre='',
            primer_apellido='TEST',
            segundo_apellido='',
            num_telefono='3007778888',
            dir_correo='pass@test.com',
            sede_id=sede_test.id,
            rol='usuario_operador',
            estado='ACTIVO',
            usuario='passtest'
        )
        
        password = 'SecurePass@123'
        usuario.set_password(password)
        
        # Verificar que el hash no es igual a la contraseña original
        assert usuario.password_hash != password
        # Verificar que se puede validar la contraseña
        assert usuario.check_password(password) is True
        # Verificar que una contraseña incorrecta falla
        assert usuario.check_password('WrongPassword') is False
    
    def test_intentos_fallidos(self, usuario_operador):
        """Test: Incrementar intentos fallidos y bloqueo automático"""
        assert usuario_operador.intentos_fallidos == 0
        assert usuario_operador.estado == 'ACTIVO'
        
        # Simular 10 intentos fallidos
        for _ in range(10):
            usuario_operador.incrementar_intentos_fallidos()
        
        assert usuario_operador.intentos_fallidos == 10
        assert usuario_operador.estado == 'BLOQUEADO'
    
    def test_resetear_intentos(self, usuario_operador):
        """Test: Resetear intentos fallidos"""
        usuario_operador.intentos_fallidos = 5
        usuario_operador.estado = 'BLOQUEADO'
        
        usuario_operador.resetear_intentos_fallidos()
        
        assert usuario_operador.intentos_fallidos == 0
        assert usuario_operador.estado == 'ACTIVO'
    
    def test_acceso_sede_master(self, usuario_master, sede_test):
        """Test: Usuario master tiene acceso a todas las sedes"""
        assert usuario_master.tiene_acceso_sede(sede_test.id) is True
        assert usuario_master.tiene_acceso_sede(9999) is True  # Cualquier sede
    
    def test_acceso_sede_operador(self, usuario_operador, sede_test):
        """Test: Usuario operador solo accede a su sede"""
        assert usuario_operador.tiene_acceso_sede(sede_test.id) is True
        assert usuario_operador.tiene_acceso_sede(9999) is False  # Otra sede
    
    def test_to_dict(self, usuario_master):
        """Test: Conversión a diccionario"""
        data = usuario_master.to_dict()
        
        assert isinstance(data, dict)
        assert data['usuario'] == 'admin_test'
        assert data['rol'] == 'usuario_master'
        assert 'password_hash' not in data  # No debe incluir el hash


class TestSede:
    """Tests para el modelo Sede"""
    
    def test_crear_sede(self, db_session):
        """Test: Crear una sede correctamente"""
        sede = Sede(
            codigo_sede='SEDE999',
            descripcion_sede='SEDE NUEVA',
            direccion_sede='Calle Nueva 456',
            estado='ACTIVO'
        )
        
        db_session.session.add(sede)
        db_session.session.commit()
        
        assert sede.id is not None
        assert sede.codigo_sede == 'SEDE999'
        assert sede.estado == 'ACTIVO'


class TestVisitante:
    """Tests para el modelo Visitante"""
    
    def test_crear_visitante(self, db_session):
        """Test: Crear un visitante correctamente"""
        visitante = Visitante(
            tipo_identificacion='CC',
            num_identificacion='4444333322',
            primer_nombre='MARIA',
            segundo_nombre='',
            primer_apellido='LOPEZ',
            segundo_apellido='',
            num_telefono='3004443333',
            dir_correo='maria@test.com',
            empresa='TEST COMPANY',
            nit_empresa='900111222',
            estado='ACTIVO'
        )
        
        db_session.session.add(visitante)
        db_session.session.commit()
        
        assert visitante.id is not None
        assert visitante.num_identificacion == '4444333322'
        assert visitante.estado == 'ACTIVO'
    
    def test_nombre_completo(self, visitante_test):
        """Test: Obtener nombre completo del visitante"""
        assert visitante_test.primer_nombre == 'JUAN'
        assert visitante_test.primer_apellido == 'PEREZ'


class TestAutorizacionIngreso:
    """Tests para el modelo AutorizacionIngreso"""
    
    def test_crear_autorizacion(self, db_session, usuario_funcionario, sede_test):
        """Test: Crear una autorización correctamente"""
        autorizacion = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='3333222211',
            primer_nombre='CARLOS',
            segundo_nombre='',
            primer_apellido='MARTINEZ',
            segundo_apellido='',
            num_telefono='3003332222',
            empresa='EMPRESA ABC',
            nit_empresa='900333222',
            prefijo_dependencia='SIS',
            descripcion_dependencia='SISTEMAS',
            funcionario_autoriza='ADMIN',
            estado='PENDIENTE',
            fecha_vencimiento=date.today() + timedelta(days=1),
            usuario_id=usuario_funcionario.id,
            sede_id=sede_test.id
        )
        
        db_session.session.add(autorizacion)
        db_session.session.commit()
        
        assert autorizacion.id is not None
        assert autorizacion.estado == 'PENDIENTE'
        assert autorizacion.fecha_vencimiento > date.today()
    
    def test_marcar_como_utilizada(self, autorizacion_test):
        """Test: Marcar autorización como utilizada"""
        assert autorizacion_test.estado == 'PENDIENTE'
        
        autorizacion_test.marcar_como_utilizada(log_visitante_id=1)
        
        assert autorizacion_test.estado == 'UTILIZADA'
        assert autorizacion_test.utilizada_en_log_id == 1
        assert autorizacion_test.fecha_utilizacion is not None
    
    def test_cancelar_autorizacion(self, autorizacion_test):
        """Test: Cancelar una autorización pendiente"""
        assert autorizacion_test.estado == 'PENDIENTE'
        
        resultado = autorizacion_test.cancelar()
        
        assert resultado is True
        assert autorizacion_test.estado == 'CANCELADA'
    
    def test_no_cancelar_utilizada(self, autorizacion_test):
        """Test: No se puede cancelar una autorización ya utilizada"""
        autorizacion_test.marcar_como_utilizada(1)
        
        resultado = autorizacion_test.cancelar()
        
        assert resultado is False
        assert autorizacion_test.estado == 'UTILIZADA'
    
    def test_verificar_vencimiento(self, db_session, usuario_funcionario, sede_test):
        """Test: Verificar que las autorizaciones vencidas se marcan correctamente"""
        # Crear autorización vencida (fecha en el pasado)
        autorizacion_vencida = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='2222111100',
            primer_nombre='VENCIDO',
            segundo_nombre='',
            primer_apellido='TEST',
            segundo_apellido='',
            num_telefono='3002221111',
            empresa='EMPRESA OLD',
            nit_empresa='900222111',
            prefijo_dependencia='ADM',
            descripcion_dependencia='ADMIN',
            funcionario_autoriza='ADMIN',
            estado='PENDIENTE',
            fecha_vencimiento=date.today() - timedelta(days=1),  # Ayer
            usuario_id=usuario_funcionario.id,
            sede_id=sede_test.id
        )
        
        db_session.session.add(autorizacion_vencida)
        db_session.session.commit()
        
        assert autorizacion_vencida.estado == 'PENDIENTE'
        
        # Verificar vencimiento
        vencida = autorizacion_vencida.verificar_vencimiento()
        
        assert vencida is True
        assert autorizacion_vencida.estado == 'VENCIDA'
    
    def test_esta_activa(self, autorizacion_test):
        """Test: Verificar si una autorización está activa"""
        assert autorizacion_test.esta_activa is True
        
        # Marcar como utilizada
        autorizacion_test.marcar_como_utilizada(1)
        assert autorizacion_test.esta_activa is False
        
    def test_to_dict(self, autorizacion_test):
        """Test: Conversión a diccionario"""
        data = autorizacion_test.to_dict()
        
        assert isinstance(data, dict)
        assert data['estado'] == 'PENDIENTE'
        assert data['empresa'] == 'EMPRESA XYZ'
