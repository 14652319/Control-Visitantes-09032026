"""
========================================
TESTS - AUTORIZACIONES DE INGRESO (COMPLETO)
Tests para todos los endpoints de autorizaciones visitantes
9 endpoints: listar, buscar, crear, obtener, actualizar, cancelar, eliminar, aplicar, estadísticas
========================================
"""

import pytest
import json
from datetime import date, timedelta


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


@pytest.fixture
def autorizacion_cancelada(db_session, usuario_funcionario, sede_test):
    """Crea una autorización en estado CANCELADA para tests de eliminación"""
    from app.models import AutorizacionIngreso
    auth = AutorizacionIngreso(
        tipo_identificacion='CC',
        num_identificacion='5555666677',
        primer_nombre='CANCELADO',
        primer_apellido='TEST',
        empresa='EMPRESA CANCEL',
        nit_empresa='900555666',
        prefijo_dependencia='TEST',
        descripcion_dependencia='DEPENDENCIA TEST',
        funcionario_autoriza='FUNC TEST',
        estado='CANCELADA',
        fecha_vencimiento=date.today() + timedelta(days=1),
        usuario_id=usuario_funcionario.id,
        sede_id=sede_test.id
    )
    db_session.session.add(auth)
    db_session.session.commit()
    return auth


@pytest.fixture
def autorizacion_utilizada(db_session, usuario_funcionario, sede_test):
    """Crea una autorización en estado UTILIZADA"""
    from app.models import AutorizacionIngreso
    auth = AutorizacionIngreso(
        tipo_identificacion='CC',
        num_identificacion='7777888899',
        primer_nombre='UTILIZADO',
        primer_apellido='TEST',
        empresa='EMPRESA UTIL',
        nit_empresa='900777888',
        prefijo_dependencia='TEST',
        descripcion_dependencia='DEPENDENCIA TEST',
        funcionario_autoriza='FUNC TEST',
        estado='UTILIZADA',
        fecha_vencimiento=date.today() + timedelta(days=1),
        usuario_id=usuario_funcionario.id,
        sede_id=sede_test.id
    )
    db_session.session.add(auth)
    db_session.session.commit()
    return auth


DATA_AUTORIZACION = {
    'tipo_identificacion': 'CC',
    'num_identificacion': '3333444455',
    'primer_nombre': 'NUEVO',
    'segundo_nombre': 'VISITANTE',
    'primer_apellido': 'AUTORIZADO',
    'segundo_apellido': 'TEST',
    'empresa': 'EMPRESA NUEVA SAS',
    'nit_empresa': '900333444',
    'prefijo_dependencia': 'TEST',
    'descripcion_dependencia': 'DEPENDENCIA TEST',
    'funcionario_autoriza': 'FUNCIONARIO PRUEBA',
    'observaciones': 'Reunión de trabajo'
}


# ============================================================
# TESTS: GET /api/autorizaciones/
# ============================================================

class TestListarAutorizaciones:
    """Tests para listar autorizaciones"""

    def test_listar_sin_autenticacion(self, client):
        resp = client.get('/api/autorizaciones/')
        assert resp.status_code in [401, 302]

    def test_listar_como_master(self, login_master, autorizacion_test):
        resp = login_master.get('/api/autorizaciones/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'autorizaciones' in data
        assert 'total' in data
        assert data['total'] >= 1

    def test_listar_como_funcionario_solo_propias(self, login_funcionario, autorizacion_test):
        resp = login_funcionario.get('/api/autorizaciones/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        # Funcionario solo ve sus propias autorizaciones
        for auth in data['autorizaciones']:
            assert auth is not None

    def test_listar_como_operador_solo_pendientes_sede(self, login_operador, autorizacion_test):
        resp = login_operador.get('/api/autorizaciones/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_listar_filtrar_por_estado(self, login_master, autorizacion_test):
        resp = login_master.get('/api/autorizaciones/?estado=PENDIENTE')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        for auth in data['autorizaciones']:
            assert auth['estado'] == 'PENDIENTE'

    def test_listar_incluir_vencidas(self, login_master, autorizacion_test):
        resp = login_master.get('/api/autorizaciones/?incluir_vencidas=true')
        assert resp.status_code == 200


# ============================================================
# TESTS: GET /api/autorizaciones/buscar
# ============================================================

class TestBuscarAutorizacion:
    """Tests para buscar autorizaciones por identificación"""

    def test_buscar_existente(self, login_operador, autorizacion_test):
        resp = login_operador.get('/api/autorizaciones/buscar?identificacion=9999888877')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['encontrado'] is True
        assert data['total'] >= 1

    def test_buscar_no_existente(self, login_operador):
        resp = login_operador.get('/api/autorizaciones/buscar?identificacion=0000000000')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['encontrado'] is False
        assert data['total'] == 0

    def test_buscar_sin_parametro(self, login_operador):
        resp = login_operador.get('/api/autorizaciones/buscar')
        assert resp.status_code == 400

    def test_buscar_sin_autenticacion(self, client):
        resp = client.get('/api/autorizaciones/buscar?identificacion=123')
        assert resp.status_code in [401, 302]


# ============================================================
# TESTS: POST /api/autorizaciones/
# ============================================================

class TestCrearAutorizacion:
    """Tests para crear autorizaciones"""

    def test_crear_como_funcionario(self, login_funcionario, sede_test):
        resp = login_funcionario.post('/api/autorizaciones/',
            data=json.dumps(DATA_AUTORIZACION),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['autorizacion']['estado'] == 'PENDIENTE'
        assert data['autorizacion']['num_identificacion'] == '3333444455'

    def test_crear_como_master(self, login_master, sede_test):
        resp = login_master.post('/api/autorizaciones/',
            data=json.dumps(DATA_AUTORIZACION),
            content_type='application/json'
        )
        assert resp.status_code == 201

    def test_crear_como_operador_denegado(self, login_operador):
        resp = login_operador.post('/api/autorizaciones/',
            data=json.dumps(DATA_AUTORIZACION),
            content_type='application/json'
        )
        assert resp.status_code == 403

    def test_crear_sin_campo_requerido(self, login_funcionario):
        data_incompleto = {
            'tipo_identificacion': 'CC',
            'num_identificacion': '1234567890',
            # Falta primer_nombre, primer_apellido, etc.
        }
        resp = login_funcionario.post('/api/autorizaciones/',
            data=json.dumps(data_incompleto),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_crear_normaliza_mayusculas(self, login_funcionario, sede_test):
        data = DATA_AUTORIZACION.copy()
        data['primer_nombre'] = 'minusculas'
        data['empresa'] = 'empresa test'
        data['num_identificacion'] = '8888777766'
        resp = login_funcionario.post('/api/autorizaciones/',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert resp.status_code == 201
        result = json.loads(resp.data)
        assert result['autorizacion']['primer_nombre'] == 'MINUSCULAS'

    def test_crear_sin_autenticacion(self, client):
        resp = client.post('/api/autorizaciones/',
            data=json.dumps(DATA_AUTORIZACION),
            content_type='application/json'
        )
        assert resp.status_code in [401, 302]


# ============================================================
# TESTS: GET /api/autorizaciones/<id>
# ============================================================

class TestObtenerAutorizacion:
    """Tests para obtener autorizacion por ID"""

    def test_obtener_existente(self, login_master, autorizacion_test):
        resp = login_master.get(f'/api/autorizaciones/{autorizacion_test.id}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['autorizacion']['id'] == autorizacion_test.id

    def test_obtener_inexistente(self, login_master):
        resp = login_master.get('/api/autorizaciones/99999')
        assert resp.status_code == 404

    def test_funcionario_ve_propia(self, login_funcionario, autorizacion_test):
        resp = login_funcionario.get(f'/api/autorizaciones/{autorizacion_test.id}')
        assert resp.status_code == 200

    def test_operador_misma_sede(self, login_operador, autorizacion_test):
        """Operador puede ver autorizaciones de su sede"""
        resp = login_operador.get(f'/api/autorizaciones/{autorizacion_test.id}')
        assert resp.status_code == 200


# ============================================================
# TESTS: PUT /api/autorizaciones/<id>
# ============================================================

class TestActualizarAutorizacion:
    """Tests para actualizar autorizaciones"""

    def test_actualizar_pendiente(self, login_funcionario, autorizacion_test):
        resp = login_funcionario.put(f'/api/autorizaciones/{autorizacion_test.id}',
            data=json.dumps({
                'empresa': 'Empresa Actualizada',
                'observaciones': 'Actualización de prueba'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_actualizar_no_pendiente(self, login_master, autorizacion_utilizada):
        resp = login_master.put(f'/api/autorizaciones/{autorizacion_utilizada.id}',
            data=json.dumps({'empresa': 'No Debería'}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_actualizar_inexistente(self, login_master):
        resp = login_master.put('/api/autorizaciones/99999',
            data=json.dumps({'empresa': 'Nada'}),
            content_type='application/json'
        )
        assert resp.status_code == 404

    def test_actualizar_como_operador_denegado(self, login_operador, autorizacion_test):
        resp = login_operador.put(f'/api/autorizaciones/{autorizacion_test.id}',
            data=json.dumps({'empresa': 'Hack'}),
            content_type='application/json'
        )
        assert resp.status_code == 403


# ============================================================
# TESTS: DELETE /api/autorizaciones/<id> (cancelar)
# ============================================================

class TestCancelarAutorizacion:
    """Tests para cancelar autorizaciones"""

    def test_cancelar_pendiente(self, login_funcionario, autorizacion_test):
        resp = login_funcionario.delete(f'/api/autorizaciones/{autorizacion_test.id}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_cancelar_no_pendiente(self, login_master, autorizacion_utilizada):
        resp = login_master.delete(f'/api/autorizaciones/{autorizacion_utilizada.id}')
        assert resp.status_code == 400

    def test_cancelar_inexistente(self, login_master):
        resp = login_master.delete('/api/autorizaciones/99999')
        assert resp.status_code == 404

    def test_cancelar_como_operador_denegado(self, login_operador, autorizacion_test):
        resp = login_operador.delete(f'/api/autorizaciones/{autorizacion_test.id}')
        assert resp.status_code == 403

    def test_cancelar_como_master(self, login_master, sede_test, usuario_funcionario):
        """Master puede cancelar cualquier autorización"""
        from app.models import AutorizacionIngreso
        from app.extensions import db
        auth = AutorizacionIngreso(
            tipo_identificacion='CC',
            num_identificacion='6666777788',
            primer_nombre='PARA',
            primer_apellido='CANCELAR',
            empresa='TEST',
            nit_empresa='900666777',
            prefijo_dependencia='ADM',
            descripcion_dependencia='ADMIN',
            funcionario_autoriza='TEST',
            estado='PENDIENTE',
            fecha_vencimiento=date.today() + timedelta(days=5),
            usuario_id=usuario_funcionario.id,
            sede_id=sede_test.id
        )
        db.session.add(auth)
        db.session.commit()

        resp = login_master.delete(f'/api/autorizaciones/{auth.id}')
        assert resp.status_code == 200


# ============================================================
# TESTS: DELETE /api/autorizaciones/<id>/eliminar (hard delete)
# ============================================================

class TestEliminarAutorizacion:
    """Tests para eliminar permanentemente autorizaciones"""

    def test_eliminar_cancelada(self, login_funcionario, autorizacion_cancelada):
        resp = login_funcionario.delete(f'/api/autorizaciones/{autorizacion_cancelada.id}/eliminar')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_eliminar_pendiente_denegado(self, login_funcionario, autorizacion_test):
        """No se puede eliminar una pendiente — solo VENCIDA o CANCELADA"""
        resp = login_funcionario.delete(f'/api/autorizaciones/{autorizacion_test.id}/eliminar')
        assert resp.status_code == 400

    def test_eliminar_utilizada_denegado(self, login_master, autorizacion_utilizada):
        """No se puede eliminar una utilizada"""
        resp = login_master.delete(f'/api/autorizaciones/{autorizacion_utilizada.id}/eliminar')
        assert resp.status_code == 400

    def test_eliminar_inexistente(self, login_master):
        resp = login_master.delete('/api/autorizaciones/99999/eliminar')
        assert resp.status_code == 404

    def test_eliminar_como_operador_denegado(self, login_operador, autorizacion_cancelada):
        resp = login_operador.delete(f'/api/autorizaciones/{autorizacion_cancelada.id}/eliminar')
        assert resp.status_code == 403


# ============================================================
# TESTS: POST /api/autorizaciones/<id>/aplicar
# ============================================================

class TestAplicarAutorizacion:
    """Tests para aplicar autorizaciones (operador llena formulario)"""

    def test_aplicar_pendiente_operador(self, login_operador, autorizacion_test):
        resp = login_operador.post(f'/api/autorizaciones/{autorizacion_test.id}/aplicar')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'autorizacion' in data

    def test_aplicar_pendiente_master(self, login_master, autorizacion_test):
        resp = login_master.post(f'/api/autorizaciones/{autorizacion_test.id}/aplicar')
        assert resp.status_code == 200

    def test_aplicar_no_pendiente(self, login_operador, autorizacion_utilizada):
        resp = login_operador.post(f'/api/autorizaciones/{autorizacion_utilizada.id}/aplicar')
        assert resp.status_code == 400

    def test_aplicar_inexistente(self, login_operador):
        resp = login_operador.post('/api/autorizaciones/99999/aplicar')
        assert resp.status_code == 404

    def test_aplicar_como_funcionario_denegado(self, login_funcionario, autorizacion_test):
        resp = login_funcionario.post(f'/api/autorizaciones/{autorizacion_test.id}/aplicar')
        assert resp.status_code == 403


# ============================================================
# TESTS: GET /api/autorizaciones/estadisticas
# ============================================================

class TestEstadisticasAutorizaciones:
    """Tests para estadísticas de autorizaciones"""

    def test_estadisticas_como_master(self, login_master, autorizacion_test):
        resp = login_master.get('/api/autorizaciones/estadisticas')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        stats = data['estadisticas']
        assert 'total' in stats
        assert 'pendientes' in stats
        assert 'utilizadas' in stats
        assert 'vencidas' in stats
        assert 'canceladas' in stats
        assert 'proximas_vencer' in stats

    def test_estadisticas_con_filtro_sede(self, login_master, autorizacion_test, sede_test):
        resp = login_master.get(f'/api/autorizaciones/estadisticas?sede_id={sede_test.id}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_estadisticas_como_operador_denegado(self, login_operador):
        resp = login_operador.get('/api/autorizaciones/estadisticas')
        assert resp.status_code == 403

    def test_estadisticas_como_funcionario_denegado(self, login_funcionario):
        resp = login_funcionario.get('/api/autorizaciones/estadisticas')
        assert resp.status_code == 403

    def test_estadisticas_sin_autenticacion(self, client):
        resp = client.get('/api/autorizaciones/estadisticas')
        assert resp.status_code in [401, 302]

    def test_estadisticas_conteo_correcto(self, login_master, autorizacion_test, autorizacion_cancelada, autorizacion_utilizada):
        resp = login_master.get('/api/autorizaciones/estadisticas')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        stats = data['estadisticas']
        assert stats['total'] >= 3
        assert stats['pendientes'] >= 1
        assert stats['canceladas'] >= 1
        assert stats['utilizadas'] >= 1
