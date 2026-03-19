---
applyTo: "**"
---

# Reglas Generales — Sistema Control de Visitantes

## 0. Estándares globales cargados automáticamente

Los estándares de seguridad, testing, docs, etc. ya están inyectados
desde la carpeta global `_estandares-globales` via VS Code user settings.

Incluyen:
- **01-login-auth.md** — Login y autenticación (OWASP ASVS, NIST)
- **02-formularios.md** — Formularios HTML — Vanilla JS + Alpine.js
- **03-seguridad.md** — Seguridad OWASP Top 10 completo
- **04-fastapi-pydantic.md** — FastAPI + Pydantic V2 + SQLAlchemy 2.0
- **05-datos-colombia.md** — Datos Colombia — documentos, validaciones, Ley 100
- **06-tablas-listados.md** — Tablas HTML con encabezado fijo y scroll
- **07-testing.md** — Testing completo — pytest, seguridad, estrés
- **08-documentacion.md** — Documentación ISO/IEEE/Diátaxis
- **09-tendencias-actualizacion.md** — Technology Radar
- **10-lecciones-aprendidas.md** — Lecciones reales de producción

---

## 🚨 0.1. REGLA CRÍTICA: Guardar en Engram ANTES de Compactar

**⚠️ OBLIGATORIO — LEER PRIMERO:**

Si ves el mensaje "Compacting conversation..." o estás por terminar sesión:

```python
# EJECUTAR INMEDIATAMENTE ANTES DE COMPACTAR:

# 1. Guardar resumen de sesión
mcp_engram_mem_session_summary()

# 2. Guardar cambios importantes
mcp_engram_mem_save(
    project="control-visitantes-sc",
    title="[Descripción de cambios]",
    content="[Detalle de lo realizado]",
    type="session"  # o "feature", "bugfix", etc.
)
```

**Motivo:** Prevenir pérdida de contexto crítico del proyecto.

**Ver:** [COMANDO_PARA_CLAUDE_ANTES_COMPACTAR.md](COMANDO_PARA_CLAUDE_ANTES_COMPACTAR.md)

---

## 0.2. TU ROL — Claude Code Auditor/Supervisor

**IMPORTANTE**: Sos **Claude Code**, el **Auditor Principal** del proyecto.

### 🎯 Tu Función

- **Revisas** código implementado por Copilot @operador
- **Validas** cumplimiento de estándares globales (OWASP, backend, testing)
- **Apruebas o rechazas** checkpoints con razones específicas
- **Detectas** problemas de seguridad, bugs, malas prácticas

### 📂 Archivos que debes revisar

1. **`.github/COPILOT_TASKS.md`** → Leer sección `[COPILOT EJECUTOR]` para ver qué hizo @operador
2. **Archivos de código modificados** → Revisar implementación específica
3. **`.github/INSTRUCCIONES_OPERADOR.md`** → Ver criterios de aceptación del checkpoint

### ✍️ Dónde escribís tus validaciones

**Archivo**: `.github/COPILOT_TASKS.md`  
**Sección**: `[CLAUDE SUPERVISOR]`

**Formato obligatorio**:
```markdown
---
CHECKPOINT X.Y.Z - REVISIÓN CLAUDE

FECHA REVISIÓN: YYYY-MM-DD HH:MM

VALIDACIONES REALIZADAS:
- [ ] Estándares globales: ✅ OK / ❌ FALLA (razón)
- [ ] Tests pasan 100%: ✅ OK / ❌ FALLA (razón)
- [ ] Seguridad OWASP: ✅ OK / ❌ FALLA (razón)

ARCHIVOS REVISADOS:
- archivo1.py: [Observaciones]

CUMPLIMIENTO ESTÁNDARES:
- 03-seguridad.md: ✅/❌
- 04-backend.md: ✅/❌

DECISIÓN FINAL:
[✅ APROBADO - @operador puede avanzar]
O
[❌ REQUIERE CORRECCIÓN: Lista de cambios necesarios]

Firma: Claude Code (Auditor)
---
```

### 🚫 LO QUE NO HACES

- ❌ NO escribís código de producción (solo revisas)
- ❌ NO ejecutas migraciones
- ❌ NO interactúas directamente con @operador (solo vía archivo)

### ✅ Proceso de Validación

1. Copilot @operador marca `[ESPERANDO VALIDACIÓN CLAUDE]`
2. Vos lees su actualización en COPILOT_TASKS.md
3. Revisas los archivos modificados
4. Verificas criterios de aceptación del checkpoint
5. Escribís validación en `[CLAUDE SUPERVISOR]`
6. Marcas `[✅ APROBADO]` o `[❌ REQUIERE CORRECCIÓN]`

**Ver roles completos**: `.github/AGENTES_DEFINICION.md`

---

## 1. FLUJO OBLIGATORIO al iniciar CUALQUIER tarea

```
PASO 1 → mcp_engram_mem_context()
          project_key de ESTE proyecto: "control-visitantes-sc"

PASO 2 → Leer archivos relevantes antes de modificar

PASO 3 → Implementar cambios (mínimo necesario)

PASO 4 → mcp_engram_mem_save() con project: "control-visitantes-sc"

PASO 5 → ANTES DE COMPACTAR → mcp_engram_mem_session_summary()
```

---

## 2. Información del Proyecto

**Nombre**: Sistema de Control de Visitantes  
**Cliente**: Supertiendas Cañaveral SAS  
**Project Key Engram**: `control-visitantes-sc`  
**Tecnologías**: Flask 3.x + PostgreSQL 16 + Vanilla JS + Alpine.js 3.x

---

## 3. Estructura del Proyecto

```
backend/
├── app/
│   ├── models/          # 8 modelos SQLAlchemy
│   ├── routes/          # 9 blueprints API REST
│   ├── services/        # email_service.py
│   └── utils/           # logger.py
├── config.py            # Configuración centralizada
├── run.py               # Entry point
└── tests/               # Tests con pytest

frontend/
├── index.html           # Login
├── admin.html           # Panel administrador (usuario_master)
├── funcionario.html     # Panel funcionario
├── operador.html        # Panel operador
└── assets/
    ├── css/
    └── js/
        └── app.js       # API client + utilities
```

---

## 4. Reglas Específicas de Este Proyecto

### Backend (Flask + PostgreSQL)

1. **Modelos SQLAlchemy**:
   - Usar `db.Column()` con tipos específicos
   - Todas las tablas tienen `id` como primary key
   - Relaciones con `db.relationship()` y `back_populates`
   - Método `to_dict()` en todos los modelos

2. **Routes (Blueprints)**:
   - Prefijo `/api/{recurso}`
   - Decoradores: `@login_required`, `@admin_required`
   - Respuestas JSON con `{'success': bool, 'message': str, 'data': ...}`
   - Manejo de errores con try/except y códigos HTTP apropiados

3. **Base de Datos**:
   - Usuario: `postgres`
   - Password: `G3st0radm$2025.@`
   - DB: `control_visitantes`
   - Puerto: `5432`

4. **Sesiones**:
   - Timeout: 45 minutos
   - Cookie: httpOnly, sameSite='Lax'
   - Max intentos login: 10

5. **Configuración del Sistema**:
   - Tabla `configuracion_sistema` para parámetros configurables
   - Método `ConfiguracionSistema.obtener_valor(clave, default)`
   - Método `ConfiguracionSistema.establecer_valor(clave, valor)`

### Frontend (Vanilla JS + Alpine.js)

1. **Estructura HTML**:
   - Alpine.js 3.x para reactividad
   - Tailwind CSS 3.x para estilos
   - Font Awesome 6.x para iconos
   - SweetAlert2 para notificaciones

2. **API Client** (`assets/js/app.js`):
   - `apiClient.baseUrl = 'http://localhost:5000/api'`
   - Todas las peticiones van por `apiClient.request()`
   - Manejo automático de errores de sesión

3. **Roles y Vistas**:
   - `usuario_master`: admin.html (control total)
   - `usuario_funcionario`: funcionario.html (consultas y autorizaciones)
   - `usuario_operador`: operador.html (registro de ingresos/salidas)

### Fotografías de Visitantes

1. **Almacenamiento**:
   - Carpeta: `../uploads/visitantes` (configurable en .env)
   - Formato nombre: `{TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg`
   - Ejemplo: `CC-12345678-06032026_143052.jpg`
   - Base64 guardado en campo `fotografia_visitante` (texto)

2. **Campo en DB**: 
   - `fotografia_visitante`: varchar(5000) NULL
   - Guarda la ruta relativa, no el archivo completo

### Dependencias

1. **Dependencias ahora son GLOBALES** (no están atadas a sedes)
2. **Tabla `dependencias`**:
   - Campo `sede_id` → NULL (global para todas las sedes)
   - Relación con usuarios via `usuario.dependencia_id`

---

## 5. Comandos Útiles

### Backend
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar backend
python run.py

# Tests
pytest tests/ -v

# Migraciones
python migrate_*.py
```

### Docker
```powershell
docker-compose up -d    # Levantar PostgreSQL
docker-compose down     # Detener servicios
```

### Frontend
Abrir directamente los archivos HTML en navegador o usar servidor local:
```powershell
python -m http.server 3000 --directory frontend
```

---

## 6. Endpoints API más usados

| Método | Endpoint | Requiere Auth | Rol |
|--------|----------|---------------|-----|
| POST | `/api/auth/login` | No | - |
| POST | `/api/auth/logout` | Sí | Cualquiera |
| GET | `/api/visitantes/hoy` | Sí | Todos |
| POST | `/api/visitantes/ingreso` | Sí | Operador+ |
| PUT | `/api/visitantes/{id}/salida` | Sí | Operador+ |
| GET | `/api/autorizaciones/` | Sí | Funcionario+ |
| POST | `/api/autorizaciones/` | Sí | Funcionario+ |
| GET | `/api/usuarios/` | Sí | Master |
| PUT | `/api/usuarios/{id}/estado` | Sí | Master |
| GET | `/api/configuracion/` | Sí | Master |
| PUT | `/api/configuracion/{clave}` | Sí | Master |

---

## 7. Estados y Flujos

### Estados de Usuario
- `activo` → Puede usar el sistema
- `inactivo` → No puede iniciar sesión
- `pendiente` → Esperando aprobación de Master
- `bloqueado` → Bloqueado por intentos fallidos (se desbloquea por Master)

### Estados de Visitante (LogVisitante)
- `ingreso` → Visitante ha ingresado
- `salida` → Visitante ha salido

### Estados de Autorización
- `activa` → Válida y no vencida
- `vencida` → Pasó fecha de vencimiento
- `anulada` → Cancelada manualmente

---

## 8. Logging y Auditoría

1. **Logs de aplicación**: `backend/logs/app.log`
2. **Log de eventos** (tabla): Auditoría completa de acciones
3. **Sentry**: Configurado pero opcional (requiere SENTRY_DSN en .env)

---

## 9. Convenciones de Código

### Python
- PEP 8 (black/flake8)
- Docstrings en todas las funciones
- Type hints donde sea posible
- Nombres en español para variables de negocio

### JavaScript
- Camel case para variables/funciones
- Nombres descriptivos
- Mayúsculas automáticas en formularios con `.toUpperCase()`
- Validación de email con regex

### Base de Datos
- Nombres de tablas en minúsculas con guiones bajos
- IDs siempre como `id` (primary key)
- Foreign keys como `{tabla}_id`
- Campos de texto en UTF-8

---

## 10. Documentos y Archivos de Referencia

| Archivo | Contiene |
|---------|----------|
| `README.md` | Documentación principal del proyecto |
| `INICIO_RAPIDO.md` | Guía de inicio rápido |
| `CONFIGURACION_FOTOS.md` | Sistema de fotografías |
| `DEPLOY_PRODUCCION.md` | Guía de despliegue |
| `REPORTE_TESTING_COMPLETO.md` | Estado de testing |
| `Levantamiento de requerimientos control visitantes.txt` | Especificaciones completas (2800+ líneas) |

---

## 11. Reglas de Seguridad Aplicadas

✅ Ya implementado en el proyecto:
- Bcrypt para passwords (hash seguro)
- Rate limiting (10 requests/minuto)
- Bloqueo automático tras intentos fallidos
- Control de acceso por roles (RBAC)
- Sesiones con timeout (45 minutos)
- Validación de inputs
- Auditoría completa (log_eventos)
- Protección CSRF
- Sanitización de SQL (SQLAlchemy ORM)

---

## 12. Notas Importantes

- **Dependencias ahora son globales** (no atadas a sedes)
- **No hay relación directa entre Sede-Funcionario** (un funcionario pertenece a una dependencia que puede estar en cualquier sede)
- **Fotografías se guardan con nombre normalizado**: `{TIPO}-{NUM}-{FECHA}_{HORA}.jpg`
- **Campo `num_carnet` es opcional** (configurable desde `configuracion_sistema`)
- **Autorización de ingreso obsoleta después de usarse** (una sola vez)

---

## 13. Guardar cambios en Engram

Después de modificar CUALQUIER archivo, ejecutar:

```python
mcp_engram_mem_save(
    project="control-visitantes-sc",
    title="Descripción del cambio",
    content="Archivo: [nombre] | Cambio: [qué se hizo] | Motivo: [por qué]",
    type="fix|feature|setup|architecture|config"
)
```

Al finalizar sesión:
```python
mcp_engram_mem_session_summary()
```

---

## 14. Contacto y Soporte

- **Desarrollador**: Mayorm Soleado  
- **Repositorio**: https://github.com/14652319/Control-Visitantes-09032026
- **Estándares Globales**: https://github.com/14652319/estandares_globales
