"""
========================================
TESTS - MÓDULO SST
Tests para Seguridad y Salud en el Trabajo
33 endpoints, RBAC, CRUD, flujos de estado
========================================
"""

import pytest
import json
from datetime import date, timedelta


# ============================================================
# FIXTURES SST
# ============================================================

@pytest.fixture
def login_master(client, usuario_master):
    """Login como usuario master y devuelve client autenticado"""
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
def empresa_sst(login_master):
    """Crea una empresa contratista de prueba"""
    resp = login_master.post('/api/sst/empresas',
        data=json.dumps({
            'tipo_persona': 'JURIDICA',
            'razon_social': 'Empresa Test SST SAS',
            'nit': '900111222',
            'digito_verificacion': '3',
            'representante_legal': 'Carlos Test',
            'telefono': '3001112233',
            'email': 'empresa@test.com',
            'direccion': 'Calle Test 123',
            'ciudad': 'Cali'
        }),
        content_type='application/json'
    )
    data = json.loads(resp.data)
    return data.get('data', {})


@pytest.fixture
def empleado_sst(login_master, empresa_sst):
    """Crea un empleado contratista de prueba"""
    resp = login_master.post('/api/sst/empleados',
        data=json.dumps({
            'empresa_id': empresa_sst['id'],
            'tipo_id': 'CC',
            'num_id': '7777888899',
            'nombres': 'PEDRO',
            'apellidos': 'GONZALEZ',
            'cargo': 'Electricista'
        }),
        content_type='application/json'
    )
    data = json.loads(resp.data)
    return data.get('data', {})


@pytest.fixture
def autorizacion_sst(login_master, empresa_sst, sede_prueba):
    """Crea una autorización SST en estado borrador"""
    hoy = date.today()
    resp = login_master.post('/api/sst/autorizaciones',
        data=json.dumps({
            'empresa_id': empresa_sst['id'],
            'sede_id': sede_prueba.id,
            'labor': 'Mantenimiento eléctrico',
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': (hoy + timedelta(days=30)).isoformat()
        }),
        content_type='application/json'
    )
    data = json.loads(resp.data)
    return data.get('data', {})


# ============================================================
# TESTS: HEALTH CHECK
# ============================================================

class TestSSTHealth:

    def test_health_sin_auth(self, client):
        """SST health requiere autenticación"""
        resp = client.get('/api/sst/health')
        assert resp.status_code in (302, 401)

    def test_health_con_auth(self, login_master):
        """SST health responde OK con autenticación"""
        resp = login_master.get('/api/sst/health')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True


# ============================================================
# TESTS: EMPRESAS CONTRATISTAS
# ============================================================

class TestEmpresas:

    def test_listar_empresas_sin_auth(self, client):
        """Listar empresas requiere autenticación"""
        resp = client.get('/api/sst/empresas')
        assert resp.status_code in (302, 401)

    def test_listar_empresas(self, login_master):
        """Listar empresas devuelve lista"""
        resp = login_master.get('/api/sst/empresas')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True
        assert 'data' in data

    def test_crear_empresa_juridica(self, login_master):
        """Crear empresa jurídica exitosamente"""
        resp = login_master.post('/api/sst/empresas',
            data=json.dumps({
                'tipo_persona': 'JURIDICA',
                'razon_social': 'Nueva Empresa SAS',
                'nit': '900999111',
                'digito_verificacion': '5',
                'representante_legal': 'Rep Legal Test',
                'telefono': '3005551111'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['success'] is True
        assert data['data']['nit'] == '900999111'

    def test_crear_empresa_sin_nit(self, login_master):
        """Crear empresa jurídica sin NIT falla"""
        resp = login_master.post('/api/sst/empresas',
            data=json.dumps({
                'tipo_persona': 'JURIDICA',
                'razon_social': 'Sin NIT SAS'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_crear_empresa_natural(self, login_master):
        """Crear empresa como persona natural"""
        resp = login_master.post('/api/sst/empresas',
            data=json.dumps({
                'tipo_persona': 'NATURAL',
                'tipo_identificacion': 'CC',
                'num_identificacion': '55566677',
                'primer_nombre': 'Carlos',
                'primer_apellido': 'Perez',
                'razon_social': 'Carlos Perez',
                'nit': '55566677',
                'digito_verificacion': '0',
                'representante_legal': 'Carlos Perez'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201

    def test_obtener_empresa(self, login_master, empresa_sst):
        """Obtener empresa por ID"""
        resp = login_master.get(f"/api/sst/empresas/{empresa_sst['id']}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['data']['id'] == empresa_sst['id']

    def test_obtener_empresa_inexistente(self, login_master):
        """Obtener empresa inexistente devuelve 404"""
        resp = login_master.get('/api/sst/empresas/99999')
        assert resp.status_code == 404

    def test_actualizar_empresa(self, login_master, empresa_sst):
        """Actualizar empresa exitosamente"""
        resp = login_master.put(f"/api/sst/empresas/{empresa_sst['id']}",
            data=json.dumps({'telefono': '3009999999'}),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_buscar_empresa(self, login_master, empresa_sst):
        """Buscar empresa por término"""
        resp = login_master.get('/api/sst/empresas/buscar?q=Test+SST')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True


# ============================================================
# TESTS: EMPLEADOS CONTRATISTAS
# ============================================================

class TestEmpleados:

    def test_listar_empleados_sin_auth(self, client):
        """Listar empleados requiere autenticación"""
        resp = client.get('/api/sst/empleados')
        assert resp.status_code in (302, 401)

    def test_listar_empleados(self, login_master):
        """Listar empleados devuelve lista"""
        resp = login_master.get('/api/sst/empleados')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_crear_empleado(self, login_master, empresa_sst):
        """Crear empleado exitosamente"""
        resp = login_master.post('/api/sst/empleados',
            data=json.dumps({
                'empresa_id': empresa_sst['id'],
                'tipo_id': 'CC',
                'num_id': '1234509876',
                'nombres': 'JUAN',
                'apellidos': 'PEREZ',
                'cargo': 'Soldador'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['data']['nombres'] == 'JUAN'

    def test_crear_empleado_sin_empresa(self, login_master):
        """Crear empleado sin empresa_id falla"""
        resp = login_master.post('/api/sst/empleados',
            data=json.dumps({
                'tipo_id': 'CC',
                'num_id': '9999888877',
                'nombres': 'SIN',
                'apellidos': 'EMPRESA'
            }),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_obtener_empleado(self, login_master, empleado_sst):
        """Obtener empleado por ID"""
        resp = login_master.get(f"/api/sst/empleados/{empleado_sst['id']}")
        assert resp.status_code == 200

    def test_obtener_empleado_inexistente(self, login_master):
        """Obtener empleado inexistente"""
        resp = login_master.get('/api/sst/empleados/99999')
        assert resp.status_code == 404

    def test_actualizar_empleado(self, login_master, empleado_sst):
        """Actualizar empleado"""
        resp = login_master.put(f"/api/sst/empleados/{empleado_sst['id']}",
            data=json.dumps({'cargo': 'Técnico SST'}),
            content_type='application/json'
        )
        assert resp.status_code == 200

    def test_buscar_empleado(self, login_master, empleado_sst):
        """Buscar empleado por término"""
        resp = login_master.get('/api/sst/empleados/buscar?q=PEDRO')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True


# ============================================================
# TESTS: CERTIFICADOS
# ============================================================

class TestCertificados:

    def test_listar_certificados(self, login_master):
        """Listar certificados"""
        resp = login_master.get('/api/sst/certificados')
        assert resp.status_code == 200

    def test_crear_certificado(self, login_master, empleado_sst):
        """Crear certificado exitosamente"""
        hoy = date.today()
        resp = login_master.post('/api/sst/certificados',
            data=json.dumps({
                'empleado_id': empleado_sst['id'],
                'tipo_certificado': 'ALTURA',
                'nombre_certificado': 'Trabajo en Alturas',
                'fecha_expedicion': hoy.isoformat(),
                'fecha_vencimiento': (hoy + timedelta(days=365)).isoformat()
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_certificados_por_empleado(self, login_master, empleado_sst):
        """Obtener certificados de un empleado"""
        resp = login_master.get(f"/api/sst/certificados/empleado/{empleado_sst['id']}")
        assert resp.status_code == 200

    def test_actualizar_certificado(self, login_master, empleado_sst):
        """Crear y actualizar un certificado"""
        hoy = date.today()
        # Crear
        resp = login_master.post('/api/sst/certificados',
            data=json.dumps({
                'empleado_id': empleado_sst['id'],
                'tipo_certificado': 'ELECTRICO',
                'nombre_certificado': 'Riesgo Eléctrico',
                'fecha_expedicion': hoy.isoformat()
            }),
            content_type='application/json'
        )
        cert_id = json.loads(resp.data)['data']['id']
        # Actualizar
        resp2 = login_master.put(f'/api/sst/certificados/{cert_id}',
            data=json.dumps({'verificado': True}),
            content_type='application/json'
        )
        assert resp2.status_code == 200


# ============================================================
# TESTS: PLANILLAS SS
# ============================================================

class TestPlanillas:

    def test_listar_planillas(self, login_master):
        """Listar planillas"""
        resp = login_master.get('/api/sst/planillas')
        assert resp.status_code == 200

    def test_crear_planilla(self, login_master, empresa_sst):
        """Crear planilla exitosamente"""
        hoy = date.today()
        resp = login_master.post('/api/sst/planillas',
            data=json.dumps({
                'empresa_id': empresa_sst['id'],
                'periodo': hoy.strftime('%Y-%m'),
                'fecha_pago': hoy.isoformat(),
                'vigencia_fin': (hoy + timedelta(days=30)).isoformat()
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_obtener_planilla(self, login_master, empresa_sst):
        """Crear y obtener planilla por ID"""
        hoy = date.today()
        resp = login_master.post('/api/sst/planillas',
            data=json.dumps({
                'empresa_id': empresa_sst['id'],
                'periodo': '2025-01',
                'fecha_pago': hoy.isoformat(),
                'vigencia_fin': (hoy + timedelta(days=30)).isoformat()
            }),
            content_type='application/json'
        )
        planilla_id = json.loads(resp.data)['data']['id']
        resp2 = login_master.get(f'/api/sst/planillas/{planilla_id}')
        assert resp2.status_code == 200

    def test_planillas_por_empresa(self, login_master, empresa_sst):
        """Obtener planillas por empresa"""
        resp = login_master.get(f"/api/sst/planillas/empresa/{empresa_sst['id']}")
        assert resp.status_code == 200

    def test_planillas_vigentes(self, login_master, empresa_sst):
        """Obtener planillas vigentes por empresa"""
        resp = login_master.get(f"/api/sst/planillas/vigentes/{empresa_sst['id']}")
        assert resp.status_code == 200


# ============================================================
# TESTS: AUTORIZACIONES SST
# ============================================================

class TestAutorizaciones:

    def test_listar_autorizaciones(self, login_master):
        """Listar autorizaciones SST"""
        resp = login_master.get('/api/sst/autorizaciones')
        assert resp.status_code == 200

    def test_crear_autorizacion(self, login_master, empresa_sst, sede_prueba):
        """Crear autorización SST"""
        hoy = date.today()
        resp = login_master.post('/api/sst/autorizaciones',
            data=json.dumps({
                'empresa_id': empresa_sst['id'],
                'sede_id': sede_prueba.id,
                'labor': 'Pintura de fachada',
                'fecha_inicio': hoy.isoformat(),
                'fecha_fin': (hoy + timedelta(days=15)).isoformat()
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['data']['estado'] == 'borrador'

    def test_obtener_autorizacion(self, login_master, autorizacion_sst):
        """Obtener autorización por ID"""
        resp = login_master.get(f"/api/sst/autorizaciones/{autorizacion_sst['id']}")
        assert resp.status_code == 200

    def test_obtener_autorizacion_inexistente(self, login_master):
        """Obtener autorización inexistente"""
        resp = login_master.get('/api/sst/autorizaciones/99999')
        assert resp.status_code == 404

    def test_actualizar_autorizacion_borrador(self, login_master, autorizacion_sst):
        """Actualizar autorización en borrador"""
        resp = login_master.put(f"/api/sst/autorizaciones/{autorizacion_sst['id']}",
            data=json.dumps({'labor': 'Mantenimiento general'}),
            content_type='application/json'
        )
        assert resp.status_code == 200

    def test_enviar_revision(self, login_master, autorizacion_sst):
        """Enviar autorización a revisión"""
        resp = login_master.post(f"/api/sst/autorizaciones/{autorizacion_sst['id']}/enviar-revision")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['data']['estado'] == 'revision'

    def test_aprobar_autorizacion(self, login_master, autorizacion_sst):
        """Aprobar autorización (flujo completo borrador → revision → aprobada)"""
        aid = autorizacion_sst['id']
        # Enviar a revisión
        login_master.post(f'/api/sst/autorizaciones/{aid}/enviar-revision')
        # Aprobar
        resp = login_master.post(f'/api/sst/autorizaciones/{aid}/aprobar')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['data']['estado'] == 'aprobada'

    def test_rechazar_autorizacion(self, login_master, empresa_sst, sede_prueba):
        """Rechazar autorización en revisión"""
        hoy = date.today()
        # Crear
        resp = login_master.post('/api/sst/autorizaciones',
            data=json.dumps({
                'empresa_id': empresa_sst['id'],
                'sede_id': sede_prueba.id,
                'labor': 'Para rechazar',
                'fecha_inicio': hoy.isoformat(),
                'fecha_fin': (hoy + timedelta(days=5)).isoformat()
            }),
            content_type='application/json'
        )
        aid = json.loads(resp.data)['data']['id']
        # Enviar a revisión
        login_master.post(f'/api/sst/autorizaciones/{aid}/enviar-revision')
        # Rechazar
        resp2 = login_master.post(f'/api/sst/autorizaciones/{aid}/rechazar',
            data=json.dumps({'motivo': 'Documentos incompletos'}),
            content_type='application/json'
        )
        assert resp2.status_code == 200

    def test_anular_autorizacion(self, login_master, autorizacion_sst):
        """Anular autorización"""
        aid = autorizacion_sst['id']
        # Enviar a revisión → aprobar → anular
        login_master.post(f'/api/sst/autorizaciones/{aid}/enviar-revision')
        login_master.post(f'/api/sst/autorizaciones/{aid}/aprobar')
        resp = login_master.post(f'/api/sst/autorizaciones/{aid}/anular',
            data=json.dumps({'motivo': 'Contrato cancelado'}),
            content_type='application/json'
        )
        assert resp.status_code == 200

    def test_no_actualizar_aprobada(self, login_master, autorizacion_sst):
        """No se puede actualizar una autorización que no está en borrador"""
        aid = autorizacion_sst['id']
        login_master.post(f'/api/sst/autorizaciones/{aid}/enviar-revision')
        resp = login_master.put(f"/api/sst/autorizaciones/{aid}",
            data=json.dumps({'labor': 'Cambio ilegal'}),
            content_type='application/json'
        )
        assert resp.status_code == 400


# ============================================================
# TESTS: INGRESOS CONTRATISTAS
# ============================================================

class TestIngresos:

    def _crear_autorizacion_aprobada(self, client, empresa_sst, sede_prueba):
        """Helper: crea autorización y la aprueba"""
        hoy = date.today()
        resp = client.post('/api/sst/autorizaciones',
            data=json.dumps({
                'empresa_id': empresa_sst['id'],
                'sede_id': sede_prueba.id,
                'labor': 'Ingreso test',
                'fecha_inicio': hoy.isoformat(),
                'fecha_fin': (hoy + timedelta(days=30)).isoformat()
            }),
            content_type='application/json'
        )
        aid = json.loads(resp.data)['data']['id']
        client.post(f'/api/sst/autorizaciones/{aid}/enviar-revision')
        client.post(f'/api/sst/autorizaciones/{aid}/aprobar')
        return aid

    def test_listar_ingresos(self, login_master):
        """Listar ingresos"""
        resp = login_master.get('/api/sst/ingresos')
        assert resp.status_code == 200

    def test_listar_ingresos_activos(self, login_master):
        """Listar ingresos activos"""
        resp = login_master.get('/api/sst/ingresos/activos')
        assert resp.status_code == 200

    def test_registrar_ingreso(self, login_master, empresa_sst, empleado_sst, sede_prueba):
        """Registrar ingreso de contratista"""
        aid = self._crear_autorizacion_aprobada(login_master, empresa_sst, sede_prueba)
        resp = login_master.post('/api/sst/ingresos',
            data=json.dumps({
                'empleado_id': empleado_sst['id'],
                'autorizacion_sst_id': aid,
                'sede_id': sede_prueba.id
            }),
            content_type='application/json'
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['data']['tipo_evento'] == 'ingreso'

    def test_registrar_ingreso_campos_faltantes(self, login_master):
        """Registrar ingreso sin campos requeridos falla"""
        resp = login_master.post('/api/sst/ingresos',
            data=json.dumps({'empleado_id': 1}),
            content_type='application/json'
        )
        assert resp.status_code == 400

    def test_registrar_ingreso_autorizacion_inexistente(self, login_master, sede_prueba):
        """Registrar ingreso con autorización inexistente"""
        resp = login_master.post('/api/sst/ingresos',
            data=json.dumps({
                'empleado_id': 1,
                'autorizacion_sst_id': 99999,
                'sede_id': sede_prueba.id
            }),
            content_type='application/json'
        )
        assert resp.status_code == 404

    def test_registrar_ingreso_duplicado(self, login_master, empresa_sst, empleado_sst, sede_prueba):
        """No se puede registrar ingreso si ya tiene uno activo"""
        aid = self._crear_autorizacion_aprobada(login_master, empresa_sst, sede_prueba)
        # Primer ingreso
        login_master.post('/api/sst/ingresos',
            data=json.dumps({
                'empleado_id': empleado_sst['id'],
                'autorizacion_sst_id': aid,
                'sede_id': sede_prueba.id
            }),
            content_type='application/json'
        )
        # Segundo ingreso debe fallar
        resp = login_master.post('/api/sst/ingresos',
            data=json.dumps({
                'empleado_id': empleado_sst['id'],
                'autorizacion_sst_id': aid,
                'sede_id': sede_prueba.id
            }),
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert 'ya se encuentra' in data['message'].lower()

    def test_registrar_salida(self, login_master, empresa_sst, empleado_sst, sede_prueba):
        """Registrar salida después de ingreso"""
        aid = self._crear_autorizacion_aprobada(login_master, empresa_sst, sede_prueba)
        # Ingreso
        resp_in = login_master.post('/api/sst/ingresos',
            data=json.dumps({
                'empleado_id': empleado_sst['id'],
                'autorizacion_sst_id': aid,
                'sede_id': sede_prueba.id
            }),
            content_type='application/json'
        )
        log_id = json.loads(resp_in.data)['data']['id']
        # Salida
        resp_out = login_master.put(f'/api/sst/ingresos/{log_id}/salida',
            data=json.dumps({'observaciones': 'Salida normal'}),
            content_type='application/json'
        )
        assert resp_out.status_code == 201

    def test_registrar_salida_inexistente(self, login_master):
        """Registrar salida de log inexistente"""
        resp = login_master.put('/api/sst/ingresos/99999/salida',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert resp.status_code == 404


# ============================================================
# TESTS: OPERADORES (EPS/AFP/ARL)
# ============================================================

class TestOperadores:

    def test_listar_operadores(self, login_master):
        """Listar operadores (puede estar vacío)"""
        resp = login_master.get('/api/sst/operadores')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_listar_operadores_por_tipo(self, login_master):
        """Listar operadores filtrando por tipo"""
        for tipo in ('EPS', 'AFP', 'ARL'):
            resp = login_master.get(f'/api/sst/operadores?tipo={tipo}')
            assert resp.status_code == 200


# ============================================================
# TESTS: RBAC — Control de acceso por roles
# ============================================================

class TestRBAC:

    def test_operador_no_sst_rechazado(self, login_operador):
        """Operador normal no tiene acceso a SST"""
        resp = login_operador.get('/api/sst/empresas')
        assert resp.status_code == 403

    def test_sin_auth_rechazado(self, client):
        """Sin autenticación, todo SST rechazado"""
        endpoints = [
            '/api/sst/empresas',
            '/api/sst/empleados',
            '/api/sst/certificados',
            '/api/sst/planillas',
            '/api/sst/autorizaciones',
            '/api/sst/ingresos',
            '/api/sst/ingresos/activos',
            '/api/sst/operadores',
        ]
        for ep in endpoints:
            resp = client.get(ep)
            assert resp.status_code in (302, 401), f"{ep} debería requerir auth"
