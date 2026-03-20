# 🧪 Tests - Sistema de Control de Visitantes

## 📋 Descripción

Suite completa de tests unitarios y de integración para el sistema de control de visitantes.

## 🏗️ Estructura

```
tests/
├── __init__.py           # Configuración principal
├── conftest.py           # Fixtures de pytest
├── test_models.py        # Tests de modelos (Usuario, Visitante, etc)
├── test_auth.py          # Tests de autenticación y seguridad
└── test_api.py           # Tests de endpoints de API
```

## 🚀 Ejecutar Tests

### Todos los tests
```bash
cd backend
pytest
```

### Tests específicos
```bash
# Solo tests de modelos
pytest tests/test_models.py

# Solo tests de autenticación
pytest tests/test_auth.py

# Solo tests de API
pytest tests/test_api.py
```

### Con reporte detallado
```bash
pytest -v
```

### Con cobertura de código
```bash
pytest --cov=app --cov-report=html
```

Luego abre `htmlcov/index.html` en tu navegador.

## 📊 Cobertura de Tests

### Modelos (test_models.py)
- ✅ Usuario: Creación, password hashing, intentos fallidos, bloqueo, acceso por sede
- ✅ Sede: Creación y gestión
- ✅ Visitante: Creación y validación
- ✅ AutorizacionIngreso: Creación, uso, cancelación, vencimiento

### Autenticación (test_auth.py)
- ✅ Login exitoso y fallido
- ✅ Usuarios inexistentes
- ✅ Usuarios bloqueados
- ✅ Case insensitive
- ✅ Incremento de intentos fallidos
- ✅ Bloqueo automático
- ✅ Control de acceso por roles
- ✅ Seguridad de contraseñas (bcrypt)

### API (test_api.py)
- ✅ Health check
- ✅ Verificación de identificación
- ✅ Verificación de correo
- ✅ Flujos de integración completos
- ✅ Validación de datos únicos
- ✅ Casos extremos (edge cases)

## 🔧 Configuración

Los tests usan:
- **Base de datos en memoria** (SQLite) para no afectar la BD de producción
- **Fixtures** para crear datos de prueba automáticamente
- **Limpieza automática** después de cada test

## 📈 Métricas Esperadas

- **Cobertura de código:** ~80%+
- **Total de tests:** 45+
- **Tiempo de ejecución:** < 10 segundos

## ⚠️ Importante

- Los tests NO afectan la base de datos de producción
- Cada test corre en aislamiento (limpieza automática)
- Los tests usan SQLite en memoria por velocidad
- Para tests de integración completa, considera usar una BD de testing PostgreSQL

## 🐛 Debugging

Si un test falla:

```bash
# Ver output detallado
pytest -v -s

# Detener en el primer fallo
pytest -x

# Ver traceback completo
pytest --tb=long
```

## 📝 Agregar Nuevos Tests

Ejemplo:

```python
def test_mi_nueva_funcionalidad(client, usuario_master):
    """Test: Descripción de qué prueba"""
    # Arrange: Preparar datos
    data = {'campo': 'valor'}
    
    # Act: Ejecutar acción
    response = client.post('/api/mi-endpoint', json=data)
    
    # Assert: Verificar resultado
    assert response.status_code == 200
    assert response.json['success'] is True
```

## 🎯 Próximos Tests a Agregar

- [ ] Tests de reportes Excel
- [ ] Tests de envío de emails
- [ ] Tests de limpieza de fotos
- [ ] Tests de rate limiting
- [ ] Tests de CORS
- [ ] Tests de performance

## 📚 Documentación

- [Pytest](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
