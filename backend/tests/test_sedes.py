"""
========================================
TESTS - SEDES
Tests para todos los endpoints de gestión de sedes
6 endpoints: publico, listar, obtener, crear, actualizar, eliminar
========================================
"""

import pytest
import json


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def login_master(client, usuario_master):
    """Login como master y devuelve client autenticado"""
    client.post('/api/auth/login',
        data=json.dumps({'usuario': 'admin_test', 'password': 'Test@123'}),
        content_type='application/json'
    )
    return client


@pytest.fixture
def login_operador(client, usuario_operador):
    """Login como operador y devuelve client autenticado"""
    client.post('/api/auth/login',
        data=json.dumps({'usuario': 'operador_test', 'password': 'Test@123'}),
        content_type='application/json'
    )
    return client


@pytest.fixture
def login_funcionario(client, usuario_funcionario):
    """Login como funcionario y devuelve client autenticado"""
    client.post('/api/auth/login',
        data=json.dumps({'usuario': 'funcionario_test', 'password': 'Test@123'}),
        content_type='application/json'
    )
    return client


# ============================================================
# TESTS: GET /api/sedes/publico
# ============================================================

class TestSedesPublico:
    """Tests para endpoint público de sedes"""

    def test_listar_publico_sin_auth(self, client, sede_test):
        """Endpoint público no requiere autenticación"""
        resp = client.get('/api/sedes/publico')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'sedes' in data
        assert len(data['sedes']) >= 1

    def test_listar_publico_solo_activas(self, client, sede_test, db_session):
        """El endpoint público solo retorna sedes activas"""
        from app.models import Sede
        sede_inactiva = Sede(
            codigo_sede='INACT01',
            descripcion_sede='SEDE INACTIVA',
            direccion_sede='Calle Inactiva',
            estado='INACTIVO'
        )
        db_session.session.add(sede_inactiva)
        db_session.session.commit()

        resp = client.get('/api/sedes/publico')
        data = json.loads(resp.data)
        for sede in data['sedes']:
            assert sede['estado'] == 'ACTIVO'


# ============================================================
# TESTS: GET /api/sedes/
# ============================================================

class TestListarSedes:
    """Tests para listar todas las sedes"""

    def test_listar_sin_autenticacion(self, client):
        resp = client.get('/api/sedes/')
        assert resp.status_code in [401, 302]

    def test_listar_como_master(self, login_master, sede_test):
        resp = login_master.get('/api/sedes/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'total' in data
        assert 'sedes' in data
        assert data['total'] >= 1

    def test_listar_como_operador(self, login_operador, sede_test):
        resp = login_operador.get('/api/sedes/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_listar_incluye_inactivas(self, login_master, sede_test, db_session):
        """A diferencia de /publico, /api/sedes/ incluye todas"""
        from app.models import Sede
        sede_inactiva = Sede(
            codigo_sede='INACT02',
            descripcion_sede='OTRA INACTIVA',
            direccion_sede='Calle Inactiva 2',
            estado='INACTIVO'
        )
        db_session.session.add(sede_inactiva)
        db_session.session.commit()

        resp = login_master.get('/api/sedes/')
        data = json.loads(resp.data)
        estados = [s['estado'] for s in data['sedes']]
        assert 'INACTIVO' in estados


# ============================================================
# TESTS: GET /api/sedes/<id>
# ============================================================

class TestObtenerSede:
    """Tests para obtener sede por ID"""

    def test_obtener_existente(self, login_master, sede_test):
        resp = login_master.get(f'/api/sedes/{sede_test.id}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['sede']['codigo_sede'] == 'TEST001'

    def test_obtener_inexistente(self, login_master):
        resp = login_master.get('/api/sedes/99999')
        assert resp.status_code == 404
        data = json.loads(resp.data)
        assert data['success'] is False

    def test_obtener_sin_autenticacion(self, client, sede_test):
        resp = client.get(f'/api/sedes/{sede_test.id}')
        assert resp.status_code in [401, 302]


# ============================================================
# TESTS: POST /api/sedes/
# ============================================================

class TestCrearSede:
    """Tests para crear sede"""

    def test_crear_sede_exitosa(self, login_master):
        resp = login_master.post('/api/sedes/',
            data=json.dumps({
                'codigo_sede': 'NUEVA01',
                'descripcion_sede': 'Sede Nueva',
                'direccion_sede': 'Carrera 1 #2-3'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['sede']['codigo_sede'] == 'NUEVA01'
        assert data['sede']['descripcion_sede'] == 'SEDE NUEVA'  # uppercase

    def test_crear_sin_codigo(self, login_master):
        resp = login_master.post('/api/sedes/',
            data=json.dumps({
                'descripcion_sede': 'Sin Código',
                'direccion_sede': 'Dirección'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_crear_sin_descripcion(self, login_master):
        resp = login_master.post('/api/sedes/',
            data=json.dumps({
                'codigo_sede': 'NODESC',
                'direccion_sede': 'Dirección'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_crear_sin_direccion(self, login_master):
        resp = login_master.post('/api/sedes/',
            data=json.dumps({
                'codigo_sede': 'NODIR',
                'descripcion_sede': 'Sin Dirección'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_crear_codigo_duplicado(self, login_master, sede_test):
        resp = login_master.post('/api/sedes/',
            data=json.dumps({
                'codigo_sede': 'TEST001',  # Ya existe
                'descripcion_sede': 'Duplicada',
                'direccion_sede': 'Calle Duplicada'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 409

    def test_crear_como_operador_denegado(self, login_operador):
        resp = login_operador.post('/api/sedes/',
            data=json.dumps({
                'codigo_sede': 'HACK',
                'descripcion_sede': 'Hack',
                'direccion_sede': 'Hack'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 403

    def test_crear_como_funcionario_denegado(self, login_funcionario):
        resp = login_funcionario.post('/api/sedes/',
            data=json.dumps({
                'codigo_sede': 'FUNC',
                'descripcion_sede': 'Func',
                'direccion_sede': 'Func'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 403


# ============================================================
# TESTS: PUT /api/sedes/<id>
# ============================================================

class TestActualizarSede:
    """Tests para actualizar sede"""

    def test_actualizar_descripcion(self, login_master, sede_test):
        resp = login_master.put(f'/api/sedes/{sede_test.id}',
            data=json.dumps({'descripcion_sede': 'Descripción Actualizada'}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['sede']['descripcion_sede'] == 'DESCRIPCIÓN ACTUALIZADA'

    def test_actualizar_direccion(self, login_master, sede_test):
        resp = login_master.put(f'/api/sedes/{sede_test.id}',
            data=json.dumps({'direccion_sede': 'Nueva Dirección 123'}),
            content_type='application/json'
        )
        assert resp.status_code == 200

    def test_actualizar_estado(self, login_master, sede_test):
        resp = login_master.put(f'/api/sedes/{sede_test.id}',
            data=json.dumps({'estado': 'INACTIVO'}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['sede']['estado'] == 'INACTIVO'

    def test_actualizar_inexistente(self, login_master):
        resp = login_master.put('/api/sedes/99999',
            data=json.dumps({'descripcion_sede': 'Nada'}),
            content_type='application/json'
        )
        assert resp.status_code == 404

    def test_actualizar_como_operador_denegado(self, login_operador, sede_test):
        resp = login_operador.put(f'/api/sedes/{sede_test.id}',
            data=json.dumps({'descripcion_sede': 'Hack'}),
            content_type='application/json'
        )
        assert resp.status_code == 403


# ============================================================
# TESTS: DELETE /api/sedes/<id>
# ============================================================

class TestEliminarSede:
    """Tests para eliminar sede"""

    def test_eliminar_sede_sin_asociaciones(self, login_master, db_session):
        """Puede eliminar sede sin usuarios ni visitas"""
        from app.models import Sede
        sede_sola = Sede(
            codigo_sede='SOLA01',
            descripcion_sede='SEDE SOLA',
            direccion_sede='Calle Sola',
            estado='ACTIVO'
        )
        db_session.session.add(sede_sola)
        db_session.session.commit()
        sede_id = sede_sola.id

        resp = login_master.delete(f'/api/sedes/{sede_id}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_eliminar_sede_con_usuarios_denegado(self, login_master, sede_test, usuario_operador):
        """No puede eliminar sede con usuarios asociados"""
        resp = login_master.delete(f'/api/sedes/{sede_test.id}')
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert 'usuario' in data['message'].lower()

    def test_eliminar_inexistente(self, login_master):
        resp = login_master.delete('/api/sedes/99999')
        assert resp.status_code == 404

    def test_eliminar_como_operador_denegado(self, login_operador, sede_test):
        resp = login_operador.delete(f'/api/sedes/{sede_test.id}')
        assert resp.status_code == 403

    def test_eliminar_como_funcionario_denegado(self, login_funcionario, sede_test):
        resp = login_funcionario.delete(f'/api/sedes/{sede_test.id}')
        assert resp.status_code == 403
