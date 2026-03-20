# Guía de Contribución
# Sistema de Control de Visitantes

¡Gracias por tu interés en contribuir al Sistema de Control de Visitantes! Esta guía te ayudará contribuir de manera efectiva.

---

## 📋 Tabla de Contenidos

1. [Código de Conducta](#código-de-conducta)
2. [Cómo Contribuir](#cómo-contribuir)
3. [Configuración del Entorno](#configuración-del-entorno)
4. [Estándares de Código](#estándares-de-código)
5. [Proceso de Pull Request](#proceso-de-pull-request)
6. [Reportar Bugs](#reportar-bugs)
7. [Solicitar Funcionalidades](#solicitar-funcionalidades)

---

## 🤝 Código de Conducta

Este proyecto adhiere a un código de conducta profesional:

- ✅ Respeto y profesionalismo en todas las interacciones
- ✅ Críticas constructivas enfocadas en el código, no en las personas
- ✅ Apertura a diferentes puntos de vista y experiencias
- ❌ Lenguaje ofensivo, acoso o discriminación

---

## 🚀 Cómo Contribuir

### Tipos de Contribución

1. **Reportar Bugs** 🐛
2. **Proponer Mejoras** 💡
3. **Escribir Documentación** 📝
4. **Corregir Código** 🔧
5. **Implementar Features** ✨
6. **Revisar Pull Requests** 👀

### Antes de Empezar

1. **Busca primero**: Verifica que tu issue no exista ya
2. **Discute grandes cambios**: Abre un issue antes de empezar
3. **Lee la documentación**: Familiarízate con el proyecto

---

## 💻 Configuración del Entorno

### Requisitos

- Python 3.11+
- PostgreSQL 15+
- Git
- Node.js 18+ (para herramientas de desarrollo)

### Instalación

```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/tu-usuario/control-visitantes.git
cd control-visitantes

# 2. Crear rama de desarrollo
git checkout -b feature/mi-nueva-funcionalidad

# 3. Configurar backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependencias de desarrollo

# 4. Configurar base de datos
createdb control_visitantes_dev
python init_db.py

# 5. Configurar .env
cp .env.example .env
# Editar .env con tus configuraciones locales

# 6. Ejecutar tests
pytest tests/ -v --cov=app

# 7. Iniciar servidor
python run.py
```

### Herramientas de Desarrollo

```bash
# Instalar herramientas adicionales
pip install black flake8 isort mypy pytest-watch

# Configurar pre-commit hooks
pip install pre-commit
pre-commit install
```

---

## 📏 Estándares de Código

### Python (Backend)

#### Style Guide: PEP 8

```python
# ✅ BIEN
def registrar_visitante(tipo_id: str, num_id: str) -> dict:
    """
    Registra un nuevo visitante en el sistema.
    
    Args:
        tipo_id: Tipo de identificación (CC, CE, TI, etc.)
        num_id: Número de identificación
        
    Returns:
        dict: Datos del visitante registrado
        
    Raises:
        ValueError: Si la identificación ya existe
    """
    visitante = Visitante.query.filter_by(
        tipo_identificacion=tipo_id,
        num_identificacion=num_id
    ).first()
    
    if visitante:
        raise ValueError("Visitante ya registrado")
    
    return visitante.to_dict()


# ❌ MAL
def regvisit(t,n):
    v=Visitante.query.filter_by(tipo_identificacion=t,num_identificacion=n).first()
    if v: raise ValueError("ya existe")
    return v.to_dict()
```

#### Formato de Código

```bash
# Formatear código con Black
black app/ tests/

# Ordenar imports con isort
isort app/ tests/

# Verificar estilo con Flake8
flake8 app/ tests/ --max-line-length=100
```

#### Convenciones de Nombres

```python
# Variables y funciones: snake_case
usuario_actual = get_usuario_actual()

# Clases: PascalCase
class UsuarioMaster:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 10

# Privadas: prefijo con _
def _funcion_interna():
    pass
```

#### Docstrings

```python
def buscar_visitante(tipo_id: str, num_id: str) -> Optional[Visitante]:
    """
    Busca un visitante por su identificación.
    
    Esta función realiza una búsqueda en la base de datos
    utilizando el tipo y número de identificación.
    
    Args:
        tipo_id (str): Tipo de identificación (CC, CE, TI, PA, NIT)
        num_id (str): Número de identificación sin puntos ni guiones
        
    Returns:
        Optional[Visitante]: Visitante encontrado o None
        
    Example:
        >>> visitante = buscar_visitante('CC', '12345678')
        >>> print(visitante.nombre_completo)
        'Juan Pérez'
    """
    return Visitante.query.filter_by(
        tipo_identificacion=tipo_id,
        num_identificacion=num_id
    ).first()
```

### JavaScript (Frontend)

#### Style Guide: Airbnb JavaScript

```javascript
// ✅ BIEN
const buscarVisitante = async (tipoId, numId) => {
  try {
    const response = await apiClient.visitantes.buscar(tipoId, numId);
    
    if (response.success && response.encontrado) {
      return response.visitante;
    }
    
    return null;
  } catch (error) {
    console.error('Error buscando visitante:', error);
    throw error;
  }
};

// ❌ MAL
function buscarVisitante(t,n){
var r=apiClient.visitantes.buscar(t,n)
if(r.success&&r.encontrado)return r.visitante
return null}
```

### SQL

```sql
-- ✅ BIEN: Nombres descriptivos, formato legible
CREATE TABLE log_visitantes (
    id SERIAL PRIMARY KEY,
    visitante_id INTEGER NOT NULL REFERENCES visitantes(id) ON DELETE CASCADE,
    fecha_hora_entrada TIMESTAMP DEFAULT NOW(),
    estado VARCHAR(50) DEFAULT 'EN_INSTALACIONES',
    
    CONSTRAINT chk_estado CHECK (estado IN ('EN_INSTALACIONES', 'SALIO'))
);

CREATE INDEX idx_log_fecha_entrada 
    ON log_visitantes(fecha_hora_entrada DESC);

-- ❌ MAL
CREATE TABLE log(id int primary key,vid int,fh timestamp,est varchar(50));
```

---

## 🔄 Proceso de Pull Request

### 1. Crear Rama

```bash
# Nombres descriptivos con prefijos
git checkout -b feature/sistema-notificaciones      # Nueva funcionalidad
git checkout -b fix/error-login-bloqueado          # Corrección de bug
git checkout -b docs/actualizar-readme             # Documentación
git checkout -b refactor/optimizar-queries         # Refactorización
```

### 2. Realizar Cambios

```bash
# Commits pequeños y descriptivos
git add .
git commit -m "feat: agregar sistema de notificaciones por email"

# Formato de commits (Conventional Commits)
# feat:     Nueva funcionalidad
# fix:      Corrección de bug
# docs:     Cambios en documentación
# style:    Formato (no afecta funcionalidad)
# refactor: Refactorización de código
# test:     Agregar o modificar tests
# chore:    Tareas de mantenimiento
```

### 3. Tests y Calidad

```bash
# Ejecutar todos los tests
pytest tests/ -v --cov=app --cov-report=term

# Verificar cobertura mínima (70%)
pytest tests/ --cov=app --cov-report=html
# Abrir: htmlcov/index.html

# Verificar estilo
flake8 app/ tests/
black app/ tests/ --check
isort app/ tests/ --check

# Type checking
mypy app/
```

### 4. Crear Pull Request

**Template de PR:**

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva funcionalidad (cambio que agrega funcionalidad)
- [ ] Breaking change (cambio que rompe compatibilidad)
- [ ] Documentación

## ¿Cómo se ha probado?
Describe los tests realizados.

## Checklist
- [ ] Mi código sigue el style guide del proyecto
- [ ] He realizado una revisión de mi código
- [ ] He comentado mi código en áreas complejas
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que prueban mi fix/feature
- [ ] Los tests nuevos y existentes pasan localmente
- [ ] He actualizado el CHANGELOG.md

## Screenshots (si aplica)
```

### 5. Code Review

Tu PR será revisado considerando:

- ✅ **Funcionalidad**: ¿Resuelve el problema?
- ✅ **Tests**: ¿Tiene tests adecuados?
- ✅ **Documentación**: ¿Está documentado?
- ✅ **Estilo**: ¿Sigue las convenciones?
- ✅ **Performance**: ¿Es eficiente?
- ✅ **Seguridad**: ¿Introduce vulnerabilidades?

---

## 🐛 Reportar Bugs

### Template de Issue

```markdown
**Descripción del Bug**
Descripción clara y concisa del bug.

**Pasos para Reproducir**
1. Ir a '...'
2. Click en '...'
3. Scroll hasta '...'
4. Ver error

**Comportamiento esperado**
Qué debería suceder.

**Comportamiento actual**
Qué sucede realmente.

**Screenshots**
Si aplica, agregar screenshots.

**Entorno:**
- OS: [Windows 10, Ubuntu 22.04, etc.]
- Navegador: [Chrome 120, Firefox 121, etc.]
- Versión del sistema: [1.0.0]
- Base de datos: [PostgreSQL 15.3]

**Logs**
```
Pegar logs relevantes aquí
```

**Contexto adicional**
Cualquier otra información relevante.
```

---

## 💡 Solicitar Funcionalidades

### Template de Feature Request

```markdown
**¿Tu feature request está relacionada con un problema?**
Describe el problema: "Estoy frustrado cuando..."

**Solución deseada**
Describe la solución que te gustaría.

**Alternativas consideradas**
Describe alternativas que consideraste.

**Impacto**
- [ ] Alta prioridad (bloquea desarrollo)
- [ ] Media prioridad (mejora significativa)
- [ ] Baja prioridad (nice to have)

**Contexto adicional**
Screenshots, mockups, diagramas, etc.
```

---

## 📝 Escribir Tests

### Estructura de Tests

```python
# tests/test_visitantes.py

def test_buscar_visitante_existente(client, db_session, visitante_prueba):
    """
    Test de búsqueda de visitante que existe en la base de datos.
    
    Given: Un visitante registrado en la base de datos
    When: Se busca por su identificación
    Then: Se debe retornar el visitante con success=True
    """
    # Arrange
    tipo_id = visitante_prueba.tipo_identificacion
    num_id = visitante_prueba.num_identificacion
    
    # Act
    response = client.get(f'/api/visitantes/buscar', query_string={
        'tipo_identificacion': tipo_id,
        'num_identificacion': num_id
    })
    
    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['encontrado'] is True
    assert data['visitante']['num_identificacion'] == num_id


def test_buscar_visitante_no_existente(client):
    """
    Test de búsqueda de visitante que no existe.
    
    Given: Una identificación no registrada
    When: Se busca por esa identificación
    Then: Se debe retornar encontrado=False
    """
    # Act
    response = client.get('/api/visitantes/buscar', query_string={
        'tipo_identificacion': 'CC',
        'num_identificacion': '99999999'
    })
    
    # Assert
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['encontrado'] is False
```

### Coverage Objetivo

- **Mínimo aceptable**: 70%
- **Target**: 80%
- **Ideal**: 90%+

```bash
# Generar reporte de coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Ver archivos con baja cobertura
pytest tests/ --cov=app --cov-report=term-missing
```

---

## 🏷️ Versionamiento

Seguimos [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (Patch: bug fixes)
1.0.1 → 1.1.0  (Minor: nueva funcionalidad, compatible)
1.1.0 → 2.0.0  (Major: breaking changes)
```

---

## 📞 Contacto

¿Preguntas? Contacta:

- **Email**: soporte@supertiendas.com
- **Issues**: GitHub Issues
- **Slack**: #control-visitantes (si aplica)

---

**¡Gracias por contribuir al Sistema de Control de Visitantes!** 🎉
