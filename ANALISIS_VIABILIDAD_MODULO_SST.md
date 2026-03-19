# ANÁLISIS DE VIABILIDAD: Módulo SST para Gestión de Contratistas

**Fecha**: 19 de Marzo de 2026  
**Analista**: GitHub Copilot  
**Proyecto**: Control de Visitantes - Supertiendas Cañaveral  
**Documento fuente**: Levantamiento de requerimientos control visitantes.txt (líneas 3090-5782)

---

## 📋 RESUMEN EJECUTIVO

### Alcance del Requerimiento
Módulo completo para gestión de **contratistas** con validaciones de seguridad social obligatorias (Ley 100 Colombia), certificaciones de trabajo especializado, y generación de autorizaciones oficiales en PDF.

### Veredicto
✅ **VIABLE Y BIEN DISEÑADO** con las siguientes condiciones:
- Requiere backup completo antes de iniciar
- Implementación por fases iterativas (no todo de una vez)
- Testing extensivo en cada fase
- Capacitación previa del personal

### Tiempo Estimado Real
**80-120 días hábiles** (16-24 semanas)
- Documento estima: 48-68 días (SUBESTIMADO)
- Realista: 80-120 días considerando testing y ajustes

---

## 1⃣ CUMPLIMIENTO CON REGLAS GLOBALES

### ✅ Seguridad (OWASP ASVS + Estándar 03-seguridad.md)

| Criterio | Cumple | Observaciones |
|----------|--------|---------------|
| **Autenticación** | ✅ SÍ | Usa sistema existente (bcrypt, sesiones, rate limiting) |
| **Autorización RBAC** | ✅ SÍ | 2 roles nuevos bien definidos con permisos granulares |
| **Validación de inputs** | ✅ SÍ | Validaciones Pydantic para todas las entradas |
| **Protección CSRF** | ✅ SÍ | Heredado del sistema actual |
| **SQL Injection** | ✅ SÍ | SQLAlchemy ORM con parámetros preparados |
| **File upload seguro** | ⚠️ PARCIAL | Requiere validación adicional (ver recomendaciones) |
| **Auditoría** | ✅ SÍ | Log completo en `log_eventos` |
| **Sesiones seguras** | ✅ SÍ | httpOnly, timeout 45 min |
| **Principio mínimo privilegio** | ✅ SÍ | admin_sst NO puede gestionar usuarios, operador_seguridad solo registro |

**Hallazgos de Seguridad**:
- ✅ Separación de responsabilidades bien implementada
- ✅ No hay acceso directo a DB desde frontend
- ⚠️ Falta validación de extensiones y tamaño de archivos PDF
- ⚠️ Falta validación de mime-type real (no solo extensión)

---

### ✅ Backend (FastAPI/Flask + Estándar 04-fastapi-pydantic.md)

| Criterio | Cumple | Observaciones |
|----------|--------|---------------|
| **Modelos Pydantic V2** | ⚠️ N/A | Se especifica SQLAlchemy ORM, proyecto usa Flask no FastAPI |
| **SQLAlchemy 2.0** | ✅ SÍ | Uso correcto de db.Column, relaciones, índices |
| **Validaciones** | ✅ SÍ | CHECK constraints, UNIQUE constraints, validaciones de negocio |
| **Relaciones correctas** | ✅ SÍ | Foreign keys bien definidas con ON DELETE CASCADE apropiado |
| **Índices optimizados** | ✅ SÍ | Índices en columnas de búsqueda frecuente |
| **Campos calculados** | ✅ SÍ | Campo `vigente` como GENERATED ALWAYS AS |
| **Auditoría** | ✅ SÍ | fecha_creacion, fecha_modificacion, usuario_registro_id |

**Hallazgos Técnicos**:
- ✅ Diseño de DB normalizado (3NF)
- ✅ Constraints de integridad referencial correctos
- ✅ Catálogo de operadores (EPS/AFP/ARL) separado y pre-cargado
- ⚠️ Requiere migración de `usuarios.rol` a VARCHAR(50) con nuevo CHECK constraint

---

### ✅ Datos Colombia (Estándar 05-datos-colombia.md)

| Criterio | Cumple | Observaciones |
|----------|--------|---------------|
| **Tipos de documento** | ✅ SÍ | CC, CE, TI, PAS, NIT |
| **Validación NIT** | ⚠️ PARCIAL | Guarda dígito verificación pero no lo valida automáticamente |
| **Ley 100 (Seguridad Social)** | ✅ SÍ | Implementa EPS, AFP, ARL correctamente |
| **Vigencia planillas** | ✅ SÍ | 30 días post-pago (correcto según normativa) |
| **Operadores certificados** | ✅ SÍ | Catálogo de operadores oficiales |

**Hallazgos Normativos**:
- ✅ Cumple Ley 100/1993 (seguridad social)
- ✅ Cumple Resolución 4272/2021 (trabajo en alturas)
- ⚠️ Falta validación automática de NIT con dígito verificador (algoritmo bien conocido)

---

### ✅ Frontend (Estándar 02-formularios.md + 06-tablas-listados.md)

| Criterio | Cumple | Observaciones |
|----------|--------|---------------|
| **Vanilla JS + Alpine.js** | ✅ SÍ | Consistente con sistema actual |
| **Formularios accesibles** | ✅ SÍ | Labels, placeholders, validación HTML5 |
| **Auto-guardado** | ✅ SÍ | LocalStorage cada 30s para formularios largos |
| **Tablas con scroll** | ✅ SÍ | Encabezado fijo, scroll vertical |
| **Filtros y búsqueda** | ✅ SÍ | Filtros por estado, empresa, sede, fecha |

---

### ✅ Testing (Estándar 07-testing.md)

| Criterio | Cumple | Observaciones |
|----------|--------|---------------|
| **Tests unitarios** | ⚠️ PENDIENTE | Documento no especifica tests, deben crearse |
| **Tests de integración** | ⚠️ PENDIENTE | Deben crearse para flujos completos |
| **Tests de seguridad** | ⚠️ PENDIENTE | OWASP ZAP, validación de permisos |
| **Tests de carga** | ⚠️ PENDIENTE | Locust para registro masivo de empleados |

**Recomendación**: Crear suite completa de tests antes de desplegar.

---

### ✅ Documentación (Estándar 08-documentacion.md)

| Criterio | Cumple | Observaciones |
|----------|--------|---------------|
| **Documentación técnica** | ✅ SÍ | Documento muy detallado (2692 líneas) |
| **Diagramas** | ✅ SÍ | ASCII art para arquitectura y flujos |
| **Endpoints documentados** | ✅ SÍ | Especificación completa de API |
| **Manual de usuario** | ⚠️ PENDIENTE | Debe crearse para admin_sst y operador_seguridad |

---

## 2⃣ ANÁLISIS DE IMPACTO EN SISTEMA ACTUAL

### ✅ Cero Impacto en Visitantes Estándar

**Arquitectura modular CORRECTA**:
```
┌──────────────────────────────────────────────────────────┐
│                    SISTEMA ACTUAL                         │
│                   (INTACTO - 0% cambios)                  │
├──────────────────────────────────────────────────────────┤
│ ✅ Visitantes estándar → funcionario.html                │
│ ✅ Operador registro → operador.html                     │
│ ✅ Master admin → admin.html                             │
│ ✅ Tablas: visitantes, log_visitantes, autorizaciones    │
│ ✅ Routes: /api/visitantes, /api/autorizaciones          │
└──────────────────────────────────────────────────────────┘
                           │
                           │ (Comparte infraestructura)
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   INFRAESTRUCTURA COMPARTIDA              │
├──────────────────────────────────────────────────────────┤
│ • usuarios (tabla) → +2 roles (admin_sst, operador_seg)  │
│ • sedes (tabla) → Sin cambios                            │
│ • log_eventos (tabla) → Sin cambios                      │
│ • configuracion_sistema (tabla) → Sin cambios            │
│ • email_service.py → Sin cambios                         │
│ • logger.py → Sin cambios                                │
└──────────────────────────────────────────────────────────┘
                           │
                           │ (Módulo nuevo independiente)
                           ▼
┌──────────────────────────────────────────────────────────┐
│                     MÓDULO SST NUEVO                      │
│                  (100% INDEPENDIENTE)                     │
├──────────────────────────────────────────────────────────┤
│ 🆕 Contratistas → admin_sst.html, operador_seguridad.html│
│ 🆕 8 tablas nuevas (empresas, empleados, planillas, etc) │
│ 🆕 Routes: /api/sst/*                                    │
│ 🆕 Servicio: pdf_service.py                              │
└──────────────────────────────────────────────────────────┘
```

### ⚠️ Cambio ÚNICO en Sistema Actual

**ÚNICO punto de modificación**:
```sql
-- Migración: migrate_add_roles_sst.py
ALTER TABLE usuarios ALTER COLUMN rol TYPE VARCHAR(50);
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS check_rol_valido;
ALTER TABLE usuarios ADD CONSTRAINT check_rol_valido 
    CHECK (rol IN (
        'usuario_master', 
        'usuario_operador', 
        'usuario_funcionario',
        'admin_sst',              -- NUEVO
        'operador_seguridad'      -- NUEVO
    ));
```

**Riesgo**: ⚠️ **BAJO** 
- Migración simple
- No afecta datos existentes
- Compatible con código actual
- Require downtime mínimo (<1 min)

---

## 3⃣ ANÁLISIS DE VIABILIDAD TÉCNICA

### ✅ Base de Datos

**Diseño de tablas**: ⭐⭐⭐⭐⭐ (Excelente)
- Normalización correcta (3NF)
- Relaciones bien definidas
- Índices en campos clave
- Constraints de integridad
- Campos auditables

**Complejidad estimada**: MEDIA
- 8 tablas nuevas
- 15-20 foreign keys
- 10-15 índices
- 5-8 constraints CHECK
- 2-3 campos calculados GENERATED

**Tiempo estimado DB**: 8-12 días
- Migrations: 3-4 días
- Testing migraciones: 2-3 días
- Seeders (operadores): 1 día
- Verificación integridad: 2-4 días

---

### ✅ Backend (Flask + SQLAlchemy)

**Modelos SQLAlchemy**: ⭐⭐⭐⭐☆ (Muy bueno)
```python
# 8 modelos nuevos a crear:
backend/app/models/
├── empresa_contratista.py      # ~80 líneas
├── empleado_contratista.py     # ~70 líneas
├── operador_aportes.py         # ~40 líneas
├── planilla_ss.py              # ~100 líneas
├── certificado_trabajo.py      # ~60 líneas
├── autorizacion_sst.py         # ~120 líneas (principal)
├── empleado_por_autorizacion.py# ~80 líneas
└── log_ingreso_contratista.py  # ~80 líneas
TOTAL: ~630 líneas
```

**Endpoints API**: ⭐⭐⭐⭐☆ (Muy bueno)
```python
# 1 blueprint nuevo:
backend/app/routes/
└── sst.py   # ~800-1000 líneas
    ├── Empresas: 6 endpoints
    ├── Operadores: 2 endpoints
    ├── Planillas: 4 endpoints
    ├── Certificados: 3 endpoints
    ├── Empleados: 4 endpoints
    ├── Autorizaciones: 8 endpoints
    ├── Ingresos: 5 endpoints
    └── Reportes: 6 endpoints
    TOTAL: ~38 endpoints
```

**Complejidad estimada**: ALTA
- 38 endpoints REST
- Validaciones complejas (vigencias, certificados, planillas)
- Transiciones de estado (BORRADOR → REVISION → APROBADA)
- Cálculos automáticos (vigencia = fecha_pago + 30 días)
- Manejo de archivos (PDF upload)
- Generación de PDF

**Tiempo estimado Backend**: 20-25 días
- Modelos: 4-5 días
- Endpoints básicos (CRUD): 8-10 días
- Lógica de negocio compleja: 5-7 días
- Generación PDF: 3-4 días
- Testing unitario: 3-4 días

---

### ⚠️ Generación de PDF

**Librería propuesta**: WeasyPrint
**Evaluación**: ⭐⭐⭐☆☆ (Aceptable con reservas)

**Ventajas**:
- ✅ Renderiza HTML/CSS a PDF
- ✅ Soporte Unicode (español completo)
- ✅ Relativamente fácil

**Desventajas**:
- ⚠️ Dependencias pesadas (Cairo, Pango, GTK+)
- ⚠️ Instalación compleja en Windows
- ⚠️ Puede fallar en producción sin librerías del sistema

**Alternativa recomendada**: **ReportLab**
- ✅ Librería pura Python
- ✅ Sin dependencias del sistema
- ✅ Más estable en producción
- ❌ Requiere programar layout (no HTML/CSS)

**Decisión**: ⚠️ Usar **xhtml2pdf** (mejor compromiso)
- ✅ HTML/CSS a PDF
- ✅ Sin dependencias pesadas
- ✅ Instalación simple: `pip install xhtml2pdf`
- ❌ Soporte CSS limitado a CSS2

---

### ✅ Frontend (Vanilla JS + Alpine.js)

**Nuevas vistas**: 2 archivos HTML
```
frontend/
├── admin_sst.html            # ~600-800 líneas
└── operador_seguridad.html   # ~400-500 líneas
```

**Componentes reutilizables**:
- ✅ apiClient (ya existe en app.js)
- ✅ SweetAlert2 (ya existe)
- ✅ Estilos Tailwind CSS (ya existe)
- 🆕 Componente de auto-guardado (nuevo, ~50 líneas)
- 🆕 Componente de validación NIT (nuevo, ~30 líneas)
- 🆕 Componente de upload de archivos (nuevo, ~80 líneas)

**Tiempo estimado Frontend**: 12-15 días
- admin_sst.html: 6-8 días
- operador_seguridad.html: 4-5 días
- Componentes nuevos: 2-3 días
- Testing manual: 2-3 días

---

## 4⃣ RIESGOS Y MITIGACIONES

### 🔴 RIESGO ALTO: Complejidad del Flujo de Autorizaciones

**Descripción**: 
El flujo de autorizaciones tiene 6 estados posibles (BORRADOR, REVISION, APROBADA, RECHAZADA, VENCIDA, ANULADA) con transiciones y reglas complejas.

**Probabilidad**: Alta  
**Impacto**: Alto  

**Mitigación**:
1. Crear máquina de estados con validaciones estrictas
2. Tests exhaustivos de transiciones inválidas
3. Documentar casos de uso con ejemplos
4. Implementar logging detallado de cambios de estado

---

### 🟡 RIESGO MEDIO: Generación de PDF puede fallar

**Descripción**: 
Si la plantilla HTML está mal formada, el PDF puede fallar o verse mal.

**Probabilidad**: Media  
**Impacto**: Medio  

**Mitigación**:
1. Validar plantilla HTML con múltiples datos de prueba
2. Implementar try/except con fallback
3. Guardar HTML en archivo de respaldo antes de generar PDF
4. Crear tests automatizados con datos variados

---

### 🟡 RIESGO MEDIO: Validación de Planillas de Seguridad Social

**Descripción**: 
No hay API pública para validar planillas en operadores (Compensar, Nueva EPS, etc). Validación es manual viendo PDF.

**Probabilidad**: Alta (inherente)  
**Impacto**: Medio  

**Mitigación**:
1. Capacitar bien al personal admin_sst
2. Crear checklist de validación de planillas
3. Guardar siempre PDF de la planilla
4. Implementar alertas de vencimiento con 15 días de anticipación

---

### 🟢 RIESGO BAJO: Auto-completado de Datos

**Descripción**: 
Si datos duplicados existen con ligeras diferencias, puede crear inconsistencias.

**Probabilidad**: Baja  
**Impacto**: Bajo  

**Mitigación**:
1. Usar UNIQUE constraints en DB
2. Normalizar datos antes de guardar (mayúsculas, trim)
3. Mostrar mensaje al usuario si encuentra duplicados
4. Permitir seleccionar entre existentes

---

## 5⃣ ESTIMACIÓN DE TIEMPO REALISTA

### Desglose por Fases

| Fase | Tarea | Tiempo Estimado |
|------|-------|-----------------|
| **1** | Análisis y backup completo | 2-3 días |
| **2** | Migración DB (8 tablas) | 8-12 días |
| **3** | Modelos SQLAlchemy (8 modelos) | 4-5 días |
| **4** | Endpoints básicos CRUD | 8-10 días |
| **5** | Lógica de negocio compleja | 5-7 días |
| **6** | Generación de PDF | 3-4 días |
| **7** | Frontend admin_sst.html | 6-8 días |
| **8** | Frontend operador_seguridad.html | 4-5 días |
| **9** | Componentes JavaScript nuevos | 2-3 días |
| **10** | Testing unitario Backend | 5-7 días |
| **11** | Testing integración | 4-5 días |
| **12** | Testing seguridad (OWASP) | 3-4 días |
| **13** | Documentación técnica | 2-3 días |
| **14** | Manuales de usuario | 3-4 días |
| **15** | Capacitación personal | 2-3 días |
| **16** | Despliegue producción | 2-3 días |
| **17** | Ajustes post-despliegue | 5-7 días |
| | **TOTAL** | **68-92 días** |

**Agregando buffer (20%)**: **82-110 días**

**Estimación conservadora final**: **80-120 días hábiles** (16-24 semanas)

---

## 6⃣ RECOMENDACIONES

### ✅ RECOMENDACIONES TÉCNICAS

1. **Implementar por fases iterativas**:
   ```
   Fase 1: DB + Modelos (12-17 días)
   Fase 2: Empresas + Planillas (15-20 días)
   Fase 3: Empleados + Certificados (12-15 días)
   Fase 4: Autorizaciones (18-25 días)
   Fase 5: Ingresos/Salidas (8-12 días)
   Fase 6: Reportes (10-15 días)
   Fase 7: Testing completo (12-16 días)
   ```

2. **Backup OBLIGATORIO antes de iniciar**:
   - ✅ Backup completo de DB
   - ✅ Backup de código fuente
   - ✅ Crear branch separado: `feature/modulo-sst`
   - ✅ No mergear a main hasta testing completo

3. **Testing EXHAUSTIVO**:
   - ✅ Tests unitarios para cada endpoint
   - ✅ Tests de integración para flujos completos
   - ✅ Tests de seguridad (OWASP ZAP)
   - ✅ Tests de carga (registro 100 empleados simultáneos)
   - ✅ Tests de validación de permisos

4. **Validaciones adicionales**:
   ```python
   # Agregar validación de NIT con dígito verificador
   def validar_nit(nit, digito_verificacion):
       """Valida NIT colombiano con algoritmo oficial"""
       # Implementar algoritmo módulo 11
   
   # Validar extensión y mime-type de archivos
   ALLOWED_EXTENSIONS = {'pdf'}
   ALLOWED_MIMETYPES = {'application/pdf'}
   
   def validar_archivo_pdf(file):
       # Validar extensión
       # Validar mime-type real
       # Validar tamaño máximo (5 MB)
   ```

5. **Cambiar librería PDF**:
   ```python
   # En lugar de WeasyPrint, usar xhtml2pdf:
   pip install xhtml2pdf
   
   from xhtml2pdf import pisa
   
   def generar_pdf(html_content, output_path):
       with open(output_path, "wb") as pdf_file:
           pisa.CreatePDF(html_content, dest=pdf_file)
   ```

6. **Agregar índices compuestos**:
   ```sql
   -- Para búsquedas frecuentes:
   CREATE INDEX idx_empleado_empresa_estado 
       ON empleados_contratistas(empresa_id, estado);
   
   CREATE INDEX idx_autorizacion_sede_estado_vigencia 
       ON autorizaciones_sst(sede_id, estado, vigencia_fin);
   ```

---

### ✅ RECOMENDACIONES DE PROCESO

1. **Capacitación PREVIA al despliegue**:
   - Entrenar a admin_sst en validación de planillas
   - Entrenar a operador_seguridad en uso del sistema
   - Hacer simulacros con datos de prueba

2. **Despliegue gradual**:
   - Semana 1: Solo admin_sst usa el sistema (no operadores)
   - Semana 2: Agregar operador_seguridad de 1 sede
   - Semana 3: Expandir a todas las sedes
   - Monitorear logs y errores constantemente

3. **Documentación clara**:
   - ✅ Manual de usuario admin_sst (con screenshots)
   - ✅ Manual de usuario operador_seguridad
   - ✅ FAQ con casos comunes
   - ✅ Videos cortos de capacitación (5-10 min)

4. **Soporte post-despliegue**:
   - Disponibilidad inmediata primeras 2 semanas
   - Canal de Slack/WhatsApp para dudas urgentes
   - Reunión diaria de seguimiento (primeros 5 días)

---

## 7⃣ VEREDICTO FINAL

### ✅ VIABILIDAD: **SÍ, ALTAMENTE VIABLE**

**Calificación general**: ⭐⭐⭐⭐☆ (4/5)

**Fortalezas**:
1. ✅ Arquitectura modular e independiente
2. ✅ Cero impacto en sistema actual
3. ✅ Diseño de DB robusto y normalizado
4. ✅ Cumple con reglas globales de seguridad
5. ✅ Cumple con normativa colombiana (Ley 100)
6. ✅ Documentación extremadamente detallada
7. ✅ Separación clara de responsabilidades

**Debilidades**:
1. ⚠️ Complejidad alta (38 endpoints, 8 tablas)
2. ⚠️ Tiempo de desarrollo subestimado en documento original
3. ⚠️ Validaciones de archivos PDF requiere refuerzo
4. ⚠️ No hay API pública para validar planillas (validación manual)
5. ⚠️ Requiere capacitación extensa del personal

**Riesgos**:
- 🔴 1 alto (complejidad de estados)
- 🟡 2 medios (PDF, validación planillas)
- 🟢 1 bajo (auto-completado)

**Recomendación**: **PROCEDER CON IMPLEMENTACIÓN** bajo las siguientes condiciones:

1. ✅ Backup completo antes de iniciar
2. ✅ Implementar por fases (no todo de una vez)
3. ✅ Testing exhaustivo en cada fase
4. ✅ Cambiar WeasyPrint por xhtml2pdf
5. ✅ Agregar validaciones de archivos
6. ✅ Capacitación previa del personal
7. ✅ Despliegue gradual (1 sede → todas)
8. ✅ Tiempo real: **80-120 días** (no 48-68)

---

## 8⃣ PRÓXIMOS PASOS INMEDIATOS

### Antes de iniciar desarrollo:

1. ✅ **Aprobar este análisis** (stakeholders)
2. ✅ **Crear backup completo** del sistema actual
3. ✅ **Crear branch** `feature/modulo-sst`
4. ✅ **Definir plan de capacitación** para admin_sst y operador_seguridad
5. ✅ **Confirmar tiempos** (80-120 días vs 48-68 original)
6. ✅ **Asignar recursos** (desarrolladores, tiempo, presupuesto)

### Primera fase (si se aprueba):

1. Crear migración para tabla `usuarios` (agregar roles)
2. Crear 8 tablas nuevas con migraciones
3. Crear seeders para operadores (EPS, AFP, ARL)
4. Testing de integridad referencial
5. Verificación en ambiente de desarrollo

**Tiempo fase 1**: 12-17 días

---

## 📎 ANEXOS

### A. Cambios en Sistema Actual

**Archivos a modificar**:
1. `backend/app/models/usuario.py` → Agregar validación de nuevos roles
2. `backend/app/__init__.py` → Registrar blueprint `/api/sst`
3. `frontend/index.html` → Agregar redirección para admin_sst y operador_seguridad

**TOTAL**: 3 archivos (cambios mínimos)

### B. Archivos Nuevos a Crear

**Backend** (10 archivos):
- 8 modelos en `backend/app/models/`
- 1 blueprint en `backend/app/routes/sst.py`
- 1 servicio en `backend/app/services/pdf_service.py`

**Frontend** (2 archivos):
- `frontend/admin_sst.html`
- `frontend/operador_seguridad.html`

**Migraciones** (9 archivos):
- `migrate_add_roles_sst.py`
- `migrate_create_operadores_aportes.py`
- `migrate_create_empresas_contratistas.py`
- `migrate_create_empleados_contratistas.py` 
- `migrate_create_certificados_trabajo.py`
- `migrate_create_planillas_ss.py`
- `migrate_create_autorizaciones_sst.py`
- `migrate_create_empleados_por_autorizacion.py`
- `migrate_create_log_ingresos_contratistas.py`

**Seeders** (1 archivo):
- `backend/init_operadores_ss.py` (EPS, AFP, ARL)

**Tests** (8 archivos):
- `tests/test_empresas_sst.py`
- `tests/test_planillas_sst.py`
- `tests/test_certificados_sst.py`
- `tests/test_empleados_sst.py`
- `tests/test_autorizaciones_sst.py`
- `tests/test_ingresos_sst.py`
- `tests/test_pdf_generacion.py`
- `tests/test_permisos_sst.py`

**TOTAL**: ~30 archivos nuevos

### C. Dependencias Nuevas

```txt
# requirements.txt (agregar):
xhtml2pdf==0.2.13            # Para generación de PDF
Pillow==10.2.0               # Para procesamiento de imágenes en PDF
```

---

**FIN DEL ANÁLISIS**

---

**Elaborado por**: GitHub Copilot  
**Fecha**: 19 de Marzo de 2026  
**Versión**: 1.0  
**Estado**: ✅ Listo para revisión
