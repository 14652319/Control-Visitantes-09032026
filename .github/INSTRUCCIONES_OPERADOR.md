# INSTRUCCIONES PARA COPILOT @operador
# Implementación Módulo SST — Sistema Control Visitantes

> **TU ROL**: Ejecutor / Implementador
> **TU JEFE**: Copilot @evaluador (coordina con Claude auditor)
> **TU TRABAJO**: Implementar código según este plan paso a paso
> **REGLA DE ORO**: NO avances al siguiente checkpoint hasta que veas `[✅ APROBADO]` en `.github/COPILOT_TASKS.md`

---

## 🚨 ESTADO ACTUAL — LEER ANTES DE HACER CUALQUIER COSA

```
✅ CORRECCIONES 3.2.2 y 3.2.3 APLICADAS POR CLAUDE (commit siguiente)
✅ CHECKPOINT 3.2.4 puede ser revisado
⏳ CHECKPOINT 3.2.5 espera aprobación de Claude sobre 3.2.4
```

---

## 📋 PROTOCOLO DE TRABAJO

### 🔄 Flujo de Trabajo

```
1. Lees CHECKPOINT actual aquí (INSTRUCCIONES_OPERADOR.md)
2. Implementas según instrucciones detalladas
3. Ejecutas tests de verificación
4. Escribes actualización en .github/COPILOT_TASKS.md sección [COPILOT EJECUTOR]
5. Marcas [ESPERANDO VALIDACIÓN CLAUDE]
6. ESPERAS hasta ver [✅ APROBADO POR CLAUDE] en COPILOT_TASKS.md
7. Si ves [❌ REQUIERE CORRECCIÓN], corriges y vuelves a paso 4
8. Si ves [✅ APROBADO], avanzas al siguiente CHECKPOINT
```

---

## ⛔ MAPA DE SECCIONES — QUIÉN ESCRIBE DÓNDE

```
╔══════════════════════════════════════════════════════════════╗
║  SECCIÓN                    ¿QUIÉN ESCRIBE?   ¿VOS?         ║
╠══════════════════════════════════════════════════════════════╣
║  [COPILOT EJECUTOR]         @operador          ✅ SÍ        ║
║  [COPILOT EVALUADOR]        @evaluador         ❌ NO        ║
║  [CLAUDE SUPERVISOR]        Claude Code        ❌ NUNCA     ║
╚══════════════════════════════════════════════════════════════╝
```

**Solo escribís en `[COPILOT EJECUTOR]`.**
Si escribís en `[CLAUDE SUPERVISOR]`, Claude lo borra y la validación queda inválida.

---

### 📝 Plantilla para actualizar COPILOT_TASKS.md (copiar y pegar exacto)

```markdown
---
## [COPILOT EJECUTOR] — CHECKPOINT X.Y.Z

Fecha: YYYY-MM-DD HH:MM
Commit: abc1234

QUÉ HICE:
- [paso 1]
- [paso 2]

ARCHIVOS CREADOS/MODIFICADOS:
- backend/archivo.py (nuevo)

TESTS EJECUTADOS:
  python backend/archivo.py → ✅ OK

ESTADO: [ESPERANDO VALIDACIÓN CLAUDE]
---
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### 📦 ESTADO ACTUAL

- **Rama**: `master` (cambiarás a `feature/modulo-sst` en PASO 2)
- **FASE activa**: Esperando inicio
- **Próximo**: PASO 1 - FASE 1 (5-8 horas)

---

## ✅ PASO 1: FASE 1 — Correcciones Críticas (5-8h)

### CHECKPOINT 1.1: Agregar Índices DB ⏱️ 30 min

**QUÉ VAS A HACER**: Crear y ejecutar migración que agrega 3 índices para optimizar búsquedas.

**ARCHIVO A CREAR**: `backend/migrate_add_indices_visitantes.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Agregar índices para optimización de búsquedas
Fecha: 2026-03-19
Checkpoint: 1.1
"""
from config import db
from sqlalchemy import text

def agregar_indices():
    """Agregar índices faltantes para optimizar búsquedas"""
    print("Iniciando creación de índices...")
    
    indices = [
        # Índice para búsquedas por identificación (visitantes)
        """
        CREATE INDEX IF NOT EXISTS idx_visitante_identificacion 
        ON visitantes(tipo_identificacion, num_identificacion);
        """,
        
        # Índice para búsquedas por fecha (log_visitantes)
        """
        CREATE INDEX IF NOT EXISTS idx_log_visitantes_fecha 
        ON log_visitantes(fecha_ingreso);
        """,
        
        # Índice para búsquedas de autorizaciones por usuario y estado
        """
        CREATE INDEX IF NOT EXISTS idx_autorizacion_usuario_estado 
        ON autorizaciones_ingreso(usuario_id, estado);
        """,
    ]
    
    for i, sql in enumerate(indices, 1):
        print(f"  Creando índice {i}/3...")
        db.session.execute(text(sql))
    
    db.session.commit()
    print("✅ 3 índices creados exitosamente")

def rollback():
    """Revertir índices si es necesario"""
    print("Eliminando índices...")
    db.session.execute(text("DROP INDEX IF EXISTS idx_visitante_identificacion;"))
    db.session.execute(text("DROP INDEX IF EXISTS idx_log_visitantes_fecha;"))
    db.session.execute(text("DROP INDEX IF EXISTS idx_autorizacion_usuario_estado;"))
    db.session.commit()
    print("✅ Índices eliminados")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            agregar_indices()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Ejecutando rollback...")
            rollback()
```

**COMANDOS A EJECUTAR**:
```powershell
# 1. Activar entorno virtual (si no está activo)
.\.venv\Scripts\Activate.ps1

# 2. Ejecutar migración
python backend/migrate_add_indices_visitantes.py

# 3. Verificar índices creados
psql -U postgres -d control_visitantes -c "\d visitantes"
psql -U postgres -d control_visitantes -c "\d log_visitantes"
psql -U postgres -d control_visitantes -c "\d autorizaciones_ingreso"
```

**VALIDACIÓN**:
- ✅ Script ejecuta sin errores
- ✅ Mensaje "✅ 3 índices creados exitosamente"
- ✅ Comando `\d` muestra los 3 índices en sus respectivas tablas

**COMMIT**:
```bash
git add backend/migrate_add_indices_visitantes.py
git commit -m "feat: agregar índices optimización búsquedas (CHECKPOINT 1.1)"
```

**AL TERMINAR**: Actualiza `.github/COPILOT_TASKS.md` sección `[COPILOT EJECUTOR]` y marca `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 1.2: Optimizar Queries (.filter → .filter_by) ⏱️ 45 min

**QUÉ VAS A HACER**: Reemplazar queries complejas por queries optimizadas en todos los archivos de rutas.

**ARCHIVOS A MODIFICAR**:

#### 1. `backend/app/routes/visitantes.py`

**Buscar línea ~45**:
```python
visitantes = Visitante.query.filter(Visitante.sede_id == sede_id).all()
```

**Reemplazar por**:
```python
visitantes = Visitante.query.filter_by(sede_id=sede_id).all()
```

**Buscar línea ~60**:
```python
visitante = Visitante.query.filter(Visitante.id == id).first()
```

**Reemplazar por**:
```python
visitante = Visitante.query.filter_by(id=id).first()
```

#### 2. `backend/app/routes/autorizaciones.py`

**Buscar línea ~60**:
```python
autorizaciones = AutorizacionIngreso.query.filter(
    AutorizacionIngreso.usuario_id == current_user.id
).all()
```

**Reemplazar por**:
```python
autorizaciones = AutorizacionIngreso.query.filter_by(
    usuario_id=current_user.id
).all()
```

**Buscar línea ~80**:
```python
autorizacion = AutorizacionIngreso.query.filter(
    AutorizacionIngreso.id == id
).first()
```

**Reemplazar por**:
```python
autorizacion = AutorizacionIngreso.query.filter_by(id=id).first()
```

#### 3. `backend/app/routes/sedes.py`

**Buscar y reemplazar** todas las ocurrencias similares.

#### 4. `backend/app/routes/dependencias.py`

**Buscar y reemplazar** todas las ocurrencias similares.

**PATRÓN GENERAL**:
```python
# ANTES (no hacer esto):
.filter(Modelo.campo == valor)

# DESPUÉS (hacer esto):
.filter_by(campo=valor)
```

**NOTA**: NO cambiar queries con condiciones complejas (OR, AND, comparaciones <, >, etc). Solo las simples con `==`.

**TESTS**:
```powershell
# Ejecutar tests de routes
pytest backend/tests/test_visitantes.py -v
pytest backend/tests/test_autorizaciones.py -v
pytest backend/tests/test_sedes.py -v
```

**CRITERIO**:
- ✅ Tests pasan 100%
- ✅ No hay errores de sintaxis
- ✅ Queries funcionan igual o mejor

**COMMIT**:
```bash
git add backend/app/routes/
git commit -m "refactor: optimizar queries con filter_by (CHECKPOINT 1.2)"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 1.3: Fix Crítico - Dependencia.to_dict() ⏱️ 30 min

**QUÉ VAS A HACER**: Corregir método `to_dict()` en modelo Dependencia que rompe API.

**ARCHIVO**: `backend/app/models/dependencia.py`

**Buscar el método** (línea ~40-60):
```python
def to_dict(self):
    """Convierte modelo a diccionario"""
    data = {
        'id': self.id,
        'nombre': self.nombre,
        # ... resto de campos
    }
    return data
```

**Reemplazar por**:
```python
def to_dict(self, incluir_sedes=True):
    """Convierte modelo a diccionario
    
    Args:
        incluir_sedes (bool): Si True, incluye datos de sede relacionada
    
    Returns:
        dict: Datos del modelo en formato JSON
    """
    data = {
        'id': self.id,
        'nombre': self.nombre,
        'descripcion': self.descripcion,
        'activo': self.activo,
        'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
    }
    
    # Incluir sede solo si se solicita y existe relación
    if incluir_sedes and hasattr(self, 'sede') and self.sede:
        data['sede'] = {
            'id': self.sede.id,
            'nombre': self.sede.nombre
        }
    
    return data
```

**TESTS**:
```powershell
# Test unitario del modelo
pytest backend/tests/test_dependencias.py -v

# Test de endpoint (con servidor corriendo en otra terminal)
# Terminal 1:
python backend/run.py

# Terminal 2:
curl http://localhost:5000/api/dependencias
# Debe responder 200 OK con JSON
```

**CRITERIO**:
- ✅ Método acepta parámetro `incluir_sedes` con default `True`
- ✅ Endpoint `/api/dependencias` responde 200
- ✅ No lanza excepción `TypeError`
- ✅ Tests pasan

**COMMIT**:
```bash
git add backend/app/models/dependencia.py
git commit -m "fix: agregar parámetro incluir_sedes a Dependencia.to_dict() (CHECKPOINT 1.3)"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 1.4: VALIDACIÓN FINAL FASE 1

**QUÉ VAS A HACER**: Ejecutar tests completos y verificar que TODO funciona.

**TESTS COMPLETOS**:
```powershell
# 1. Tests unitarios
pytest backend/tests/ -v

# 2. Verificar servidor arranca sin errores
python backend/run.py
# Debe mostrar: "Running on http://127.0.0.1:5000"
# Presionar Ctrl+C para detener

# 3. Verificar endpoints principales
# (Con servidor corriendo)
curl http://localhost:5000/api/visitantes
curl http://localhost:5000/api/autorizaciones
curl http://localhost:5000/api/dependencias
curl http://localhost:5000/api/sedes
```

**CHECKLIST**:
- [ ] 3 índices existen en base de datos
- [ ] Queries optimizadas (archivos modificados)
- [ ] Dependencia.to_dict() corregido
- [ ] Tests pasan 100%
- [ ] Servidor arranca sin errores
- [ ] Endpoints responden correctamente
- [ ] 3 commits realizados con mensajes claros

**AL TERMINAR**: Actualiza COPILOT_TASKS.md con resumen COMPLETO de FASE 1 → `[FASE 1 COMPLETA - ESPERANDO APROBACIÓN CLAUDE]`

---

## 🛠️ PASO 2: Preparación Módulo SST (2-3 días)

### ⚠️ IMPORTANTE: Solo ejecutar PASO 2 cuando veas `[✅ FASE 1 APROBADA POR CLAUDE]`

### CHECKPOINT 2.1: Backup Completo ⏱️ 1 hora

**QUÉ VAS A HACER**: Crear respaldos obligatorios de DB y código antes de cambios mayores.

**COMANDOS**:
```powershell
# 1. Crear directorio de backup
New-Item -ItemType Directory -Force -Path "D:\0.A. Proyectos\0.0. BackUp\control-visitantes-pre-sst"

# 2. Backup de base de datos
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump -U postgres -d control_visitantes > "D:\0.A. Proyectos\0.0. BackUp\control-visitantes-pre-sst\db_backup_$fecha.sql"

# 3. Verificar tamaño del archivo (debe ser >100KB)
Get-ChildItem "D:\0.A. Proyectos\0.0. BackUp\control-visitantes-pre-sst\" | Select-Object Name, Length

# 4. Crear tag en git
git tag -a "pre-sst-v1.0" -m "Backup antes de iniciar implementación Módulo SST - $(Get-Date -Format 'yyyy-MM-dd')"
git push origin pre-sst-v1.0

# 5. Crear y cambiar a branch nuevo
git checkout -b feature/modulo-sst
git push -u origin feature/modulo-sst
```

**VALIDACIÓN**:
- ✅ Archivo `db_backup_YYYYMMDD_HHMMSS.sql` existe
- ✅ Tamaño del backup > 100 KB
- ✅ Tag `pre-sst-v1.0` existe en GitHub
- ✅ Branch `feature/modulo-sst` activo y pusheado

**OUTPUT ESPERADO**:
```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          19/03/2026  14:30         245678 db_backup_20260319_143000.sql

Switched to a new branch 'feature/modulo-sst'
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 2.2: Migración Roles SST ⏱️ 45 min

**QUÉ VAS A HACER**: Agregar 2 roles nuevos (`admin_sst`, `operador_seguridad`) a tabla usuarios.

**ARCHIVO A CREAR**: `backend/migrate_add_roles_sst.py`

**CÓDIGO COMPLETO**:
```python
"""
Migración: Agregar roles admin_sst y operador_seguridad
Fecha: 2026-03-19
Checkpoint: 2.2
Relacionado: Módulo SST para gestión de contratistas
"""
from config import db
from sqlalchemy import text

def migrate():
    """Agregar nuevos roles a tabla usuarios"""
    print("=" * 60)
    print("MIGRACIÓN: Agregar roles SST a tabla usuarios")
    print("=" * 60)
    
    try:
        # Paso 1: Ampliar tipo de columna rol
        print("\n[1/3] Ampliando tipo de columna 'rol' a VARCHAR(50)...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            ALTER COLUMN rol TYPE VARCHAR(50);
        """))
        print("  ✅ Columna ampliada")
        
        # Paso 2: Eliminar constraint viejo
        print("\n[2/3] Eliminando constraint antiguo...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            DROP CONSTRAINT IF EXISTS check_rol_valido;
        """))
        print("  ✅ Constraint antiguo eliminado")
        
        # Paso 3: Crear constraint nuevo con roles adicionales
        print("\n[3/3] Creando constraint nuevo con 5 roles...")
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
        print("  ✅ Constraint nuevo creado")
        
        db.session.commit()
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA: Roles SST agregados exitosamente")
        print("=" * 60)
        print("\nRoles ahora disponibles:")
        print("  1. usuario_master")
        print("  2. usuario_operador")
        print("  3. usuario_funcionario")
        print("  4. admin_sst (NUEVO)")
        print("  5. operador_seguridad (NUEVO)")
        
    except Exception as e:
        print(f"\n❌ ERROR durante migración: {e}")
        print("Ejecutando rollback...")
        db.session.rollback()
        rollback()
        raise

def rollback():
    """Revertir cambios si algo falla"""
    print("\n" + "=" * 60)
    print("ROLLBACK: Revirtiendo migración de roles SST")
    print("=" * 60)
    
    try:
        print("\n[1/2] Eliminando constraint nuevo...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            DROP CONSTRAINT IF EXISTS check_rol_valido;
        """))
        print("  ✅ Constraint eliminado")
        
        print("\n[2/2] Restaurando constraint antiguo (3 roles)...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            ADD CONSTRAINT check_rol_valido 
            CHECK (rol IN (
                'usuario_master', 
                'usuario_operador', 
                'usuario_funcionario'
            ));
        """))
        print("  ✅ Constraint restaurado")
        
        db.session.commit()
        print("\n✅ ROLLBACK COMPLETADO: Sistema restaurado a 3 roles")
        
    except Exception as e:
        print(f"\n❌ ERROR durante rollback: {e}")
        db.session.rollback()

def verificar():
    """Verificar que migración fue exitosa"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: Comprobando migración")
    print("=" * 60)
    
    result = db.session.execute(text("""
        SELECT conname, pg_get_constraintdef(oid) AS definition
        FROM pg_constraint 
        WHERE conrelid = 'usuarios'::regclass 
        AND conname = 'check_rol_valido';
    """))
    
    row = result.fetchone()
    if row:
        print(f"\nConstraint encontrado: {row[0]}")
        print(f"Definición: {row[1]}")
        
        # Verificar que incluye los 5 roles
        definition = row[1]
        roles_esperados = ['admin_sst', 'operador_seguridad']
        todos_presentes = all(rol in definition for rol in roles_esperados)
        
        if todos_presentes:
            print("\n✅ VERIFICACIÓN EXITOSA: Todos los roles nuevos presentes")
            return True
        else:
            print("\n❌ VERIFICACIÓN FALLIDA: Faltan roles nuevos")
            return False
    else:
        print("\n❌ VERIFICACIÓN FALLIDA: Constraint no encontrado")
        return False

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            migrate()
            verificar()
        except Exception as e:
            print(f"\n❌ Error fatal: {e}")
            exit(1)
```

**EJECUTAR**:
```powershell
python backend/migrate_add_roles_sst.py
```

**OUTPUT ESPERADO**:
```
============================================================
MIGRACIÓN: Agregar roles SST a tabla usuarios
============================================================

[1/3] Ampliando tipo de columna 'rol' a VARCHAR(50)...
  ✅ Columna ampliada

[2/3] Eliminando constraint antiguo...
  ✅ Constraint antiguo eliminado

[3/3] Creando constraint nuevo con 5 roles...
  ✅ Constraint nuevo creado

============================================================
✅ MIGRACIÓN COMPLETADA: Roles SST agregados exitosamente
============================================================
```

**VERIFICACIÓN MANUAL**:
```powershell
psql -U postgres -d control_visitantes -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'usuarios'::regclass AND conname = 'check_rol_valido';"
```

**CRITERIO**:
- ✅ Migración ejecuta sin errores
- ✅ Mensaje "✅ MIGRACIÓN COMPLETADA"
- ✅ Verificación muestra 5 roles (incluyendo admin_sst, operador_seguridad)
- ✅ Usuarios existentes siguen funcionando

**COMMIT**:
```bash
git add backend/migrate_add_roles_sst.py
git commit -m "feat: agregar roles admin_sst y operador_seguridad (CHECKPOINT 2.2)"
git push origin feature/modulo-sst
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 2.3: Preparar Seeder Operadores ⏱️ 30 min

**QUÉ VAS A HACER**: Crear script para pre-cargar operadores de seguridad social (EPS, AFP, ARL).

**NOTA**: Este script NO se ejecuta ahora (la tabla no existe aún). Se ejecutará en FASE 3.1.3.

**ARCHIVO A CREAR**: `backend/init_operadores_ss.py`

**CÓDIGO** (ver archivo completo en el plan original, líneas del seeder)

**CRITERIO**:
- ✅ Archivo creado
- ✅ 13 operadores listados correctamente (EPS: 5, AFP: 4, ARL: 4)
- ✅ NITs correctos (datos reales de Colombia 2026)

**COMMIT**:
```bash
git add backend/init_operadores_ss.py
git commit -m "chore: preparar seeder operadores seguridad social (CHECKPOINT 2.3)"
git push origin feature/modulo-sst
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 2.4: VALIDACIÓN PASO 2 COMPLETO

**QUÉ VAS A HACER**: Verificar que toda la preparación está lista.

**CHECKLIST**:
- [ ] Backup DB existe (tamaño > 100KB)
- [ ] Tag `pre-sst-v1.0` en GitHub
- [ ] Branch `feature/modulo-sst` activo
- [ ] Migración roles ejecutada sin errores
- [ ] Constraint acepta 5 roles (verificado en DB)
- [ ] SEEDER preparado (archivo existe, no ejecutado)
- [ ] Sistema actual funciona normal (tests pasan)
- [ ] 3 commits en branch `feature/modulo-sst`

**TESTS**:
```powershell
# Verificar que sistema actual funciona
pytest backend/tests/ -v

# Verificar servidor arranca
python backend/run.py
# Ctrl+C para detener
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md con resumen COMPLETO de PASO 2 → `[PASO 2 COMPLETO - ESPERANDO APROBACIÓN CLAUDE]`

---

## 🏗️ PASO 3: Módulo SST (80-120 días)

### ✅ USUARIO AUTORIZÓ INICIO — 2026-03-19

**@evaluador agregó instrucciones de FASE 3.1 — Puedes iniciar ahora.**

---

## FASE 3.1 — Base de Datos y Modelos (12-17 días)

> Crear las 8 tablas nuevas y sus modelos SQLAlchemy. Sin esto, nada del módulo SST funciona.

---

### CHECKPOINT 3.1.1: Migración tabla `operadores_aportes` ⏱️ 2 horas

**QUÉ VAS A HACER**: Crear la tabla de EPS, AFP y ARL (datos maestros de seguridad social).

**ARCHIVO A CREAR**: `backend/migrate_create_operadores_aportes.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Crear tabla operadores_aportes
Fecha: 2026-03-19
Checkpoint: 3.1.1
Tabla para EPS, AFP y ARL registradas en Colombia
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Creando tabla operadores_aportes...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS operadores_aportes (
                id          SERIAL PRIMARY KEY,
                nombre      VARCHAR(100) NOT NULL,
                tipo        VARCHAR(10)  NOT NULL,
                nit         VARCHAR(20)  NOT NULL,
                activo      BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
                CONSTRAINT check_tipo_operador CHECK (tipo IN ('EPS', 'AFP', 'ARL')),
                CONSTRAINT unique_nit_tipo UNIQUE (nit, tipo)
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_operador_tipo
                ON operadores_aportes(tipo);
        """))
        db.session.commit()
        print("✅ Tabla operadores_aportes creada")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS operadores_aportes CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
```

**⚠️ NOTA IMPORTANTE**: Constraint es `UNIQUE(nit, tipo)` NO `UNIQUE(nit)`. Razón: SURA EPS y ARL SURA comparten NIT 800088702 (misma empresa Suramericana S.A.).

**DESPUÉS DE CREAR LA MIGRACIÓN**:
```powershell
# Ejecutar migración
python backend/migrate_create_operadores_aportes.py

# Ejecutar seeder (ahora sí, tabla existe)
python backend/init_operadores_ss.py

# Verificar 13 registros
psql -U postgres -d control_visitantes -c "SELECT tipo, COUNT(*) FROM operadores_aportes GROUP BY tipo ORDER BY tipo;"
# Esperado: ARL=4, AFP=4, EPS=5
```

**COMMIT**:
```bash
git add backend/migrate_create_operadores_aportes.py
git commit -m "feat: crear tabla operadores_aportes (EPS/AFP/ARL) - CHECKPOINT 3.1.1"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 3.1.2: Migración tabla `empresas_contratistas` ⏱️ 2 horas

**QUÉ VAS A HACER**: Crear tabla principal de empresas contratistas.

**ARCHIVO A CREAR**: `backend/migrate_create_empresas_contratistas.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Crear tabla empresas_contratistas
Fecha: 2026-03-19
Checkpoint: 3.1.2
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Creando tabla empresas_contratistas...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS empresas_contratistas (
                id                  SERIAL PRIMARY KEY,
                razon_social        VARCHAR(200) NOT NULL,
                nit                 VARCHAR(20)  NOT NULL UNIQUE,
                digito_verificacion VARCHAR(1)   NOT NULL,
                representante_legal VARCHAR(150) NOT NULL,
                telefono            VARCHAR(20),
                email               VARCHAR(100),
                direccion           VARCHAR(200),
                ciudad              VARCHAR(100),
                estado              VARCHAR(20)  NOT NULL DEFAULT 'activa',
                created_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
                updated_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
                created_by          INTEGER REFERENCES usuarios(id),
                CONSTRAINT check_estado_empresa CHECK (estado IN ('activa', 'inactiva', 'suspendida'))
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_empresa_nit
                ON empresas_contratistas(nit);
            CREATE INDEX IF NOT EXISTS idx_empresa_estado
                ON empresas_contratistas(estado);
        """))
        db.session.commit()
        print("✅ Tabla empresas_contratistas creada")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS empresas_contratistas CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
```

**DESPUÉS**:
```powershell
python backend/migrate_create_empresas_contratistas.py
# Verificar
psql -U postgres -d control_visitantes -c "\d empresas_contratistas"
```

**COMMIT**:
```bash
git add backend/migrate_create_empresas_contratistas.py
git commit -m "feat: crear tabla empresas_contratistas - CHECKPOINT 3.1.2"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

### CORRECCIÓN OBLIGATORIA 3.1.2A: Soporte Persona Natural

**ESTA CORRECCIÓN ES OBLIGATORIA ANTES DE 3.1.3.**

Claude Supervisor marcó CHECKPOINT 3.1.2 como **NO APROBADO** porque la tabla `empresas_contratistas` quedó solo para Persona Jurídica. El levantamiento exige soporte para `JURIDICA` y `NATURAL`.

**ARCHIVO A CREAR**: `backend/migrate_alter_empresas_persona_natural.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Alter tabla empresas_contratistas para soporte Persona Natural
Fecha: 2026-03-19
Checkpoint: 3.1.2A
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate():
    app = create_app()
    with app.app_context():
        print("Agregando soporte Persona Natural a empresas_contratistas...")

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD COLUMN IF NOT EXISTS tipo_persona VARCHAR(10) NOT NULL DEFAULT 'JURIDICA',
            ADD COLUMN IF NOT EXISTS tipo_identificacion VARCHAR(5),
            ADD COLUMN IF NOT EXISTS num_identificacion VARCHAR(20),
            ADD COLUMN IF NOT EXISTS primer_nombre VARCHAR(100),
            ADD COLUMN IF NOT EXISTS segundo_nombre VARCHAR(100),
            ADD COLUMN IF NOT EXISTS primer_apellido VARCHAR(100),
            ADD COLUMN IF NOT EXISTS segundo_apellido VARCHAR(100);
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS check_tipo_persona_empresa;
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD CONSTRAINT check_tipo_persona_empresa
            CHECK (tipo_persona IN ('JURIDICA', 'NATURAL'));
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS check_tipo_identificacion_empresa;
        """))

        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD CONSTRAINT check_tipo_identificacion_empresa
            CHECK (
                tipo_identificacion IS NULL
                OR tipo_identificacion IN ('CC', 'CE', 'TI', 'NIT', 'PAS', 'PEP')
            );
        """))

        db.session.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_empresa_num_identificacion_unique
            ON empresas_contratistas(num_identificacion)
            WHERE num_identificacion IS NOT NULL;
        """))

        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_empresa_tipo_persona
            ON empresas_contratistas(tipo_persona);
        """))

        db.session.commit()
        print("✅ Soporte Persona Natural agregado")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP INDEX IF EXISTS idx_empresa_tipo_persona;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_empresa_num_identificacion_unique;"))
        db.session.execute(text("ALTER TABLE empresas_contratistas DROP CONSTRAINT IF EXISTS check_tipo_identificacion_empresa;"))
        db.session.execute(text("ALTER TABLE empresas_contratistas DROP CONSTRAINT IF EXISTS check_tipo_persona_empresa;"))
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP COLUMN IF EXISTS segundo_apellido,
            DROP COLUMN IF EXISTS primer_apellido,
            DROP COLUMN IF EXISTS segundo_nombre,
            DROP COLUMN IF EXISTS primer_nombre,
            DROP COLUMN IF EXISTS num_identificacion,
            DROP COLUMN IF EXISTS tipo_identificacion,
            DROP COLUMN IF EXISTS tipo_persona;
        """))
        db.session.commit()
        print("✅ Rollback ejecutado")


if __name__ == '__main__':
    migrate()
```

**DESPUÉS**:
```powershell
python backend/migrate_alter_empresas_persona_natural.py
python -c "from app import create_app; from app.extensions import db; from sqlalchemy import text; app=create_app(); ctx=app.app_context(); ctx.push(); print(db.session.execute(text(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'empresas_contratistas' ORDER BY ordinal_position\")).fetchall())"
```

**COMMIT**:
```bash
git add backend/migrate_alter_empresas_persona_natural.py
git commit -m "fix: agregar soporte persona natural a empresas_contratistas - CHECKPOINT 3.1.2A"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md con resumen de la corrección y marca `[ESPERANDO VALIDACIÓN CLAUDE]`.

---

### CHECKPOINT 3.1.3: Migración tablas `empleados_contratistas` y `certificados_trabajo` ⏱️ 2 horas

**QUÉ VAS A HACER**: Crear 2 tablas relacionadas con empleados.

**ARCHIVO A CREAR**: `backend/migrate_create_empleados_contratistas.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Crear tablas empleados_contratistas y certificados_trabajo
Fecha: 2026-03-19
Checkpoint: 3.1.3
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("[1/2] Creando tabla empleados_contratistas...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS empleados_contratistas (
                id              SERIAL PRIMARY KEY,
                empresa_id      INTEGER NOT NULL REFERENCES empresas_contratistas(id),
                tipo_id         VARCHAR(5)   NOT NULL,
                num_id          VARCHAR(20)  NOT NULL,
                nombres         VARCHAR(100) NOT NULL,
                apellidos       VARCHAR(100) NOT NULL,
                cargo           VARCHAR(100),
                eps_id          INTEGER REFERENCES operadores_aportes(id),
                afp_id          INTEGER REFERENCES operadores_aportes(id),
                arl_id          INTEGER REFERENCES operadores_aportes(id),
                estado          VARCHAR(20)  NOT NULL DEFAULT 'activo',
                created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                CONSTRAINT check_tipo_id_empleado CHECK (tipo_id IN ('CC', 'CE', 'PA', 'PEP')),
                CONSTRAINT check_estado_empleado CHECK (estado IN ('activo', 'inactivo')),
                CONSTRAINT unique_empleado_empresa UNIQUE (empresa_id, tipo_id, num_id)
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_empleado_empresa_estado
                ON empleados_contratistas(empresa_id, estado);
            CREATE INDEX IF NOT EXISTS idx_empleado_identificacion
                ON empleados_contratistas(tipo_id, num_id);
        """))

        print("[2/2] Creando tabla certificados_trabajo...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS certificados_trabajo (
                id                  SERIAL PRIMARY KEY,
                empleado_id         INTEGER NOT NULL REFERENCES empleados_contratistas(id),
                tipo_certificado    VARCHAR(50)  NOT NULL,
                nombre_certificado  VARCHAR(200) NOT NULL,
                fecha_expedicion    DATE         NOT NULL,
                fecha_vencimiento   DATE,
                archivo_nombre      VARCHAR(200),
                archivo_ruta        VARCHAR(500),
                verificado          BOOLEAN      NOT NULL DEFAULT FALSE,
                created_at          TIMESTAMP    NOT NULL DEFAULT NOW()
            );
        """))
        db.session.commit()
        print("✅ Tablas empleados y certificados creadas")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS certificados_trabajo CASCADE;"))
        db.session.execute(text("DROP TABLE IF EXISTS empleados_contratistas CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
```

**DESPUÉS**:
```powershell
python backend/migrate_create_empleados_contratistas.py
psql -U postgres -d control_visitantes -c "\dt *contratista* *certificado*"
```

**COMMIT**:
```bash
git add backend/migrate_create_empleados_contratistas.py
git commit -m "feat: crear tablas empleados_contratistas y certificados_trabajo - CHECKPOINT 3.1.3"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 3.1.4: Migración tablas `planillas_ss`, `autorizaciones_sst` y `log_ingresos_contratistas` ⏱️ 3 horas

**QUÉ VAS A HACER**: Crear las 3 tablas más complejas del módulo SST.

**ARCHIVO A CREAR**: `backend/migrate_create_tablas_sst_principales.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Crear tablas planillas_ss, autorizaciones_sst, log_ingresos_contratistas
Fecha: 2026-03-19
Checkpoint: 3.1.4
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("[1/3] Creando tabla planillas_ss...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS planillas_ss (
                id              SERIAL PRIMARY KEY,
                empresa_id      INTEGER NOT NULL REFERENCES empresas_contratistas(id),
                periodo         VARCHAR(7)   NOT NULL,
                fecha_pago      DATE         NOT NULL,
                vigencia_fin    DATE         NOT NULL,
                archivo_nombre  VARCHAR(200),
                archivo_ruta    VARCHAR(500),
                estado          VARCHAR(20)  NOT NULL DEFAULT 'pendiente',
                created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                verificado_por  INTEGER REFERENCES usuarios(id),
                verificado_at   TIMESTAMP,
                CONSTRAINT check_estado_planilla CHECK (estado IN ('pendiente', 'verificada', 'rechazada')),
                CONSTRAINT unique_empresa_periodo UNIQUE (empresa_id, periodo)
            );
        """))

        print("[2/3] Creando tabla autorizaciones_sst...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS autorizaciones_sst (
                id              SERIAL PRIMARY KEY,
                empresa_id      INTEGER NOT NULL REFERENCES empresas_contratistas(id),
                sede_id         INTEGER REFERENCES sedes(id),
                labor           VARCHAR(300) NOT NULL,
                fecha_inicio    DATE         NOT NULL,
                fecha_fin       DATE         NOT NULL,
                estado          VARCHAR(20)  NOT NULL DEFAULT 'borrador',
                pdf_ruta        VARCHAR(500),
                created_by      INTEGER NOT NULL REFERENCES usuarios(id),
                aprobado_by     INTEGER REFERENCES usuarios(id),
                created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
                CONSTRAINT check_estado_autorizacion_sst
                    CHECK (estado IN ('borrador', 'revision', 'aprobada', 'vencida', 'anulada'))
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_autorizacion_sst_empresa
                ON autorizaciones_sst(empresa_id, estado);
            CREATE INDEX IF NOT EXISTS idx_autorizacion_sst_vigencia
                ON autorizaciones_sst(fecha_fin) WHERE estado = 'aprobada';
        """))

        print("[3/3] Creando tabla log_ingresos_contratistas...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS log_ingresos_contratistas (
                id                  SERIAL PRIMARY KEY,
                empleado_id         INTEGER NOT NULL REFERENCES empleados_contratistas(id),
                autorizacion_sst_id INTEGER NOT NULL REFERENCES autorizaciones_sst(id),
                sede_id             INTEGER REFERENCES sedes(id),
                tipo_evento         VARCHAR(10)  NOT NULL,
                timestamp_evento    TIMESTAMP    NOT NULL DEFAULT NOW(),
                registrado_por      INTEGER REFERENCES usuarios(id),
                observaciones       VARCHAR(500),
                CONSTRAINT check_tipo_evento_contratista CHECK (tipo_evento IN ('ingreso', 'salida'))
            );
        """))
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_log_contratista_fecha
                ON log_ingresos_contratistas(timestamp_evento, sede_id);
        """))

        db.session.commit()
        print("✅ 3 tablas principales SST creadas")

def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS log_ingresos_contratistas CASCADE;"))
        db.session.execute(text("DROP TABLE IF EXISTS autorizaciones_sst CASCADE;"))
        db.session.execute(text("DROP TABLE IF EXISTS planillas_ss CASCADE;"))
        db.session.commit()
        print("✅ Rollback ejecutado")

if __name__ == '__main__':
    migrate()
```

**DESPUÉS**:
```powershell
python backend/migrate_create_tablas_sst_principales.py
psql -U postgres -d control_visitantes -c "\dt" | Select-String sst
```

**COMMIT**:
```bash
git add backend/migrate_create_tablas_sst_principales.py
git commit -m "feat: crear tablas planillas_ss, autorizaciones_sst, log_ingresos_contratistas - CHECKPOINT 3.1.4"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

================================================================================
# FASE 3.2 — ENDPOINTS API SST
# Escrito por: Copilot @evaluador
# Fecha: 2026-03-19
# Pre-requisito: FASE 3.1 aprobada ✅ (commit dd9acee)
================================================================================

## CONTEXTO FASE 3.2

FASE 3.1 entregó: 7 tablas + 7 modelos SQLAlchemy.
FASE 3.2 entrega: La API REST completa del módulo SST.

**Branch activo**: `feature/modulo-sst`
**Estos endpoints son NUEVOS** — no modifican endpoints existentes.

**Hallazgos de FASE 3.1 a resolver en 3.2.0** (antes de cualquier endpoint):
- `CP313-01`: `tipo_certificado` sin CHECK constraint en `certificados_trabajo`
- `CP314-01`: `numero_autorizacion` no tiene lógica de consecutivo (SST-{AÑO}-{0001})
- `CP314-02`: No hay CHECK `fecha_fin >= fecha_inicio` en `autorizaciones_sst`
- `CP313-03` + `CP314-04`: Índices de performance faltantes

---

## CHECKPOINT 3.2.0 — Correcciones BD (hallazgos FASE 3.1)

### Qué hacer

Crear `backend/migrate_fix_hallazgos_3_1.py` y ejecutarlo.

```python
"""
Migración: Corrección de hallazgos detectados en FASE 3.1
Checkpoint: 3.2.0
Hallazgos: CP313-01, CP314-01, CP314-02, CP313-03, CP314-04
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate():
    app = create_app()
    with app.app_context():
        print("Aplicando correcciones de hallazgos FASE 3.1...")

        # CP313-01: CHECK constraint para tipo_certificado
        db.session.execute(text("""
            ALTER TABLE certificados_trabajo
            DROP CONSTRAINT IF EXISTS check_tipo_certificado;
        """))
        db.session.execute(text("""
            ALTER TABLE certificados_trabajo
            ADD CONSTRAINT check_tipo_certificado CHECK (
                tipo_certificado IN ('ALTURAS', 'ELECTRICO', 'ESPACIOS_CONFINADOS', 'MANEJO_QUIMICOS', 'PRIMEROS_AUXILIOS', 'OTRO')
            );
        """))
        print("  ✅ CP313-01: CHECK type_certificado aplicado")

        # CP314-02: CHECK fecha_fin >= fecha_inicio en autorizaciones_sst
        db.session.execute(text("""
            ALTER TABLE autorizaciones_sst
            DROP CONSTRAINT IF EXISTS check_vigencia_autorizacion;
        """))
        db.session.execute(text("""
            ALTER TABLE autorizaciones_sst
            ADD CONSTRAINT check_vigencia_autorizacion CHECK (
                vigencia_fin >= vigencia_inicio
            );
        """))
        print("  ✅ CP314-02: CHECK vigencia_fin >= vigencia_inicio aplicado")

        # CP314-01: Agregar columna consecutivo_anio para generación SST-{AÑO}-{0001}
        # La columna numero_autorizacion ya existe — solo aseguramos el índice
        db.session.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_autorizacion_numero
            ON autorizaciones_sst(numero_autorizacion);
        """))
        print("  ✅ CP314-01: Índice único en numero_autorizacion asegurado")

        # CP313-03: Índice empleado_id en certificados_trabajo
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_certificado_empleado
            ON certificados_trabajo(empleado_id);
        """))
        print("  ✅ CP313-03: Índice idx_certificado_empleado creado")

        # CP314-04: Índice empleado_id en log_ingresos_contratistas
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_log_ingreso_empleado
            ON log_ingresos_contratistas(empleado_id);
        """))
        print("  ✅ CP314-04: Índice idx_log_ingreso_empleado creado")

        db.session.commit()
        print("\n✅ Todos los hallazgos de FASE 3.1 corregidos")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("ALTER TABLE certificados_trabajo DROP CONSTRAINT IF EXISTS check_tipo_certificado;"))
        db.session.execute(text("ALTER TABLE autorizaciones_sst DROP CONSTRAINT IF EXISTS check_vigencia_autorizacion;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_autorizacion_numero;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_certificado_empleado;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_log_ingreso_empleado;"))
        db.session.commit()
        print("✅ Rollback 3.2.0 ejecutado")


if __name__ == '__main__':
    migrate()
```

**EJECUTAR**:
```powershell
cd backend
& "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\.venv\Scripts\python.exe" migrate_fix_hallazgos_3_1.py
```

**VERIFICAR en psql**:
```sql
-- Verificar constraints
SELECT constraint_name FROM information_schema.table_constraints
WHERE table_name IN ('certificados_trabajo', 'autorizaciones_sst')
AND constraint_type = 'CHECK';

-- Verificar índices nuevos
SELECT indexname FROM pg_indexes
WHERE indexname IN ('idx_certificado_empleado', 'idx_log_ingreso_empleado', 'idx_autorizacion_numero');
```

**COMMIT**:
```bash
git add backend/migrate_fix_hallazgos_3_1.py
git commit -m "fix: corregir hallazgos FASE 3.1 (constraints + indices) - CHECKPOINT 3.2.0"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.1 — Blueprint SST + Roles nuevos + Decoradores

### Qué hacer

**PARTE A**: Actualizar `backend/app/routes/auth.py`

Busca la función `role_required` y agrega los nuevos roles:

```python
# En auth.py, función role_required — agregar al set de roles válidos:
ROLES_VALIDOS = {
    'usuario_master',
    'usuario_funcionario', 
    'usuario_operador',
    'admin_sst',          # NUEVO — administrador SST
    'operador_seguridad', # NUEVO — operador de portería para contratistas
}
```

Si `role_required` usa un CHECK constraint en BD, primero verifica si existe y actualízalo:
```sql
-- Verificar constraint de rol
SELECT constraint_name, check_clause FROM information_schema.check_constraints
WHERE constraint_name LIKE '%rol%';
```

Si existe constraint en la columna `rol` de `usuarios`, crea migración para actualizarlo.

**PARTE B**: Crear `backend/app/routes/sst.py`

```python
"""
========================================
RUTAS: MÓDULO SST (Seguridad y Salud en el Trabajo)
Gestión completa de contratistas, planillas y autorizaciones SST
========================================
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.routes.auth import role_required
from app.utils.logger import logger

bp = Blueprint('sst', __name__, url_prefix='/api/sst')

# Roles con acceso al módulo SST
ROLES_SST = ['usuario_master', 'admin_sst', 'operador_seguridad']
ROLES_ADMIN_SST = ['usuario_master', 'admin_sst']


# ============================================================
# ENDPOINT: GET /api/sst/operadores
# Catálogo de operadores de aportes (EPS/AFP/ARL)
# Acceso: Cualquier usuario autenticado con rol SST
# ============================================================
@bp.route('/operadores', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_operadores():
    """Lista operadores de aportes (EPS, AFP, ARL) — catálogo de referencia"""
    try:
        from app.models.operador_aportes import OperadorAportes
        
        tipo = request.args.get('tipo')  # EPS | AFP | ARL
        
        query = OperadorAportes.query.filter_by(activo=True)
        if tipo and tipo.upper() in ('EPS', 'AFP', 'ARL'):
            query = query.filter_by(tipo=tipo.upper())
        
        operadores = query.order_by(OperadorAportes.tipo, OperadorAportes.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [op.to_dict() for op in operadores],
            'total': len(operadores)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando operadores SST: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ENDPOINT: GET /api/sst/health
# Health check del módulo SST
# ============================================================
@bp.route('/health', methods=['GET'])
@login_required
def health():
    """Verifica que el módulo SST está activo"""
    return jsonify({'success': True, 'message': 'Módulo SST activo', 'version': '3.2'}), 200
```

**PARTE C**: Registrar el blueprint en `backend/app/__init__.py`

Busca donde se registran los otros blueprints y agrega:
```python
from app.routes import sst
app.register_blueprint(sst.bp)
```

**VERIFICAR**:
```powershell
# Levantar servidor y verificar
cd backend
& "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\.venv\Scripts\python.exe" -c "
from app import create_app
app = create_app()
with app.app_context():
    rules = [str(r) for r in app.url_map.iter_rules() if '/api/sst' in str(r)]
    print('Rutas SST registradas:')
    for r in rules: print(f'  {r}')
"
```

Debe mostrar: `/api/sst/operadores` y `/api/sst/health`.

**COMMIT**:
```bash
git add backend/app/routes/sst.py backend/app/__init__.py backend/app/routes/auth.py
git commit -m "feat: crear blueprint SST + endpoint operadores aportes - CHECKPOINT 3.2.1"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.2 — API Empresas Contratistas (CRUD)

### Qué hacer

Agregar al final de `backend/app/routes/sst.py` los endpoints de empresas contratistas.

**ENDPOINTS A IMPLEMENTAR**:

```
GET    /api/sst/empresas              — listar (con filtros: tipo_persona, estado, busqueda)
POST   /api/sst/empresas              — crear empresa
GET    /api/sst/empresas/<id>         — detalle empresa
PUT    /api/sst/empresas/<id>         — actualizar empresa
GET    /api/sst/empresas/buscar       — buscar por NIT o num_identificacion
```

**LÓGICA CRÍTICA — Validación por tipo_persona**:

```python
# En POST y PUT, validar según tipo_persona:
def validar_empresa(data):
    tipo = data.get('tipo_persona', '').upper()
    if tipo == 'JURIDICA':
        if not data.get('nit'):
            return False, "Persona Jurídica requiere NIT"
        if not data.get('razon_social'):
            return False, "Persona Jurídica requiere razón social"
    elif tipo == 'NATURAL':
        if not data.get('tipo_identificacion'):
            return False, "Persona Natural requiere tipo de identificación"
        if not data.get('num_identificacion'):
            return False, "Persona Natural requiere número de identificación"
        if not data.get('primer_nombre') or not data.get('primer_apellido'):
            return False, "Persona Natural requiere nombre y apellido"
    else:
        return False, "tipo_persona debe ser 'JURIDICA' o 'NATURAL'"
    return True, None
```

**LÓGICA CRÍTICA — Búsqueda inteligente** (GET /buscar):
```python
# Buscar por NIT (Jurídica) O por num_identificacion (Natural)
# Parámetro: ?q=900123456 (puede ser NIT o documento)
# Retorna: empresa existente o {'encontrado': False}
# Útil para auto-completado en el formulario frontend
```

**RESPUESTA ESTÁNDAR**:
```python
# Siempre usar este formato:
return jsonify({
    'success': True,
    'data': empresa.to_dict(),
    'message': 'Empresa registrada exitosamente'
}), 201
```

**VERIFICACIÓN**:
```powershell
# Con servidor corriendo, probar con curl o el script de verificación
& "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\.venv\Scripts\python.exe" -c "
import requests, json
# POST crear empresa jurídica
r = requests.post('http://localhost:5000/api/sst/empresas', 
    json={'tipo_persona': 'JURIDICA', 'nit': '900123456', 'razon_social': 'TEST EMPRESA SAS'},
    cookies={'session': 'OBTENER_TOKEN_PRIMERO'})
print(r.status_code, r.json())
"
```

**COMMIT**:
```bash
git add backend/app/routes/sst.py
git commit -m "feat: API CRUD empresas contratistas - CHECKPOINT 3.2.2"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.3 — API Empleados Contratistas + Certificados

### Qué hacer

Agregar al final de `backend/app/routes/sst.py`:

**ENDPOINTS EMPLEADOS**:
```
GET    /api/sst/empleados                    — listar (filtro: empresa_id, estado)
POST   /api/sst/empleados                    — crear empleado
GET    /api/sst/empleados/<id>               — detalle empleado + sus certificados vigentes
PUT    /api/sst/empleados/<id>               — actualizar empleado
GET    /api/sst/empleados/buscar             — buscar por ?tipo=CC&num=12345678
```

**ENDPOINTS CERTIFICADOS**:
```
GET    /api/sst/certificados                          — listar (filtro: empleado_id, tipo, vigente)
POST   /api/sst/certificados                          — registrar certificado para un empleado
GET    /api/sst/certificados/empleado/<empleado_id>   — certificados de un empleado
PUT    /api/sst/certificados/<id>                     — actualizar certificado
```

**LÓGICA CRÍTICA — Certificado próximo a vencer**:
```python
from datetime import date, timedelta

def estado_vigencia(fecha_vencimiento):
    """Retorna estado de vigencia del certificado"""
    hoy = date.today()
    if fecha_vencimiento < hoy:
        return 'VENCIDO'
    elif fecha_vencimiento <= hoy + timedelta(days=30):
        return 'PROXIMO_VENCER'  # Alerta visual en frontend
    return 'VIGENTE'
```

**LÓGICA CRÍTICA — Buscar empleado**:
```python
# GET /api/sst/empleados/buscar?tipo=CC&num=12345678
# Si encuentra: retorna empleado + empresa + certificados vigentes
# Si no encuentra: retorna {'encontrado': False}
# Útil para auto-completar formularios de autorización SST
```

**COMMIT**:
```bash
git add backend/app/routes/sst.py
git commit -m "feat: API empleados contratistas + certificados - CHECKPOINT 3.2.3"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.4 — API Planillas de Seguridad Social

### Qué hacer

Agregar al final de `backend/app/routes/sst.py`:

**ENDPOINTS PLANILLAS**:
```
GET    /api/sst/planillas                         — listar (filtro: empresa_id, vigente)
POST   /api/sst/planillas                         — registrar planilla
GET    /api/sst/planillas/<id>                    — detalle planilla
GET    /api/sst/planillas/empresa/<empresa_id>    — planillas de una empresa
GET    /api/sst/planillas/vigentes/<empresa_id>   — solo planillas vigentes hoy
```

**LÓGICA CRÍTICA — Cálculo de vigencia**:
```python
from datetime import date, timedelta

# En POST /api/sst/planillas:
# vigencia_hasta = fecha_pago + 30 días (automático, no lo envía el usuario)
data = request.get_json()
fecha_pago = date.fromisoformat(data['fecha_pago'])
vigencia_hasta = fecha_pago + timedelta(days=30)
```

**LÓGICA CRÍTICA — Validación de observaciones**:
```python
# Si aporta_salud=False  → observacion_salud obligatorio
# Si aporta_pension=False → observacion_pension obligatorio
# Si aporta_arl=False    → observacion_arl obligatorio
def validar_planilla(data):
    for campo in ('salud', 'pension', 'arl'):
        if not data.get(f'aporta_{campo}', True):
            if not data.get(f'observacion_{campo}'):
                return False, f'observacion_{campo} requerido cuando aporta_{campo}=False'
    return True, None
```

**COMMIT**:
```bash
git add backend/app/routes/sst.py
git commit -m "feat: API planillas seguridad social + vigencia automatica - CHECKPOINT 3.2.4"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.5 — API Autorizaciones SST (con consecutivo)

### Qué hacer

Este es el endpoint más complejo. Agregar al final de `backend/app/routes/sst.py`.

**ENDPOINTS**:
```
GET    /api/sst/autorizaciones                        — listar (filtro: estado, sede_id, empresa_id)
POST   /api/sst/autorizaciones                        — crear en BORRADOR + generar consecutivo
GET    /api/sst/autorizaciones/<id>                   — detalle completo con empleados
PUT    /api/sst/autorizaciones/<id>                   — actualizar (solo estado=BORRADOR)
POST   /api/sst/autorizaciones/<id>/empleados         — agregar empleado a autorización
DELETE /api/sst/autorizaciones/<id>/empleados/<eid>   — quitar empleado de autorización
POST   /api/sst/autorizaciones/<id>/enviar-revision   — BORRADOR → REVISION
POST   /api/sst/autorizaciones/<id>/aprobar           — REVISION → APROBADA (admin_sst / master)
POST   /api/sst/autorizaciones/<id>/rechazar          — REVISION → RECHAZADA (requiere motivo)
POST   /api/sst/autorizaciones/<id>/anular            — APROBADA → ANULADA (solo master)
```

**LÓGICA CRÍTICA — Generación de consecutivo** (CP314-01):
```python
from sqlalchemy import text, extract
from datetime import date

def generar_consecutivo_sst():
    """Genera número de autorización SST único.
    Formato: SST-{AÑO}-{CONSECUTIVO:04d}
    Ejemplo: SST-2026-0001, SST-2026-0002, ...
    El consecutivo reinicia cada año.
    """
    anio = date.today().year
    
    # Buscar el mayor consecutivo del año actual
    resultado = db.session.execute(text("""
        SELECT MAX(CAST(SPLIT_PART(numero_autorizacion, '-', 3) AS INTEGER))
        FROM autorizaciones_sst
        WHERE numero_autorizacion LIKE :patron
    """), {'patron': f'SST-{anio}-%'}).scalar()
    
    siguiente = (resultado or 0) + 1
    return f"SST-{anio}-{siguiente:04d}"
```

**LÓGICA CRÍTICA — Transiciones de estado**:
```python
TRANSICIONES_VALIDAS = {
    'BORRADOR':  ['REVISION'],
    'REVISION':  ['APROBADA', 'RECHAZADA'],
    'APROBADA':  ['VENCIDA', 'ANULADA'],
    'RECHAZADA': [],  # Estado final
    'VENCIDA':   [],  # Estado final
    'ANULADA':   [],  # Estado final
}

def puede_transitar(estado_actual, estado_nuevo, rol_usuario):
    """Valida si la transición de estado es permitida para el rol dado"""
    if estado_nuevo not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        return False, f"No se puede pasar de {estado_actual} a {estado_nuevo}"
    
    # Solo master puede anular
    if estado_nuevo == 'ANULADA' and rol_usuario != 'usuario_master':
        return False, "Solo el master puede anular una autorización"
    
    # Solo admin_sst o master pueden aprobar/rechazar
    if estado_nuevo in ('APROBADA', 'RECHAZADA') and rol_usuario not in ('admin_sst', 'usuario_master'):
        return False, "Solo admin_sst o master pueden aprobar/rechazar"
    
    return True, None
```

**LÓGICA CRÍTICA — Verificar vigencia automática** (tarea para GET /autorizaciones):
```python
from datetime import date

def marcar_vencidas():
    """Marca como VENCIDAS las autorizaciones cuya vigencia_fin ya pasó"""
    from app.models.autorizacion_sst import AutorizacionSST
    vencidas = AutorizacionSST.query.filter(
        AutorizacionSST.estado == 'APROBADA',
        AutorizacionSST.vigencia_fin < date.today()
    ).all()
    for auth in vencidas:
        auth.estado = 'VENCIDA'
    if vencidas:
        db.session.commit()
    return len(vencidas)
```

**COMMIT**:
```bash
git add backend/app/routes/sst.py
git commit -m "feat: API autorizaciones SST + consecutivo + transiciones estado - CHECKPOINT 3.2.5"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.6 — API Ingresos Contratistas

### Qué hacer

Agregar al final de `backend/app/routes/sst.py`:

**ENDPOINTS**:
```
GET    /api/sst/ingresos           — ingresos del día (filtro: sede_id, estado)
POST   /api/sst/ingresos           — registrar ingreso de empleado contratista
PUT    /api/sst/ingresos/<id>/salida — registrar salida
GET    /api/sst/ingresos/activos   — empleados actualmente en instalaciones
```

**LÓGICA CRÍTICA — Validaciones antes de registrar ingreso**:
```python
# En POST /api/sst/ingresos, ANTES de insertar, verificar:

# 1. Autorización existe y está APROBADA
autorizacion = AutorizacionSST.query.get(data['autorizacion_sst_id'])
if not autorizacion or autorizacion.estado != 'APROBADA':
    return jsonify({'success': False, 'message': 'Autorización no válida o no aprobada'}), 400

# 2. Autorización no está vencida
if autorizacion.vigencia_fin < date.today():
    # Marcar como vencida y rechazar
    autorizacion.estado = 'VENCIDA'
    db.session.commit()
    return jsonify({'success': False, 'message': 'Autorización SST vencida'}), 400

# 3. El empleado está incluido en esa autorización
# (verificar en tabla empleados_por_autorizacion o similar)

# 4. El empleado no tiene ya un ingreso activo (EN_INSTALACIONES)
ingreso_activo = LogIngresoContratista.query.filter_by(
    empleado_id=data['empleado_id'],
    estado_ingreso='EN_INSTALACIONES'
).first()
if ingreso_activo:
    return jsonify({'success': False, 'message': 'Empleado ya se encuentra en instalaciones'}), 400
```

**LÓGICA CRÍTICA — Registrar salida**:
```python
# En PUT /api/sst/ingresos/<id>/salida:
# estado_ingreso: EN_INSTALACIONES → SALIO (irreversible)
# Registrar: fecha_salida, hora_salida, operador_salida_id, observaciones_salida
```

**COMMIT**:
```bash
git add backend/app/routes/sst.py
git commit -m "feat: API ingresos/salidas contratistas + validaciones - CHECKPOINT 3.2.6"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

## CHECKPOINT 3.2.7 — Validación Final FASE 3.2

### Qué hacer

Verificar que todos los endpoints funcionan y hacer push.

**VERIFICACIÓN COMPLETA**:

```powershell
# 1. Verificar que el servidor arranca sin errores
cd backend
& "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\.venv\Scripts\python.exe" run.py &
Start-Sleep -Seconds 3

# 2. Verificar rutas registradas
& "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\.venv\Scripts\python.exe" -c "
from app import create_app
app = create_app()
with app.app_context():
    rutas = sorted([str(r) for r in app.url_map.iter_rules() if '/api/sst' in str(r)])
    print(f'Total rutas SST: {len(rutas)}')
    for r in rutas: print(f'  {r}')
"
```

**RUTAS ESPERADAS** (mínimo):
```
/api/sst/health
/api/sst/operadores
/api/sst/empresas
/api/sst/empresas/buscar
/api/sst/empresas/<int:empresa_id>
/api/sst/empleados
/api/sst/empleados/buscar
/api/sst/empleados/<int:empleado_id>
/api/sst/certificados
/api/sst/certificados/empleado/<int:empleado_id>
/api/sst/planillas
/api/sst/planillas/empresa/<int:empresa_id>
/api/sst/planillas/vigentes/<int:empresa_id>
/api/sst/autorizaciones
/api/sst/autorizaciones/<int:aut_id>
/api/sst/autorizaciones/<int:aut_id>/empleados
/api/sst/autorizaciones/<int:aut_id>/enviar-revision
/api/sst/autorizaciones/<int:aut_id>/aprobar
/api/sst/autorizaciones/<int:aut_id>/rechazar
/api/sst/autorizaciones/<int:aut_id>/anular
/api/sst/ingresos
/api/sst/ingresos/activos
/api/sst/ingresos/<int:ingreso_id>/salida
```

**PUSH FINAL**:
```bash
git push origin feature/modulo-sst
```

**COMMIT FINAL** (si hizo cambios de verificación):
```bash
git add .
git commit -m "feat: FASE 3.2 completa - API REST modulo SST - CHECKPOINT 3.2.7"
git push origin feature/modulo-sst
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[FASE 3.2 COMPLETA - ESPERANDO VALIDACIÓN CLAUDE]`

---

## RESUMEN FASE 3.2

| Checkpoint | Descripción | Commit mensaje |
|---|---|---|
| 3.2.0 | Fix hallazgos FASE 3.1 (constraints + índices) | fix: hallazgos FASE 3.1 |
| 3.2.1 | Blueprint SST + roles + endpoint operadores | feat: blueprint SST |
| 3.2.2 | CRUD empresas contratistas | feat: API empresas |
| 3.2.3 | Empleados + Certificados | feat: API empleados + certificados |
| 3.2.4 | Planillas seguridad social | feat: API planillas SS |
| 3.2.5 | Autorizaciones SST + consecutivo | feat: API autorizaciones SST |
| 3.2.6 | Ingresos/salidas contratistas | feat: API ingresos contratistas |
| 3.2.7 | Validación final + push | feat: FASE 3.2 completa |

**NOTAS IMPORTANTES**:
- Cada checkpoint debe ser `[APROBADO]` antes de avanzar al siguiente
- El archivo `sst.py` se va construyendo incrementalmente — no reescribir todo en cada checkpoint
- Los modelos ya existen desde FASE 3.1 — importar desde `app.models.*`
- Seguir el patrón de respuesta JSON: `{'success': bool, 'data': ..., 'message': str}`
- Siempre usar `@login_required` + `@role_required(*ROLES_SST)` en todos los endpoints
- Para endpoints de solo admin: usar `@role_required(*ROLES_ADMIN_SST)`

---

### CHECKPOINT 3.1.5: Modelos SQLAlchemy (8 modelos) ⏱️ 4-5 horas

**QUÉ VAS A HACER**: Crear los 8 modelos SQLAlchemy correspondientes a las tablas del módulo SST.

**ARCHIVOS A CREAR** (en `backend/app/models/`):
1. `operador_aportes.py`
2. `empresa_contratista.py`
3. `empleado_contratista.py`
4. `certificado_trabajo.py`
5. `planilla_ss.py`
6. `autorizacion_sst.py`
7. `log_ingreso_contratista.py`

**EJEMPLO MODELO REFERENCIA** (`empresa_contratista.py`):
```python
from app.extensions import db
from datetime import datetime

class EmpresaContratista(db.Model):
    __tablename__ = 'empresas_contratistas'

    id                  = db.Column(db.Integer, primary_key=True)
    razon_social        = db.Column(db.String(200), nullable=False)
    nit                 = db.Column(db.String(20),  nullable=False, unique=True)
    digito_verificacion = db.Column(db.String(1),   nullable=False)
    representante_legal = db.Column(db.String(150), nullable=False)
    telefono            = db.Column(db.String(20))
    email               = db.Column(db.String(100))
    direccion           = db.Column(db.String(200))
    ciudad              = db.Column(db.String(100))
    estado              = db.Column(db.String(20),  nullable=False, default='activa')
    created_at          = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by          = db.Column(db.Integer,     db.ForeignKey('usuarios.id'))

    # Relaciones
    empleados      = db.relationship('EmpleadoContratista', back_populates='empresa', lazy='dynamic')
    planillas      = db.relationship('PlanillaSS',          back_populates='empresa', lazy='dynamic')
    autorizaciones = db.relationship('AutorizacionSST',     back_populates='empresa', lazy='dynamic')

    def to_dict(self):
        return {
            'id':                  self.id,
            'razon_social':        self.razon_social,
            'nit':                 self.nit,
            'digito_verificacion': self.digito_verificacion,
            'representante_legal': self.representante_legal,
            'telefono':            self.telefono,
            'email':               self.email,
            'direccion':           self.direccion,
            'ciudad':              self.ciudad,
            'estado':              self.estado,
            'created_at':          self.created_at.isoformat() if self.created_at else None,
        }
```

**SEGUIR EL MISMO PATRÓN** para los otros 6 modelos. Basarse en los modelos existentes del proyecto.

Una vez creados los 7 modelos, **registrarlos en** `backend/app/models/__init__.py`:
```python
# Agregar al final de los imports existentes:
from app.models.operador_aportes       import OperadorAportes
from app.models.empresa_contratista    import EmpresaContratista
from app.models.empleado_contratista   import EmpleadoContratista
from app.models.certificado_trabajo    import CertificadoTrabajo
from app.models.planilla_ss            import PlanillaSS
from app.models.autorizacion_sst       import AutorizacionSST
from app.models.log_ingreso_contratista import LogIngresoContratista
```

**COMMIT**:
```bash
git add backend/app/models/
git commit -m "feat: crear 7 modelos SQLAlchemy módulo SST - CHECKPOINT 3.1.5"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CORRECCIÓN OBLIGATORIA 3.1.5A: `nit` nullable para Persona Natural

**ESTA CORRECCIÓN ES OBLIGATORIA ANTES DE 3.1.6.**

HALLAZGO-CP315-01: el campo `nit` en `empresas_contratistas` está definido como `NOT NULL UNIQUE`. Una Persona Natural no tiene NIT — solo tiene `num_identificacion`. Insertar una Persona Natural fallará en BD.

**ARCHIVO A CREAR**: `backend/migrate_alter_empresas_nit_nullable.py`

**CÓDIGO EXACTO**:
```python
"""
Migración: Hacer nit nullable en empresas_contratistas para Persona Natural
Fecha: 2026-03-19
Checkpoint: 3.1.5A
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text


def migrate():
    app = create_app()
    with app.app_context():
        print("Ajustando nit en empresas_contratistas para Persona Natural...")

        # 1. Quitar NOT NULL a nit
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ALTER COLUMN nit DROP NOT NULL;
        """))

        # 2. Eliminar el UNIQUE global de nit (no funciona con valores NULL)
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS empresas_contratistas_nit_key;
        """))

        # 3. Índice único parcial: nit único solo para Persona Jurídica
        db.session.execute(text("""
            DROP INDEX IF EXISTS idx_empresa_nit_juridica;
        """))
        db.session.execute(text("""
            CREATE UNIQUE INDEX idx_empresa_nit_juridica
            ON empresas_contratistas(nit)
            WHERE tipo_persona = 'JURIDICA'
              AND nit IS NOT NULL;
        """))

        # 4. Constraint: Persona Jurídica DEBE tener nit,
        #               Persona Natural DEBE tener num_identificacion
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            DROP CONSTRAINT IF EXISTS check_identificacion_por_tipo_persona;
        """))
        db.session.execute(text("""
            ALTER TABLE empresas_contratistas
            ADD CONSTRAINT check_identificacion_por_tipo_persona CHECK (
                (tipo_persona = 'JURIDICA' AND nit IS NOT NULL)
                OR
                (tipo_persona = 'NATURAL' AND num_identificacion IS NOT NULL)
            );
        """))

        db.session.commit()
        print("✅ nit ahora nullable con índice parcial para Persona Jurídica")


def rollback():
    app = create_app()
    with app.app_context():
        db.session.execute(text("ALTER TABLE empresas_contratistas DROP CONSTRAINT IF EXISTS check_identificacion_por_tipo_persona;"))
        db.session.execute(text("DROP INDEX IF EXISTS idx_empresa_nit_juridica;"))
        db.session.execute(text("ALTER TABLE empresas_contratistas ADD CONSTRAINT empresas_contratistas_nit_key UNIQUE (nit);"))
        db.session.execute(text("ALTER TABLE empresas_contratistas ALTER COLUMN nit SET NOT NULL;"))
        db.session.commit()
        print("✅ Rollback ejecutado")


if __name__ == '__main__':
    migrate()
```

**DESPUÉS**:
```powershell
python backend/migrate_alter_empresas_nit_nullable.py
```

**VERIFICAR**:
```powershell
# Verificar que nit ahora es nullable
& "d:/0.A. Proyectos/1.1. Control de Acceso Visitantes/.venv/Scripts/python.exe" -c "from app import create_app; from app.extensions import db; from sqlalchemy import text; app=create_app(); ctx=app.app_context(); ctx.push(); r=db.session.execute(text(\"SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='empresas_contratistas' AND column_name='nit'\")).fetchone(); print(r)"
# Esperado: ('nit', 'YES')
```

**COMMIT**:
```bash
git add backend/migrate_alter_empresas_nit_nullable.py
git commit -m "fix: nit nullable + indice parcial Persona Juridica - CHECKPOINT 3.1.5A"
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md → `[ESPERANDO VALIDACIÓN CLAUDE]`

---

### CHECKPOINT 3.1.6: Validación FASE 3.1 completa ⏱️ 1 hora

**QUÉ VAS A HACER**: Verificar que todas las tablas y modelos SST están correctos.

**CHECKLIST**:
```powershell
# 1. Verificar las 8 tablas en DB
psql -U postgres -d control_visitantes -c "\dt" | Select-String "operadores|empresas|empleados|certificados|planillas|autorizaciones|log_ingresos"
# Esperado: 8 tablas listadas

# 2. Verificar seeder operadores (13 registros)
psql -U postgres -d control_visitantes -c "SELECT tipo, COUNT(*) FROM operadores_aportes GROUP BY tipo;"
# Esperado: ARL=4, AFP=4, EPS=5

# 3. Verificar servidor arranca con modelos nuevos
python backend/run.py
# Ctrl+C para detener
# No debe haber errores de import

# 4. Verificar tests existentes siguen pasando
pytest backend/tests/ -v
```

**COMMIT**:
```bash
git add .
git commit -m "feat: FASE 3.1 completa - 8 tablas SST + 7 modelos SQLAlchemy"
git push origin feature/modulo-sst
```

**AL TERMINAR**: Actualiza COPILOT_TASKS.md con resumen FASE 3.1 → `[FASE 3.1 COMPLETA - ESPERANDO APROBACIÓN CLAUDE]`

---

### ⏸️ DESPUÉS DE FASE 3.1

Una vez que Claude apruebe FASE 3.1, @evaluador agregará instrucciones para FASE 3.2 (Endpoints básicos CRUD) en este mismo archivo.

**NO implementes FASE 3.2 todavía.** Espera las instrucciones.

---

## 📊 ESTADO ACTUAL

**EJECUTAR AHORA**: PASO 1 (FASE 1) - 5-8 horas

**Siguiente paso después de PASO 1**: PASO 2 (Preparación) - 2-3 días

**Después de PASO 2**: Decisión del usuario sobre Módulo SST

---

## 🆘 SI ALGO FALLA

**Error durante migración**:
```powershell
# Ejecutar función rollback del archivo
python -c "from migrate_add_roles_sst import rollback; from app import create_app; app = create_app(); app.app_context().push(); rollback()"
```

**Error en tests**:
1. Lee el mensaje de error completo
2. Escribe en COPILOT_TASKS.md sección [COPILOT EJECUTOR] el error exacto
3. Marca `[❌ ERROR - ESPERANDO AYUDA]`
4. Claude o @evaluador te ayudarán

**Pregunta sobre instrucciones**:
1. Escribe en COPILOT_TASKS.md sección [COPILOT EJECUTOR]
2. Marca `[❓ PREGUNTA]`
3. Espera respuesta

---

## 📝 RECORDATORIOS

- ✅ **Siempre commit con mensajes descriptivos**
- ✅ **Siempre ejecutar tests después de cambios**
- ✅ **Siempre actualizar COPILOT_TASKS.md después de checkpoint**
- ✅ **NO avanzar sin `[✅ APROBADO]` de Claude**
- ✅ **Si algo falla, ejecutar rollback inmediatamente**

---

**¡Listo para empezar! 🚀**

Espera la señal del usuario para iniciar PASO 1.
