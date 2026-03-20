"""
========================================
TESTS DE VISITANTES
Sistema de Control de Visitantes
========================================
"""

import pytest
import json


def login_as_operador(client, usuario_operador):
    """Helper para hacer login como operador"""
    response = client.post('/api/auth/login', json={
        'username': 'operador_test',
        'password': 'Oper@123'
    })
    return response


def test_buscar_visitante_existente(client, usuario_operador, visitante_prueba, db_session):
    """Test de búsqueda de visitante existente"""
    # Login primero
    login_as_operador(client, usuario_operador)
    
    # Buscar visitante
    response = client.get('/api/visitantes/buscar', query_string={
        'tipo_identificacion': 'CC',
        'num_identificacion': '12345678'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['encontrado'] is True
    assert data['visitante']['num_identificacion'] == '12345678'


def test_buscar_visitante_no_existente(client, usuario_operador):
    """Test de búsqueda de visitante no existente"""
    login_as_operador(client, usuario_operador)
    
    response = client.get('/api/visitantes/buscar', query_string={
        'tipo_identificacion': 'CC',
        'num_identificacion': '99999999'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['encontrado'] is False


def test_buscar_visitante_sin_parametros(client, usuario_operador):
    """Test de búsqueda sin parámetros"""
    login_as_operador(client, usuario_operador)
    
    response = client.get('/api/visitantes/buscar')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False


def test_registrar_visitante_nuevo(client, usuario_operador, db_session):
    """Test de registro de visitante nuevo"""
    login_as_operador(client, usuario_operador)
    
    response = client.post('/api/visitantes/registrar', json={
        'tipo_identificacion': 'CC',
        'num_identificacion': '11111111',
        'primer_nombre': 'Test',
        'primer_apellido': 'Usuario',
        'num_telefono': '3001111111',
        'dir_correo': 'test@test.com',
        'empresa': 'Test SAS',
        'nit_empresa': '900111111-1'
    })
    
    assert response.status_code in [200, 201]
    data = json.loads(response.data)
    assert data['success'] is True


def test_registrar_visitante_duplicado(client, usuario_operador, visitante_prueba, db_session):
    """Test de registro de visitante duplicado"""
    login_as_operador(client, usuario_operador)
    
    response = client.post('/api/visitantes/registrar', json={
        'tipo_identificacion': 'CC',
        'num_identificacion': '12345678',  # Ya existe
        'primer_nombre': 'Juan',
        'primer_apellido': 'Pérez',
        'num_telefono': '3001234567',
        'dir_correo': 'juan@test.com',
        'empresa': 'Test SAS',
        'nit_empresa': '900123456-1'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'registrado' in data['message'].lower()


def test_listar_visitantes(client, usuario_operador, visitante_prueba, db_session):
    """Test de listado de visitantes"""
    login_as_operador(client, usuario_operador)
    
    response = client.get('/api/visitantes/listar')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'visitas' in data
    assert isinstance(data['visitas'], list)


def test_listar_visitantes_con_filtros(client, usuario_operador, db_session):
    """Test de listado con filtros"""
    login_as_operador(client, usuario_operador)
    
    response = client.get('/api/visitantes/listar', query_string={
        'busqueda': '12345',
        'pagina': 1,
        'por_pagina': 10
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'pagina' in data
    assert 'total' in data


def test_buscar_por_nit(client, usuario_operador, visitante_prueba, db_session):
    """Test de búsqueda por NIT"""
    login_as_operador(client, usuario_operador)
    
    response = client.get('/api/visitantes/buscar-por-nit', query_string={
        'nit': '900123456-1'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    if data['success']:
        assert data['empresa'] == 'Empresa Test SAS'
