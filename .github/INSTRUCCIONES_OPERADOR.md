# INSTRUCCIONES PARA COPILOT @operador
# Implementación Módulo SST — Sistema Control Visitantes

> **TU ROL**: Ejecutor / Implementador
> **TU JEFE**: Copilot @evaluador (coordina con Claude auditor)
> **TU TRABAJO**: Implementar código según este plan paso a paso
> **REGLA DE ORO**: NO avances al siguiente checkpoint hasta que veas `[✅ APROBADO]` en `.github/COPILOT_TASKS.md`

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

### 📝 Formato de Actualización en COPILOT_TASKS.md

Después de cada checkpoint, escribí esto en `.github/COPILOT_TASKS.md` sección `[COPILOT EJECUTOR]`:

```markdown
---
CHECKPOINT X.Y.Z - [Título]
Fecha: 2026-03-19 14:30
Commit: abc1234

QUÉ HICE:
- Creé archivo migrate_add_indices_visitantes.py
- Ejecuté migración: 3 índices creados
- Corrí tests de verificación

ARCHIVOS MODIFICADOS/CREADOS:
- backend/migrate_add_indices_visitantes.py (nuevo)

TESTS EJECUTADOS:
```powershell
python backend/migrate_add_indices_visitantes.py
# Resultado: ✅ Índices creados exitosamente

psql -U postgres -d control_visitantes -c "\d visitantes"
# Resultado: ✅ idx_visitante_identificacion existe
```

COMMIT:
```bash
git add backend/migrate_add_indices_visitantes.py
git commit -m "feat: agregar índices optimización búsquedas visitantes (CHECKPOINT 1.1)"
git push origin feature/modulo-sst
```

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

### ⚠️ ADVERTENCIA

**PASO 3 es LARGO** (80-120 días hábiles).

Las instrucciones completas de las 7 fases (3.1 a 3.7) se agregarán progresivamente.

**POR AHORA**: DETENTE al completar PASO 2 y espera indicaciones del usuario.

**PRÓXIMOS PASOS**:
1. Usuario decide si continuar inmediatamente con Módulo SST
2. Copilot @evaluador actualiza este archivo con instrucciones detalladas de FASE 3.1
3. Tú (Copilot @operador) ejecutas FASE 3.1 cuando se apruebe

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
