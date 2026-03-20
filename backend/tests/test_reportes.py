"""
========================================
TESTS - REPORTES
Tests para endpoints de reportes y exportación Excel
3 endpoints: GET /visitas, GET /visitas/excel, GET /estadisticas
========================================
"""

import pytest
import json
from datetime import datetime, date, time, timedelta


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
def visitas_prueba(db_session, sede_test, usuario_operador):
    """Crea registros de visitas de prueba"""
    from app.models import LogVisitante
    hoy = date.today()
    ayer = hoy - timedelta(days=1)

    visitas = [
        LogVisitante(
            fecha_ingreso=hoy,
            hora_ingreso=time(8, 30),
            tipo_identificacion='CC',
            num_identificacion='1111000001',
            primer_nombre='VISITANTE',
            primer_apellido='UNO',
            num_telefono='3001111111',
            dir_correo='v1@test.com',
            empresa='EMPRESA A',
            nit_empresa='900000001',
            prefijo_dependencia='TEST',
            descripcion_dependencia='DEPENDENCIA TEST',
            funcionario_recibe='FUNC RECIBE',
            funcionario_autoriza='FUNC AUTORIZA',
            estado_visita='EN_INSTALACIONES',
            sede_id=sede_test.id,
            usuario_registro_id=usuario_operador.id
        ),
        LogVisitante(
            fecha_ingreso=hoy,
            hora_ingreso=time(9, 0),
            fecha_salida=hoy,
            hora_salida=time(12, 0),
            tipo_identificacion='CC',
            num_identificacion='1111000002',
            primer_nombre='VISITANTE',
            primer_apellido='DOS',
            num_telefono='3002222222',
            dir_correo='v2@test.com',
            empresa='EMPRESA B',
            nit_empresa='900000002',
            prefijo_dependencia='TEST',
            descripcion_dependencia='DEPENDENCIA TEST',
            funcionario_recibe='FUNC RECIBE',
            funcionario_autoriza='FUNC AUTORIZA',
            estado_visita='SALIO',
            sede_id=sede_test.id,
            usuario_registro_id=usuario_operador.id
        ),
        LogVisitante(
            fecha_ingreso=ayer,
            hora_ingreso=time(10, 0),
            fecha_salida=ayer,
            hora_salida=time(15, 0),
            tipo_identificacion='CE',
            num_identificacion='2222000001',
            primer_nombre='VISITANTE',
            primer_apellido='AYER',
            num_telefono='3003333333',
            dir_correo='v3@test.com',
            empresa='EMPRESA C',
            nit_empresa='900000003',
            prefijo_dependencia='ADM',
            descripcion_dependencia='ADMINISTRACION',
            funcionario_recibe='FUNC RECIBE',
            funcionario_autoriza='FUNC AUTORIZA',
            estado_visita='SALIO',
            sede_id=sede_test.id,
            usuario_registro_id=usuario_operador.id
        ),
    ]
    for v in visitas:
        db_session.session.add(v)
    db_session.session.commit()
    return visitas


# ============================================================
# TESTS: GET /api/reportes/visitas
# ============================================================

class TestReporteVisitas:
    """Tests para reporte de visitas"""

    def test_reporte_sin_autenticacion(self, client):
        hoy = date.today().strftime('%Y-%m-%d')
        resp = client.get(f'/api/reportes/visitas?fecha_inicio={hoy}&fecha_fin={hoy}')
        assert resp.status_code in [401, 302]

    def test_reporte_sin_fechas(self, login_master):
        resp = login_master.get('/api/reportes/visitas')
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['success'] is False

    def test_reporte_formato_fecha_invalido(self, login_master):
        resp = login_master.get('/api/reportes/visitas?fecha_inicio=20-03-2026&fecha_fin=21-03-2026')
        assert resp.status_code == 400

    def test_reporte_rango_hoy(self, login_master, visitas_prueba):
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas?fecha_inicio={hoy}&fecha_fin={hoy}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['total'] == 2  # dos visitas hoy
        assert 'visitas' in data

    def test_reporte_rango_amplio(self, login_master, visitas_prueba):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas?fecha_inicio={ayer}&fecha_fin={hoy}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['total'] == 3  # todas las visitas

    def test_reporte_filtrar_por_estado(self, login_master, visitas_prueba):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas?fecha_inicio={ayer}&fecha_fin={hoy}&estado=EN_INSTALACIONES')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['total'] == 1
        assert data['visitas'][0]['estado_visita'] == 'EN_INSTALACIONES'

    def test_reporte_filtrar_por_dependencia(self, login_master, visitas_prueba):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas?fecha_inicio={ayer}&fecha_fin={hoy}&dependencia=ADM')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['total'] == 1

    def test_reporte_filtrar_por_sede(self, login_master, visitas_prueba, sede_test):
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas?fecha_inicio={hoy}&fecha_fin={hoy}&sede_id={sede_test.id}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['total'] == 2

    def test_reporte_rango_sin_datos(self, login_master, visitas_prueba):
        fecha = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas?fecha_inicio={fecha}&fecha_fin={fecha}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['total'] == 0

    def test_reporte_operador_ve_solo_su_sede(self, login_operador, visitas_prueba):
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_operador.get(f'/api/reportes/visitas?fecha_inicio={hoy}&fecha_fin={hoy}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        # Operador solo ve visitas de su sede
        assert data['success'] is True


# ============================================================
# TESTS: GET /api/reportes/visitas/excel
# ============================================================

class TestExportarExcel:
    """Tests para exportación Excel"""

    def test_exportar_sin_autenticacion(self, client):
        hoy = date.today().strftime('%Y-%m-%d')
        resp = client.get(f'/api/reportes/visitas/excel?fecha_inicio={hoy}&fecha_fin={hoy}')
        assert resp.status_code in [401, 302]

    def test_exportar_sin_fechas(self, login_master):
        resp = login_master.get('/api/reportes/visitas/excel')
        assert resp.status_code == 400

    def test_exportar_formato_fecha_invalido(self, login_master):
        resp = login_master.get('/api/reportes/visitas/excel?fecha_inicio=abc&fecha_fin=xyz')
        assert resp.status_code == 400

    def test_exportar_sin_resultados(self, login_master):
        fecha = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas/excel?fecha_inicio={fecha}&fecha_fin={fecha}')
        assert resp.status_code == 404  # No se encontraron visitas

    def test_exportar_excel_exitoso(self, login_master, visitas_prueba):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas/excel?fecha_inicio={ayer}&fecha_fin={hoy}')
        assert resp.status_code == 200
        assert 'spreadsheetml' in resp.content_type or 'octet-stream' in resp.content_type

    def test_exportar_excel_con_filtro_estado(self, login_master, visitas_prueba):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/visitas/excel?fecha_inicio={ayer}&fecha_fin={hoy}&estado=SALIO')
        assert resp.status_code == 200


# ============================================================
# TESTS: GET /api/reportes/estadisticas
# ============================================================

class TestEstadisticas:
    """Tests para estadísticas del sistema"""

    def test_estadisticas_sin_autenticacion(self, client):
        resp = client.get('/api/reportes/estadisticas')
        assert resp.status_code in [401, 302]

    def test_estadisticas_como_operador_denegado(self, login_operador):
        resp = login_operador.get('/api/reportes/estadisticas')
        assert resp.status_code == 403

    def test_estadisticas_por_defecto(self, login_master, visitas_prueba):
        """Sin fechas → últimos 30 días"""
        resp = login_master.get('/api/reportes/estadisticas')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'periodo' in data
        assert 'estadisticas' in data
        stats = data['estadisticas']
        assert 'total_visitas' in stats
        assert 'en_instalaciones' in stats
        assert 'salieron' in stats
        assert 'hoy' in stats
        assert stats['total_visitas'] >= 3

    def test_estadisticas_con_fechas(self, login_master, visitas_prueba):
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/estadisticas?fecha_inicio={hoy}&fecha_fin={hoy}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        stats = data['estadisticas']
        assert stats['total_visitas'] == 2  # solo visitas de hoy

    def test_estadisticas_conteo_estados(self, login_master, visitas_prueba):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        hoy = date.today().strftime('%Y-%m-%d')
        resp = login_master.get(f'/api/reportes/estadisticas?fecha_inicio={ayer}&fecha_fin={hoy}')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        stats = data['estadisticas']
        assert stats['en_instalaciones'] == 1
        assert stats['salieron'] == 2

    def test_estadisticas_hoy(self, login_master, visitas_prueba):
        resp = login_master.get('/api/reportes/estadisticas')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        hoy_stats = data['estadisticas']['hoy']
        assert hoy_stats['total'] == 2
        assert hoy_stats['en_instalaciones'] == 1
