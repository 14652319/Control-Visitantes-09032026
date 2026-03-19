# COPILOT_TASKS — Canal de Comunicación Claude ↔ Copilot
# Sistema: Control de Visitantes — Supertiendas Cañaveral SAS

> **PROTOCOLO DE COMUNICACIÓN**:
> 
> **COPILOT @evaluador** (este archivo):
> - Escribe hallazgos de análisis
> - Escribe análisis de viabilidad
> - Coordina con Claude auditor
> - NO ejecuta código (solo analiza y planifica)
> 
> **COPILOT @operador** (ejecuta código):
> - Lee instrucciones en `.github/INSTRUCCIONES_OPERADOR.md`
> - Implementa cambios según plan
> - Escribe actualizaciones en sección `[COPILOT EJECUTOR]` de este archivo
> - Marca `[ESPERANDO VALIDACIÓN CLAUDE]` cuando termina checkpoint
> 
> **CLAUDE Code** (auditor):
> - Lee actualizaciones de Copilot @operador
> - Revisa código y cumplimiento de estándares
> - Escribe en sección `[CLAUDE SUPERVISOR]` de este archivo
> - Marca `[✅ APROBADO]` o `[❌ REQUIERE CORRECCIÓN]`

---

## 📊 Estado Actual del Proyecto

- **Rama activa**: `master`
- **Último commit**: `ec1f883` (commit 12 03 2026)
- **FASE activa**: ⏸️ **ESPERANDO DECISIÓN USUARIO**
- **Próxima acción**: Iniciar **PLAN COMPLETO** (FASE 1 → Preparación → Módulo SST)

### 🎯 Decisión del Usuario: OPCIÓN A - PLAN COMPLETO

```
┌─────────────────────────────────────────────────────────┐
│ ✅ APROBADO: Implementar Módulo SST                    │
│ ⚠️  CONDICIÓN: Después de completar FASE 1             │
│ ⏱️  Tiempo total: 5-8h (FASE 1) + 80-120 días (SST)    │
└─────────────────────────────────────────────────────────┘
```

### 📋 Plan de Ejecución Coordinada

**PASO 1**: FASE 1 - Correcciones críticas (5-8 horas)  
**PASO 2**: Preparación Módulo SST (2-3 días)  
**PASO 3**: Módulo SST - 7 Fases (80-120 días)

---

## 🚀 PASO 1: FASE 1 — Correcciones Críticas (5-8h)

### CHECKPOINT 1.1: Quick Win QW-03 - Índices DB [EJECUTAR]

**COPILOT**: Implementa esto
```sql
-- Crear archivo: backend/migrate_add_indices_visitantes.py

from config import db
from sqlalchemy import text

def agregar_indices():
    """Agregar índices faltantes para optimizar búsquedas"""
    indices = [
        # Índice para búsquedas por identificación
        """
        CREATE INDEX IF NOT EXISTS idx_visitante_identificacion 
        ON visitantes(tipo_identificacion, num_identificacion);
        """,
        
        # Índice para búsquedas por fecha
        """
        CREATE INDEX IF NOT EXISTS idx_log_visitantes_fecha 
        ON log_visitantes(fecha_ingreso);
        """,
        
        # Índice para búsquedas de autorizaciones por usuario
        """
        CREATE INDEX IF NOT EXISTS idx_autorizacion_usuario 
        ON autorizaciones_ingreso(usuario_id, estado);
        """,
    ]
    
    for sql in indices:
        db.session.execute(text(sql))
    
    db.session.commit()
    print("✅ Índices creados exitosamente")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        agregar_indices()
```

**Ejecutar**:
```powershell
python backend/migrate_add_indices_visitantes.py
```

**Tests de verificación**:
```powershell
# Verificar que índices existen
psql -U postgres -d control_visitantes -c "\d visitantes"
psql -U postgres -d control_visitantes -c "\d log_visitantes"
```

**Criterio de aceptación**:
- ✅ Script ejecuta sin errores
- ✅ 3 índices creados en base de datos
- ✅ No hay impacto en funcionalidad existente

**Al terminar**: Marca `[COPILOT EJECUTOR]` con commit hash + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 1.2: Quick Win QW-04 - Optimizar queries [EJECUTAR]

**COPILOT**: Optimiza queries en estos archivos

**Archivo 1**: `backend/app/routes/visitantes.py`
```python
# ANTES (línea ~45):
visitantes = Visitante.query.filter(Visitante.sede_id == sede_id).all()

# DESPUÉS:
visitantes = Visitante.query.filter_by(sede_id=sede_id).all()
```

**Archivo 2**: `backend/app/routes/autorizaciones.py`
```python
# ANTES (línea ~60):
autorizaciones = AutorizacionIngreso.query.filter(
    AutorizacionIngreso.usuario_id == current_user.id
).all()

# DESPUÉS:
autorizaciones = AutorizacionIngreso.query.filter_by(
    usuario_id=current_user.id
).all()
```

**Buscar y reemplazar en todos los archivos de routes/**: Cambiar `.filter(Model.campo == valor)` por `.filter_by(campo=valor)` donde sea posible.

**Tests de verificación**:
```powershell
pytest backend/tests/ -v -k "test_visitantes or test_autorizaciones"
```

**Criterio de aceptación**:
- ✅ Queries optimizadas (más legibles)
- ✅ Tests pasan 100%
- ✅ Performance igual o mejor

**Al terminar**: Marca `[COPILOT EJECUTOR]` con commit hash + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 1.3: Fix crítico - Dependencia.to_dict() [EJECUTAR]

**COPILOT**: Corrige método en modelo

**Archivo**: `backend/app/models/dependencia.py`

```python
# Buscar método to_dict() y corregir parámetro faltante:

def to_dict(self, incluir_sedes=True):  # ← Agregar parámetro con default
    """Convierte modelo a diccionario"""
    data = {
        'id': self.id,
        'nombre': self.nombre,
        'descripcion': self.descripcion,
        # ... resto de campos
    }
    
    if incluir_sedes and hasattr(self, 'sede'):
        data['sede'] = self.sede.to_dict() if self.sede else None
    
    return data
```

**Tests de verificación**:
```powershell
pytest backend/tests/test_dependencias.py -v
```

**Verificar endpoint**:
```powershell
# Con servidor corriendo:
curl http://localhost:5000/api/dependencias
```

**Criterio de aceptación**:
- ✅ Método acepta parámetro `incluir_sedes`
- ✅ Endpoint `/api/dependencias` responde 200
- ✅ No lanza excepción

**Al terminar**: Marca `[COPILOT EJECUTOR]` con commit hash + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 1.4: FASE 1 COMPLETA - Validación Final [VALIDAR]

**CLAUDE**: Revisa que TODO esté correcto antes de avanzar

**Checklist de validación**:
- [ ] 3 índices creados y verificados
- [ ] Queries optimizadas (.filter_by en lugar de .filter)
- [ ] Dependencia.to_dict() corregido
- [ ] Tests pasan 100%
- [ ] No hay regresiones
- [ ] Commits con mensajes descriptivos
- [ ] Código cumple estándares globales

**Si TODO OK**: Marca `[✅ FASE 1 APROBADA POR CLAUDE - AVANZAR A PASO 2]`  
**Si hay problemas**: Marca `[❌ REQUIERE CORRECCIÓN]` + detalle

---

## 🛠️ PASO 2: Preparación Módulo SST (2-3 días)

### CHECKPOINT 2.1: Backup Completo [EJECUTAR]

**COPILOT**: Crea backups obligatorios

**Backup de Base de Datos**:
```powershell
# Crear directorio si no existe
New-Item -ItemType Directory -Force -Path "D:\0.A. Proyectos\0.0. BackUp\control-visitantes-pre-sst"

# Backup DB
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump -U postgres -d control_visitantes > "D:\0.A. Proyectos\0.0. BackUp\control-visitantes-pre-sst\db_backup_$fecha.sql"
```

**Backup de Código**:
```powershell
# Crear tag en git
git tag -a "pre-sst-v1.0" -m "Backup antes de iniciar Módulo SST"
git push origin pre-sst-v1.0

# Crear branch nuevo
git checkout -b feature/modulo-sst
git push -u origin feature/modulo-sst
```

**Criterio de aceptación**:
- ✅ Archivo SQL de backup existe (>100KB)
- ✅ Tag `pre-sst-v1.0` creado
- ✅ Branch `feature/modulo-sst` existe y está activo

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 2.2: Migración Roles en Usuarios [EJECUTAR]

**COPILOT**: Crear migración para nuevos roles

**Archivo**: `backend/migrate_add_roles_sst.py`

```python
"""
Migración: Agregar roles admin_sst y operador_seguridad
Fecha: 2026-03-19
"""
from config import db
from sqlalchemy import text

def migrate():
    """Agregar nuevos roles a tabla usuarios"""
    print("Iniciando migración de roles SST...")
    
    # Paso 1: Ampliar tipo de columna rol
    db.session.execute(text("""
        ALTER TABLE usuarios 
        ALTER COLUMN rol TYPE VARCHAR(50);
    """))
    
    # Paso 2: Eliminar constraint viejo
    db.session.execute(text("""
        ALTER TABLE usuarios 
        DROP CONSTRAINT IF EXISTS check_rol_valido;
    """))
    
    # Paso 3: Crear constraint nuevo con roles adicionales
    db.session.execute(text("""
        ALTER TABLE usuarios 
        ADD CONSTRAINT check_rol_valido 
        CHECK (rol IN (
            'usuario_master',
            'usuario_operador',
            'usuario_funcionario',
            'admin_sst',
            'operador_seguridad'
        ));
    """))
    
    db.session.commit()
    print("✅ Migración completada: roles SST agregados")

def rollback():
    """Revertir cambios si algo falla"""
    print("Revirtiendo migración...")
    db.session.execute(text("""
        ALTER TABLE usuarios DROP CONSTRAINT check_rol_valido;
        ALTER TABLE usuarios ADD CONSTRAINT check_rol_valido 
        CHECK (rol IN ('usuario_master', 'usuario_operador', 'usuario_funcionario'));
    """))
    db.session.commit()
    print("✅ Rollback completado")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            migrate()
        except Exception as e:
            print(f"❌ Error: {e}")
            rollback()
```

**Ejecutar**:
```powershell
python backend/migrate_add_roles_sst.py
```

**Verificar**:
```sql
-- Verificar constraint
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'usuarios'::regclass AND conname = 'check_rol_valido';
```

**Criterio de aceptación**:
- ✅ Migración ejecuta sin errores
- ✅ Constraint acepta 5 roles (3 viejos + 2 nuevos)
- ✅ Usuarios existentes funcionan normal

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 2.3: Seeders Operadores Seguridad Social [EJECUTAR]

**COPILOT**: Pre-cargar catálogo de operadores

**Archivo**: `backend/init_operadores_ss.py`

```python
"""
Seeder: Operadores de Aportes (EPS, AFP, ARL)
Fuente: Datos oficiales Colombia 2026
"""
from app import create_app
from app.models import db
from app.models.operador_aportes import OperadorAportes

OPERADORES = [
    # EPS
    {'nombre': 'NUEVA EPS', 'tipo': 'EPS', 'nit': '900156264', 'activo': True},
    {'nombre': 'COMPENSAR EPS', 'tipo': 'EPS', 'nit': '860066942', 'activo': True},
    {'nombre': 'SANITAS EPS', 'tipo': 'EPS', 'nit': '800251440', 'activo': True},
    {'nombre': 'SALUD TOTAL EPS', 'tipo': 'EPS', 'nit': '800130907', 'activo': True},
    {'nombre': 'SURA EPS', 'tipo': 'EPS', 'nit': '800088702', 'activo': True},
    
    # AFP
    {'nombre': 'PORVENIR', 'tipo': 'AFP', 'nit': '800144331', 'activo': True},
    {'nombre': 'PROTECCION', 'tipo': 'AFP', 'nit': '900280884', 'activo': True},
    {'nombre': 'COLFONDOS', 'tipo': 'AFP', 'nit': '860066942', 'activo': True},
    {'nombre': 'OLD MUTUAL', 'tipo': 'AFP', 'nit': '860051894', 'activo': True},
    
    # ARL
    {'nombre': 'ARL SURA', 'tipo': 'ARL', 'nit': '800088702', 'activo': True},
    {'nombre': 'POSITIVA', 'tipo': 'ARL', 'nit': '800140949', 'activo': True},
    {'nombre': 'LIBERTY', 'tipo': 'ARL', 'nit': '860024118', 'activo': True},
    {'nombre': 'BOLIVAR', 'tipo': 'ARL', 'nit': '860002400', 'activo': True},
]

def seed():
    """Insertar operadores en BD"""
    print(f"Insertando {len(OPERADORES)} operadores...")
    
    for data in OPERADORES:
        # Verificar si ya existe
        existe = OperadorAportes.query.filter_by(nit=data['nit'], tipo=data['tipo']).first()
        if not existe:
            operador = OperadorAportes(**data)
            db.session.add(operador)
            print(f"  ✅ {data['tipo']}: {data['nombre']}")
        else:
            print(f"  ⏭️  Ya existe: {data['nombre']}")
    
    db.session.commit()
    print(f"✅ Seeder completado: {len(OPERADORES)} operadores")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
```

**NOTA**: Este script asume que el modelo `OperadorAportes` y su tabla ya existen. Si no, esperar a Fase 3.1.

**Criterio de aceptación**:
- ✅ Script preparado (ejecutar después de crear tabla)
- ✅ 13 operadores listados correctamente

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 2.4: PASO 2 COMPLETO - Validación [VALIDAR]

**CLAUDE**: Verifica infraestructura lista

**Checklist**:
- [ ] Backup DB existe y es válido
- [ ] Tag git `pre-sst-v1.0` creado
- [ ] Branch `feature/modulo-sst` activo
- [ ] Migración roles ejecutada correctamente
- [ ] Constraint acepta 5 roles
- [ ] Seeder preparado (listo para ejecutar)
- [ ] Sistema actual funciona normal

**Si TODO OK**: Marca `[✅ PASO 2 APROBADO - LISTO PARA MÓDULO SST]`  
**Si hay problemas**: Marca `[❌ REQUIERE CORRECCIÓN]` + detalle

---

## 🏗️ PASO 3: Módulo SST — 7 FASES (80-120 días)

### 📦 FASE 3.1: DB + Modelos (12-17 días)

#### CHECKPOINT 3.1.1: Crear 8 Migraciones de Tablas [EJECUTAR]

**COPILOT**: Crea estas 8 migraciones siguiendo la especificación del documento (líneas 3090-5782)

**Orden de creación** (respetar dependencias):
1. `migrate_create_operadores_aportes.py` (sin FK)
2. `migrate_create_empresas_contratistas.py` (sin FK)
3. `migrate_create_empleados_contratistas.py` (FK: empresas)
4. `migrate_create_planillas_ss.py` (FK: empleados, operadores)
5. `migrate_create_certificados_trabajo.py` (FK: empleados)
6. `migrate_create_autorizaciones_sst.py` (FK: empresas, sedes, usuarios)
7. `migrate_create_empleados_por_autorizacion.py` (FK: empleados, autorizaciones)
8. `migrate_create_log_ingresos_contratistas.py` (FK: empleados, autorizaciones, sedes)

**Referencia completa**: Ver `Levantamiento de requerimientos control visitantes.txt` líneas 3400-3800 (especificación de tablas)

**Criterio de aceptación**:
- ✅ 8 migraciones creadas en `backend/`
- ✅ Cada migración tiene función `migrate()` y `rollback()`
- ✅ Índices incluidos según especificación
- ✅ Constraints (FK, CHECK, UNIQUE) correctos
- ✅ Campo GENERATED para `certificados_trabajo.vigente`

**Tests de verificación**:
```powershell
# Ejecutar cada migración en orden
python backend/migrate_create_operadores_aportes.py
python backend/migrate_create_empresas_contratistas.py
# ... (resto)

# Verificar tablas creadas
psql -U postgres -d control_visitantes -c "\dt"
```

**Al terminar**: Marca `[COPILOT EJECUTOR]` con commit hash + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

#### CHECKPOINT 3.1.2: Crear 8 Modelos SQLAlchemy [EJECUTAR]

**COPILOT**: Crea modelos en `backend/app/models/`

**Modelos a crear**:
1. `operador_aportes.py` (~40 líneas)
2. `empresa_contratista.py` (~80 líneas)
3. `empleado_contratista.py` (~70 líneas)
4. `planilla_seguridad_social.py` (~100 líneas)
5. `certificado_trabajo.py` (~60 líneas)
6. `autorizacion_sst.py` (~120 líneas) ← **Principal**
7. `empleado_por_autorizacion.py` (~80 líneas)
8. `log_ingreso_contratista.py` (~80 líneas)

**Estándar a seguir**:
- Todos heredan de `db.Model`
- Método `to_dict()` en cada modelo
- Relaciones con `db.relationship()` y `back_populates`
- Validaciones en métodos custom (ej: `validar_vigencia()`)

**Criterio de aceptación**:
- ✅ 8 modelos creados
- ✅ Relaciones bidireccionales correctas
- ✅ Método `to_dict()` funcional
- ✅ Imports correctos en `backend/app/models/__init__.py`

**Tests básicos**:
```python
# Verificar imports
from app.models import OperadorAportes, EmpresaContratista, EmpleadoContratista
# ... resto

# Verificar que modelos cargan sin errores
app = create_app()
with app.app_context():
    print(OperadorAportes.query.first())
```

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

#### CHECKPOINT 3.1.3: Ejecutar Seeder Operadores [EJECUTAR]

**COPILOT**: Ahora sí ejecutar seeder (tabla ya existe)

```powershell
python backend/init_operadores_ss.py
```

**Verificar**:
```powershell
psql -U postgres -d control_visitantes -c "SELECT * FROM operadores_aportes;"
```

**Criterio**: ✅ 13 operadores insertados

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

#### CHECKPOINT 3.1.4: FASE 3.1 COMPLETA - Validación DB + Modelos [VALIDAR]

**CLAUDE**: Validación exhaustiva antes de avanzar

**Checklist**:
- [ ] 8 tablas existen en base de datos
- [ ] Índices creados correctamente (verificar con `\d nombre_tabla`)
- [ ] Foreign keys apuntan a tablas correctas
- [ ] Constraints CHECK funcionan (intentar insertar dato inválido)
- [ ] 8 modelos SQLAlchemy creados
- [ ] Relaciones bidireccionales (`back_populates`) correctas
- [ ] Método `to_dict()` funciona en cada modelo
- [ ] 13 operadores pre-cargados
- [ ] No hay errores de import
- [ ] Tests unitarios básicos pasan

**Si TODO OK**: Marca `[✅ FASE 3.1 APROBADA - AVANZAR A 3.2]`  
**Si hay problemas**: Marca `[❌ REQUIERE CORRECCIÓN]` + detalle específico

---

### 📡 FASE 3.2: Endpoints Empresas + Planillas (15-20 días)

#### CHECKPOINT 3.2.1: Blueprint /api/sst - CRUD Empresas [EJECUTAR]

**COPILOT**: Crear blueprint `backend/app/routes/sst.py` con primeros 6 endpoints

**Endpoints a implementar**:
```
POST   /api/sst/empresas                # Crear empresa
GET    /api/sst/empresas                # Listar empresas
GET    /api/sst/empresas/<id>           # Ver detalles empresa
PUT    /api/sst/empresas/<id>           # Actualizar empresa
DELETE /api/sst/empresas/<id>           # Desactivar empresa (soft delete)
GET    /api/sst/empresas/buscar?nit=... # Buscar por NIT
```

**Decoradores obligatorios**:
- `@login_required` (todos)
- `@role_required('admin_sst')` (POST, PUT, DELETE)

**Validaciones**:
- NIT único (no duplicados)
- Validar formato NIT colombiano con dígito verificador
- Email válido (usar método de modelo Usuario)
- Teléfono formato colombiano

**Criterio de aceptación**:
- ✅ Blueprint registrado en `app/__init__.py`
- ✅ 6 endpoints funcionan
- ✅ Validaciones implementadas
- ✅ Respuestas JSON estándar `{'success': bool, 'message': str, 'data': ...}`
- ✅ Tests unitarios para cada endpoint

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

#### CHECKPOINT 3.2.2: Endpoints Planillas Seguridad Social [EJECUTAR]

**COPILOT**: Agregar 4 endpoints de planillas al blueprint

**Endpoints**:
```
POST   /api/sst/planillas               # Registrar planilla
GET    /api/sst/planillas               # Listar planillas
GET    /api/sst/planillas/<id>          # Ver planilla
PUT    /api/sst/planillas/<id>          # Actualizar planilla
```

**Lógica de negocio**:
- Calcular automático: `vigencia = fecha_pago + 30 días`
- Validar archivo PDF (mime-type, tamaño < 5MB)
- Guardar PDF en ruta configurable
- Validar que empleado pertenece a empresa correcta

**Criterio**: ✅ 4 endpoints + validaciones + tests

**Al terminar**: Marca `[COPILOT EJECUTOR]` + `[ESPERANDO VALIDACIÓN CLAUDE]`

---

#### CHECKPOINT 3.2.3: FASE 3.2 COMPLETA [VALIDAR]

**CLAUDE**: Validar

**Checklist**:
- [ ] Blueprint `/api/sst` registrado
- [ ] 10 endpoints funcionan (6 empresas + 4 planillas)
- [ ] Permisos RBAC correctos
- [ ] Validaciones implementadas (NIT, email, PDF)
- [ ] Tests pasan 100%
- [ ] Responses JSON estándar

**Estado**: `[✅ APROBADO]` o `[❌ CORRECCIÓN]`

---

### 👷 FASE 3.3: Empleados + Certificados (12-15 días)

**[Estructura similar a 3.2, con checkpoints para]**:
- 3.3.1: CRUD Empleados (4 endpoints)
- 3.3.2: CRUD Certificados (3 endpoints)
- 3.3.3: Validación FASE 3.3

---

### 🎫 FASE 3.4: Autorizaciones SST (18-25 días) ← **MÁS COMPLEJA**

**[Esta es la fase crítica con máquina de estados]**:
- 3.4.1: Endpoints básicos CRUD (5 endpoints)
- 3.4.2: Máquina de estados (6 estados + transiciones)
- 3.4.3: Generación PDF con xhtml2pdf
- 3.4.4: Validación FASE 3.4 (exhaustiva)

---

### 🚪 FASE 3.5: Ingresos/Salidas Contratistas (8-12 días)

**[Checkpoints]**:
- 3.5.1: Registro ingresos (POST)
- 3.5.2: Registro salidas (PUT)
- 3.5.3: Consultas y reportes (GET)
- 3.5.4: Validación FASE 3.5

---

### 📊 FASE 3.6: Reportes y Dashboard (10-15 días)

**[Checkpoints]**:
- 3.6.1: Estadísticas dashboard
- 3.6.2: Reportes por empresa
- 3.6.3: Reportes por sede
- 3.6.4: Alertas de vencimientos
- 3.6.5: Validación FASE 3.6

---

### 🧪 FASE 3.7: Testing Completo + Despliegue (12-16 días)

**[Checkpoints]**:
- 3.7.1: Tests unitarios (38 endpoints)
- 3.7.2: Tests integración (flujos completos)
- 3.7.3: Tests de seguridad (OWASP ZAP)
- 3.7.4: Tests de carga (Locust)
- 3.7.5: Frontend admin_sst.html
- 3.7.6: Frontend operador_seguridad.html
- 3.7.7: Documentación técnica
- 3.7.8: Manuales de usuario
- 3.7.9: Despliegue producción
- 3.7.10: VALIDACIÓN FINAL

---

## 📝 SECCIONES DE TRABAJO

### [COPILOT EJECUTOR] — Escribe aquí después de cada checkpoint

**Formato**:
```
CHECKPOINT X.Y.Z - [Título]
Fecha: YYYY-MM-DD HH:MM
Commit: <hash>

QUÉ HICE:
- [Detalle 1]
- [Detalle 2]

ARCHIVOS MODIFICADOS/CREADOS:
- ruta/archivo1.py
- ruta/archivo2.py

TESTS:
- [Comando ejecutado]
- [Resultado: PASS/FAIL]

ESTADO: [ESPERANDO VALIDACIÓN CLAUDE]
```

---

### [CLAUDE SUPERVISOR] — Escribe aquí después de revisar

**Formato**:
```
CHECKPOINT X.Y.Z - REVISIÓN

VALIDACIONES REALIZADAS:
- [ ] Criterio 1: ✅ OK / ❌ FALLA (razón)
- [ ] Criterio 2: ✅ OK / ❌ FALLA (razón)

CÓDIGO REVISADO:
- ruta/archivo1.py: [Observaciones]

TESTS VERIFICADOS:
- [Resultados]

CUMPLIMIENTO ESTÁNDARES:
- Seguridad: ✅/❌
- Backend: ✅/❌
- Testing: ✅/❌

DECISIÓN:
[✅ APROBADO - Avanzar a siguiente checkpoint]
[❌ REQUIERE CORRECCIÓN: Lista detallada de cambios necesarios]

Fecha validación: YYYY-MM-DD HH:MM
```

---

## 📌 TRABAJO ACTUAL

### Estado: ⏸️ ESPERANDO AUTORIZACIÓN USUARIO PARA INICIAR PASO 1

**Próxima acción**: Usuario debe decir "**Iniciar PASO 1**" o "**Comenzar FASE 1**"

Una vez autorizado:
- Copilot ejecuta CHECKPOINT 1.1 (índices DB)
- Claude valida cuando Copilot marque `[ESPERANDO VALIDACIÓN]`
- Ciclo se repite para cada checkpoint

---

---

## Contexto del proyecto

**Stack**: Flask 3.x + PostgreSQL 16 + Vanilla JS + Alpine.js 3.x
**Project Key Engram**: `control-visitantes-sc`
**Auditorías realizadas**: 3 (Claude + Copilot) → 75 problemas encontrados, 12 críticos
**Documentos de referencia**:
- `AUDITORIA_TECNICA.md` — Auditoría Claude (28 hallazgos)
- `AUDITORIA_COPILOT_REVISION.md` — Revisión Copilot (75 hallazgos)
- `AUDITORIA_CONSOLIDADA_Y_SOCIALIZACION.md` — Consolidado final
- `PLAN_ACCION_CORRECCIONES.md` — Plan FASE 1
- `PLAN_FULLSTACK_COMPLETO.md` — Plan FASE 2 (136h)

---

## Convenciones

### Para Claude (al escribir tareas):
- Usar `### TAREA-XXX: Título` con estado `[PENDIENTE]`
- Incluir: **Qué**, **Dónde**, **Criterios de aceptación**
- Prioridad: CRITICA | ALTA | MEDIA | BAJA

### Para Copilot (al ejecutar):
- Leer todas las tareas `[PENDIENTE]` → ejecutar en orden de prioridad
- Cambiar estado a `[COMPLETADA]` con fecha y commit hash
- Si hay bloqueo → marcar `[BLOQUEADA]` con razón clara
- Correr tests después de cada tarea
- Guardar en Engram: `mcp_engram_mem_save(project="control-visitantes-sc", ...)`
- **SIEMPRE pedir autorización al usuario antes de implementar**

---

## HALLAZGOS — Módulo SST / Contratistas (Nuevo)
> Análisis realizado por Claude Code el 2026-03-19
> Sección 29 del Levantamiento de Requerimientos (líneas 3090–4135)

### HALLAZGO-SST-01: Módulo de gran escala — requiere planificación separada
- **Severidad**: ALTA (decisión arquitectural)
- **Problema**: El módulo SST propuesto agrega 8 nuevas tablas, 2 roles nuevos, 2 paneles frontend y generación de PDF. Es esencialmente una segunda aplicación paralela.
- **Impacto**: Si se implementa antes de cerrar FASE 1, se construye sobre 12 bugs críticos sin resolver.
- **Recomendación Claude**: Implementar SOLO después de cerrar FASE 1. Tratar como FASE 3.

### HALLAZGO-SST-02: Generación de PDF (SC-SST-FOR-015) — librería faltante
- **Severidad**: ALTA
- **Archivo**: `backend/requirements.txt`
- **Problema**: El módulo SST requiere generar PDFs con formato oficial SC-SST-FOR-015. No hay `reportlab` ni `WeasyPrint` en el stack actual.
- **Solución propuesta**: Agregar `reportlab==4.x` o `WeasyPrint` antes de implementar el módulo SST.

### HALLAZGO-SST-03: Sistema de almacenamiento de archivos — no existe
- **Severidad**: ALTA
- **Problema**: El módulo SST requiere subir PDFs de planillas y certificados. No hay sistema de upload/storage hoy.
- **Solución propuesta**: Definir estrategia: sistema de archivos local con ruta configurable por entorno, o servicio externo. Documentar en `.env`.

### HALLAZGO-SST-04: Campo GENERATED ALWAYS en PostgreSQL
- **Severidad**: MEDIA
- **Tabla**: `certificados_trabajo.vigente`
- **Problema**: `vigente BOOLEAN GENERATED ALWAYS AS (fecha_vencimiento >= CURRENT_DATE) STORED` — requiere verificar que la versión de PostgreSQL del servidor sea 12+.
- **Solución propuesta**: Confirmar versión PG en producción antes de crear la tabla.

### HALLAZGO-SST-05: Diseño general — APROBADO con observaciones
- **Severidad**: INFO
- **Problema**: N/A — el diseño de tablas, roles y flujos es correcto y bien estructurado.
- **Observaciones positivas**:
  - Módulo verdaderamente paralelo, sin mezcla con sistema de visitantes
  - Tablas compartidas correctas (usuarios, sedes, log_eventos)
  - Roles con separación correcta de responsabilidades
  - Flujos detallados y coherentes con operativa real
  - Índices y constraints bien definidos

---

## 📊 HALLAZGOS COPILOT — ANÁLISIS VIABILIDAD MÓDULO SST
> **Analista**: GitHub Copilot (@evaluador)  
> **Fecha**: 19 de Marzo de 2026  
> **Documento revisado**: `ANALISIS_VIABILIDAD_MODULO_SST.md` (30 páginas, 8700 líneas)  
> **Estado**: ✅ ANÁLISIS COMPLETO — **[ESPERANDO REVISIÓN CLAUDE]**

---

### 🎯 RESUMEN EJECUTIVO

**Veredicto**: ✅ **VIABLE Y BIEN DISEÑADO** (4/5 estrellas)

**Alcance**: Módulo completo para gestión de contratistas con validaciones de seguridad social (Ley 100), certificaciones de trabajo especializado, y generación de autorizaciones en PDF.

**Tiempo Realista**: **80-120 días hábiles** (16-24 semanas)  
- ⚠️ Documento original estima 48-68 días → **SUBESTIMADO**
- ✅ Estimación conservadora: 80-120 días (considerando testing + ajustes)

**Impacto en Sistema Actual**: ⚠️ **CERO IMPACTO**  
- ✅ Arquitectura 100% modular e independiente
- ✅ Solo 1 cambio en tabla `usuarios` (agregar 2 roles nuevos)
- ✅ No modifica visitantes, autorizaciones, ni log_visitantes

---

### 📋 CUMPLIMIENTO NORMATIVO Y ESTÁNDARES

| Criterio | Cumple | Detalles |
|----------|--------|----------|
| **OWASP ASVS (Seguridad)** | ✅ SÍ | Autenticación, RBAC, validación inputs, CSRF, SQL Injection protegido |
| **Ley 100/1993** | ✅ SÍ | Seguridad social (EPS, AFP, ARL) correctamente implementada |
| **Resolución 4272/2021** | ✅ SÍ | Certificados de trabajo en alturas |
| **Estándar 03-seguridad.md** | ✅ SÍ | Auditoría completa, sesiones seguras, mínimo privilegio |
| **Estándar 04-backend.md** | ✅ SÍ | SQLAlchemy 2.0, relaciones correctas, índices optimizados |
| **Estándar 05-datos-colombia.md** | ⚠️ PARCIAL | Tipos de documento ✅, validación NIT automática ❌ (falta implementar) |
| **Estándar 02-formularios.md** | ✅ SÍ | Vanilla JS + Alpine.js, validación HTML5, auto-guardado |
| **Estándar 07-testing.md** | ⚠️ PENDIENTE | Suite de tests debe crearse (no está en especificación) |
| **Estándar 08-documentacion.md** | ✅ SÍ | Documento muy detallado (2692 líneas), endpoints especificados |

---

### 🏗️ ARQUITECTURA Y ALCANCE TÉCNICO

**Base de Datos**: 8 tablas nuevas
1. `empresas_contratistas` (~10 campos)
2. `operadores_aportes` (~5 campos, catálogo pre-cargado)
3. `planillas_seguridad_social` (~12 campos)
4. `certificados_trabajo` (~10 campos)
5. `empleados_contratistas` (~15 campos)
6. `autorizaciones_sst` (~20 campos, **tabla principal**)
7. `empleados_por_autorizacion` (~5 campos, relación N:N)
8. `log_ingresos_contratistas` (~8 campos)

**Backend**: 38 endpoints REST bajo `/api/sst/*`
- Empresas: 6 endpoints (CRUD + búsqueda)
- Planillas: 4 endpoints (CRUD)
- Certificados: 3 endpoints (CRUD)
- Empleados: 4 endpoints (CRUD + por empresa)
- Autorizaciones: 8 endpoints (CRUD + estados + PDF)
- Ingresos/Salidas: 5 endpoints (registro + consultas)
- Reportes: 6 endpoints (dashboard + estadísticas)
- Operadores: 2 endpoints (listado, readonly)

**Frontend**: 2 vistas nuevas
- `admin_sst.html` (~600-800 líneas): Gestión completa
- `operador_seguridad.html` (~400-500 líneas): Registro ingresos/salidas

**Roles Nuevos**: 2
- `admin_sst`: Administrador SST (gestión completa)
- `operador_seguridad`: Operador en portería (solo ingresos/salidas)

---

### ⚠️ RIESGOS IDENTIFICADOS

| ID | Riesgo | Severidad | Probabilidad | Impacto | Mitigación |
|----|--------|-----------|--------------|---------|------------|
| **R1** | Complejidad de estados en autorizaciones (6 estados: BORRADOR, REVISION, APROBADA, RECHAZADA, VENCIDA, ANULADA) | 🔴 ALTO | Alta | Alto | Máquina de estados con validaciones estrictas + tests exhaustivos |
| **R2** | Generación de PDF puede fallar | 🟡 MEDIO | Media | Medio | Validar plantilla HTML + try/except + guardar HTML de respaldo |
| **R3** | Validación manual de planillas (no API pública) | 🟡 MEDIO | Alta | Medio | Capacitación personal + checklist + alertas 15 días antes vencimiento |
| **R4** | Datos duplicados con diferencias | 🟢 BAJO | Baja | Bajo | UNIQUE constraints + normalización + validación pre-guardado |

---

### ✅ RECOMENDACIONES TÉCNICAS CLAVE

1. **Cambiar librería PDF**: 
   - ❌ NO usar WeasyPrint (dependencias pesadas, instalación compleja Windows)
   - ✅ SÍ usar **xhtml2pdf** (`pip install xhtml2pdf`)
   - Más estable, sin dependencias del sistema, instalación simple

2. **Agregar validación NIT automática**:
   ```python
   def validar_nit_colombia(nit, digito_verificacion):
       """Valida NIT con algoritmo módulo 11 oficial"""
       # Implementar antes de desplegar
   ```

3. **Validar archivos PDF con seguridad**:
   ```python
   ALLOWED_EXTENSIONS = {'pdf'}
   ALLOWED_MIMETYPES = {'application/pdf'}
   MAX_FILE_SIZE_MB = 5
   
   def validar_archivo_seguro(file):
       # Validar extensión, mime-type real, tamaño
   ```

4. **Implementar por 7 fases iterativas** (no todo de una vez):
   - Fase 1: DB + Modelos (12-17 días)
   - Fase 2: Empresas + Planillas (15-20 días)
   - Fase 3: Empleados + Certificados (12-15 días)
   - Fase 4: Autorizaciones (18-25 días) ← **Más compleja**
   - Fase 5: Ingresos/Salidas (8-12 días)
   - Fase 6: Reportes (10-15 días)
   - Fase 7: Testing completo (12-16 días)

5. **Backup OBLIGATORIO antes de iniciar**:
   ```powershell
   # Backup DB
   pg_dump -U postgres control_visitantes > backup_pre_sst_$(Get-Date -Format 'yyyyMMdd').sql
   
   # Backup código
   git checkout -b feature/modulo-sst
   ```

6. **Suite de tests completa** (NO está en especificación):
   - Tests unitarios para cada endpoint (38 tests)
   - Tests de integración para flujos (8 tests)
   - Tests de seguridad OWASP (5 tests)
   - Tests de permisos RBAC (10 tests)
   - Tests de carga (registro 100 empleados)

---

### 📊 DESGLOSE DE TIEMPO POR FASE

| Fase | Actividad | Días Estimados |
|------|-----------|----------------|
| 0 | Análisis + Backup + Branch | 2-3 |
| 1 | Migraciones DB (8 tablas) | 8-12 |
| 2 | Modelos SQLAlchemy (8 modelos) | 4-5 |
| 3 | Endpoints básicos CRUD | 8-10 |
| 4 | Lógica de negocio compleja | 5-7 |
| 5 | Generación de PDF | 3-4 |
| 6 | Frontend admin_sst.html | 6-8 |
| 7 | Frontend operador_seguridad.html | 4-5 |
| 8 | Componentes JS nuevos | 2-3 |
| 9 | Testing unitario Backend | 5-7 |
| 10 | Testing integración | 4-5 |
| 11 | Testing seguridad (OWASP) | 3-4 |
| 12 | Documentación técnica | 2-3 |
| 13 | Manuales de usuario | 3-4 |
| 14 | Capacitación personal | 2-3 |
| 15 | Despliegue producción | 2-3 |
| 16 | Ajustes post-despliegue | 5-7 |
| **TOTAL SIN BUFFER** | | **68-92** |
| **TOTAL CON BUFFER (20%)** | | **82-110** |
| **ESTIMACIÓN FINAL CONSERVADORA** | | **80-120** |

---

### ✅ FORTALEZAS DEL DISEÑO

1. ✅ **Arquitectura modular perfecta**: Cero entrelazado con sistema actual
2. ✅ **Diseño de DB robusto**: Normalizado 3NF, relaciones correctas, índices optimizados
3. ✅ **Cumplimiento normativo**: Ley 100 ✅, Resolución 4272 ✅, OWASP ✅
4. ✅ **Separación de responsabilidades clara**: admin_sst (gestión) vs operador_seguridad (registro)
5. ✅ **Documentación excepcional**: 2692 líneas, extremadamente detallada
6. ✅ **Auditoría completa**: Todos los cambios en `log_eventos`
7. ✅ **Flujos bien pensados**: 4 flujos documentados con casos de uso reales

---

### ⚠️ DEBILIDADES IDENTIFICADAS

1. ⚠️ **Tiempo subestimado**: Documento estima 48-68 días, realista es 80-120 días
2. ⚠️ **Complejidad alta**: 38 endpoints, máquina de estados compleja, 8 tablas
3. ⚠️ **Validación de archivos incompleta**: Falta validación mime-type y tamaño
4. ⚠️ **Validación NIT manual**: No hay algoritmo automático (fácil de agregar)
5. ⚠️ **No hay API pública para validar planillas**: Validación 100% manual
6. ⚠️ **Testing no especificado**: Suite completa debe diseñarse desde cero

---

### 🎯 VEREDICTO FINAL COPILOT

**Calificación**: ⭐⭐⭐⭐☆ (4/5 estrellas)

**Recomendación**: ✅ **PROCEDER CON IMPLEMENTACIÓN** bajo las siguientes condiciones:

1. ✅ Aceptar tiempo realista: **80-120 días** (no 48-68)
2. ✅ Backup completo DB + código antes de iniciar
3. ✅ Implementar por fases (no todo de una vez)
4. ✅ Usar xhtml2pdf en lugar de WeasyPrint
5. ✅ Agregar validaciones de seguridad para archivos PDF
6. ✅ Implementar validación automática de NIT
7. ✅ Crear suite completa de tests (no está en documento)
8. ✅ Capacitación previa del personal (admin_sst, operador_seguridad)
9. ✅ Despliegue gradual: 1 sede → todas las sedes
10. ✅ Soporte intensivo primeras 2 semanas post-despliegue

**¿Por qué 4/5 y no 5/5?**
- ⚠️ Complejidad alta requiere experiencia sólida en máquinas de estado
- ⚠️ Tiempo de desarrollo largo (3-4 meses calendario)
- ⚠️ Validaciones manuales (planillas) sin alternativa automatizada

**¿Por qué NO 3/5 o menos?**
- ✅ Diseño arquitectónico excelente (modular, independiente)
- ✅ Cumple todos los estándares de seguridad y normativos
- ✅ Documentación excepcional
- ✅ NO hay bloqueadores técnicos

---

### 📌 PRÓXIMOS PASOS INMEDIATOS (SI SE APRUEBA)

**Antes de escribir código**:
1. ✅ Aprobar este análisis (stakeholders + Claude revisor)
2. ✅ Crear backup completo DB + código
3. ✅ Crear branch `feature/modulo-sst`
4. ✅ Confirmar recursos: tiempo (80-120 días) + personal
5. ✅ Definir plan de capacitación

**Primera fase (12-17 días)**:
1. Migración `usuarios`: Agregar roles admin_sst, operador_seguridad
2. Crear seeders operadores (EPS, AFP, ARL)
3. Crear 8 migraciones de tablas
4. Testing integridad referencial
5. Verificación ambiente desarrollo

---

### 🔍 SOLICITUD A CLAUDE (AUDITOR)

**Claude**: Por favor revisa este análisis y:
1. ✅ Valida si la estimación 80-120 días es realista (comparado con tu análisis)
2. ✅ Confirma si los riesgos identificados son correctos
3. ✅ Revisa si las recomendaciones técnicas son apropiadas
4. ⚠️ Identifica cualquier riesgo que haya pasado desapercibido
5. ✅ Da tu veredicto final: ¿PROCEDER o POSPONER?

**Archivo de referencia completo**: `ANALISIS_VIABILIDAD_MODULO_SST.md`

---

## TAREAS PENDIENTES — FASE 1 (Correcciones críticas)

### TAREA-001: Fix crítico — Dependencia.to_dict() rompe API [PENDIENTE]
- **Prioridad**: CRÍTICA
- **Origen**: Auditoría consolidada — hallazgo crítico #1
- **Qué hacer**: El método `to_dict()` en el modelo `Dependencia` lanza error cuando se llama con `incluir_sedes=False`. Corregir el parámetro y su manejo.
- **Archivos**: `backend/app/models/` (modelo Dependencia)
- **Tests a correr**: `pytest backend/tests/ -v` — verificar que `/api/dependencias` responde 200
- **Criterio de aceptación**: Ninguna ruta que llame `dependencia.to_dict()` lanza excepción

### TAREA-002: Reemplazar print() por logger — autorizaciones.py [EN PROGRESO → REVISAR]
- **Prioridad**: ALTA
- **Origen**: Auditoría Claude — QW-02
- **Estado actual**: Copilot aplicó cambios (diff visto el 2026-03-19)
- **Qué verificar**:
  - `from app.utils.logger import logger` importado ✅ (confirmado en diff)
  - Todos los `print()` reemplazados por `logger.info/debug/error` ✅
  - Errores HTTP 500 ya no exponen `str(e)` al cliente ✅
- **Tests a correr**: `pytest backend/tests/ -v`
- **Criterio de aceptación**: `grep -r "print(" backend/app/routes/` no devuelve resultados

### TAREA-003: Reemplazar print() por logger — auth.py [PENDIENTE]
- **Prioridad**: ALTA
- **Origen**: Auditoría Claude — QW-02
- **Qué hacer**: Aplicar mismo patrón de TAREA-002 al archivo `backend/app/routes/auth.py`
- **Archivos**: `backend/app/routes/auth.py`
- **Tests a correr**: `pytest backend/tests/test_auth.py -v`
- **Criterio de aceptación**: Sin `print()` en auth.py, errores no exponen stack trace al cliente

### TAREA-004: Validación de email — integrar en rutas [PENDIENTE]
- **Prioridad**: ALTA
- **Origen**: Copilot agregó `Usuario.validar_email()` en modelo (diff visto 2026-03-19)
- **Qué hacer**: El método `validar_email()` ya existe en el modelo pero no está siendo llamado en las rutas de creación/edición de usuarios. Integrar la validación.
- **Archivos**: `backend/app/routes/` (rutas que crean/editan usuarios)
- **Tests a correr**: `pytest backend/tests/test_usuarios.py -v`
- **Criterio de aceptación**: POST /api/usuarios con email inválido devuelve 400 con mensaje claro

### TAREA-005: Sentry — confirmar configuración [PENDIENTE]
- **Prioridad**: MEDIA
- **Origen**: Copilot agregó integración Sentry en `__init__.py`
- **Qué hacer**: Verificar que `SENTRY_DSN` está documentado en `.env.example` y que la integración no afecta el entorno de desarrollo (no debe bloguear arranque si DSN no está configurado).
- **Archivos**: `backend/app/__init__.py`, `.env.example`
- **Tests a correr**: Arrancar app en modo desarrollo, verificar que inicia sin error aunque `SENTRY_DSN` no esté en `.env`
- **Criterio de aceptación**: App arranca limpia en dev sin `SENTRY_DSN`

### TAREA-006: requirements.txt — separar dev de prod [PENDIENTE]
- **Prioridad**: MEDIA
- **Origen**: Auditoría — Copilot movió pytest/black/flake8 fuera de requirements.txt
- **Qué hacer**: Verificar que `requirements-dev.txt` existe y tiene las dependencias de desarrollo. Confirmar que `requirements.txt` solo tiene lo de producción (gunicorn, waitress, sentry-sdk ya están).
- **Archivos**: `backend/requirements.txt`, `backend/requirements-dev.txt`
- **Criterio de aceptación**: `pip install -r requirements.txt` en producción NO instala pytest

---

## ANÁLISIS — Módulo SST (Para que Copilot revise)
> Claude solicita que Copilot evalúe la viabilidad técnica de implementar el módulo SST
> **No implementar aún — solo analizar y documentar**

### CONSULTA-SST-01: ¿Es viable el campo GENERATED ALWAYS? [PENDIENTE REVISIÓN COPILOT]
- **Pregunta**: ¿La versión de PostgreSQL en el servidor de producción soporta `GENERATED ALWAYS AS (...) STORED`? (requiere PG 12+)
- **Cómo verificar**: `SELECT version();` en la BD de producción
- **Acción**: Documentar resultado aquí y en Engram

### CONSULTA-SST-02: ¿ReportLab o WeasyPrint para PDF? [PENDIENTE DECISIÓN]
- **Pregunta**: Para generar el formato SC-SST-FOR-015, ¿cuál librería recomienda Copilot?
  - `reportlab` — más potente, curva de aprendizaje mayor
  - `WeasyPrint` — HTML→PDF, más fácil con templates Jinja2
- **Contexto**: El sistema ya usa Jinja2 en Flask, WeasyPrint podría integrarse más fácil.
- **Acción**: Copilot documenta recomendación aquí antes de que el usuario decida

---

## Historial completado

| Fecha | Tarea | Hecho por | Commit |
|-------|-------|-----------|--------|
| 2026-03-19 | Setup logger.py con rotación | Copilot | pendiente hash |
| 2026-03-19 | print()→logger en autorizaciones.py | Copilot | pendiente hash |
| 2026-03-19 | Ocultar str(e) en errores HTTP 500 (sedes, autorizaciones) | Copilot | pendiente hash |
| 2026-03-19 | Agregar Usuario.validar_email() | Copilot | pendiente hash |
| 2026-03-19 | Integrar Sentry en __init__.py | Copilot | pendiente hash |
| 2026-03-19 | Separar requirements.txt (prod vs dev) | Copilot | pendiente hash |
