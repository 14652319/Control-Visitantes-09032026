"""
========================================
TESTS - CONFIGURACIÓN DEL SISTEMA
Tests para endpoints de configuracion_sistema
4 endpoints: GET /, GET /<clave>, PUT /<clave>, PUT /batch
========================================
"""

import pytest
import json


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def login_master(client, usuario_master):
    """Login como master — configuracion.py usa session['usuario_id'] custom"""
    client.post('/api/auth/login',
        data=json.dumps({'usuario': 'admin_test', 'password': 'Test@123'}),
        content_type='application/json'
    )
    # configuracion.py tiene decoradores custom que leen session['usuario_id']
    with client.session_transaction() as sess:
        sess['usuario_id'] = usuario_master.id
    return client


@pytest.fixture
def login_operador(client, usuario_operador):
    """Login como operador — configuracion.py usa session['usuario_id'] custom"""
    client.post('/api/auth/login',
        data=json.dumps({'usuario': 'operador_test', 'password': 'Test@123'}),
        content_type='application/json'
    )
    with client.session_transaction() as sess:
        sess['usuario_id'] = usuario_operador.id
    return client


@pytest.fixture
def login_funcionario(client, usuario_funcionario):
    """Login como funcionario — configuracion.py usa session['usuario_id'] custom"""
    client.post('/api/auth/login',
        data=json.dumps({'usuario': 'funcionario_test', 'password': 'Test@123'}),
        content_type='application/json'
    )
    with client.session_transaction() as sess:
        sess['usuario_id'] = usuario_funcionario.id
    return client


@pytest.fixture
def config_prueba(db_session):
    """Crea configuraciones de prueba (limpia antes)"""
    from app.models.configuracion_sistema import ConfiguracionSistema
    # Limpiar existentes
    ConfiguracionSistema.query.delete()
    db_session.session.commit()
    configs = [
        ConfiguracionSistema(
            clave='dias_vigencia_autorizacion',
            valor='15',
            descripcion='Días de vigencia de autorizaciones',
            tipo_dato='int'
        ),
        ConfiguracionSistema(
            clave='max_intentos_login',
            valor='10',
            descripcion='Máximo de intentos de login',
            tipo_dato='int'
        ),
        ConfiguracionSistema(
            clave='tiempo_sesion_minutos',
            valor='45',
            descripcion='Tiempo de sesión en minutos',
            tipo_dato='int'
        ),
        ConfiguracionSistema(
            clave='nombre_empresa',
            valor='Supertiendas Cañaveral',
            descripcion='Nombre de la empresa',
            tipo_dato='string'
        ),
    ]
    for c in configs:
        db_session.session.add(c)
    db_session.session.commit()
    return configs


# ============================================================
# TESTS: GET /api/configuracion/
# ============================================================

class TestObtenerConfiguraciones:
    """Tests para listar todas las configuraciones"""

    def test_listar_sin_autenticacion(self, client):
        resp = client.get('/api/configuracion/')
        assert resp.status_code == 401

    def test_listar_como_master(self, login_master, config_prueba):
        resp = login_master.get('/api/configuracion/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'configuraciones' in data
        assert len(data['configuraciones']) == 4

    def test_listar_como_operador_denegado(self, login_operador, config_prueba):
        resp = login_operador.get('/api/configuracion/')
        assert resp.status_code == 403
        data = json.loads(resp.data)
        assert data['success'] is False

    def test_listar_como_funcionario_denegado(self, login_funcionario, config_prueba):
        resp = login_funcionario.get('/api/configuracion/')
        assert resp.status_code == 403


# ============================================================
# TESTS: GET /api/configuracion/<clave>
# ============================================================

class TestObtenerConfiguracion:
    """Tests para obtener configuración por clave"""

    def test_obtener_clave_existente(self, login_master, config_prueba):
        resp = login_master.get('/api/configuracion/dias_vigencia_autorizacion')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['clave'] == 'dias_vigencia_autorizacion'
        assert data['valor'] == 15  # tipo_dato=int, se convierte

    def test_obtener_clave_string(self, login_master, config_prueba):
        resp = login_master.get('/api/configuracion/nombre_empresa')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['valor'] == 'Supertiendas Cañaveral'

    def test_obtener_clave_inexistente(self, login_master):
        resp = login_master.get('/api/configuracion/clave_no_existe')
        assert resp.status_code == 404
        data = json.loads(resp.data)
        assert data['success'] is False

    def test_obtener_sin_autenticacion(self, client):
        resp = client.get('/api/configuracion/dias_vigencia_autorizacion')
        assert resp.status_code == 401


# ============================================================
# TESTS: PUT /api/configuracion/<clave>
# ============================================================

class TestActualizarConfiguracion:
    """Tests para actualizar configuración individual"""

    def test_actualizar_dias_vigencia_valido(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/dias_vigencia_autorizacion',
            data=json.dumps({'valor': 30}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['valor'] == 30

    def test_actualizar_dias_vigencia_fuera_rango_bajo(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/dias_vigencia_autorizacion',
            data=json.dumps({'valor': 0}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_dias_vigencia_fuera_rango_alto(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/dias_vigencia_autorizacion',
            data=json.dumps({'valor': 400}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_max_intentos_valido(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/max_intentos_login',
            data=json.dumps({'valor': 5}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['valor'] == 5

    def test_actualizar_max_intentos_fuera_rango(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/max_intentos_login',
            data=json.dumps({'valor': 200}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_tiempo_sesion_valido(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/tiempo_sesion_minutos',
            data=json.dumps({'valor': 60}),
            content_type='application/json'
        )
        assert resp.status_code == 200

    def test_actualizar_tiempo_sesion_muy_bajo(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/tiempo_sesion_minutos',
            data=json.dumps({'valor': 2}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_tiempo_sesion_muy_alto(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/tiempo_sesion_minutos',
            data=json.dumps({'valor': 2000}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_sin_campo_valor(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/nombre_empresa',
            data=json.dumps({'descripcion': 'test'}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_clave_generica(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/nombre_empresa',
            data=json.dumps({'valor': 'Nueva Empresa'}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_actualizar_como_operador_denegado(self, login_operador, config_prueba):
        resp = login_operador.put('/api/configuracion/nombre_empresa',
            data=json.dumps({'valor': 'Hack'}),
            content_type='application/json'
        )
        assert resp.status_code == 403

    def test_actualizar_sin_autenticacion(self, client):
        resp = client.put('/api/configuracion/nombre_empresa',
            data=json.dumps({'valor': 'Hack'}),
            content_type='application/json'
        )
        assert resp.status_code == 401

    def test_crear_nueva_clave(self, login_master):
        resp = login_master.put('/api/configuracion/nueva_clave',
            data=json.dumps({'valor': 'valor_nuevo', 'tipo_dato': 'string'}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True


# ============================================================
# TESTS: PUT /api/configuracion/batch
# ============================================================

class TestActualizarBatch:
    """Tests para actualización batch de configuraciones"""

    def test_batch_exitoso(self, login_master, config_prueba):
        resp = login_master.put('/api/configuracion/batch',
            data=json.dumps({
                'configuraciones': [
                    {'clave': 'nombre_empresa', 'valor': 'Empresa Batch'},
                    {'clave': 'nueva_config', 'valor': 'valor_batch', 'tipo_dato': 'string'},
                ]
            }),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert len(data['resultados']) == 2

    def test_batch_sin_array(self, login_master):
        resp = login_master.put('/api/configuracion/batch',
            data=json.dumps({'configuraciones': 'no_es_array'}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_batch_campo_faltante(self, login_master):
        resp = login_master.put('/api/configuracion/batch',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_batch_como_operador_denegado(self, login_operador):
        resp = login_operador.put('/api/configuracion/batch',
            data=json.dumps({
                'configuraciones': [
                    {'clave': 'test', 'valor': 'hack'}
                ]
            }),
            content_type='application/json'
        )
        assert resp.status_code == 403

    def test_batch_con_errores_parciales(self, login_master):
        resp = login_master.put('/api/configuracion/batch',
            data=json.dumps({
                'configuraciones': [
                    {'clave': 'buena_config', 'valor': 'ok'},
                    {'clave': '', 'valor': None},  # Inválida
                ]
            }),
            content_type='application/json'
        )
        # Con errores parciales retorna 400
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert len(data.get('errores', [])) > 0
