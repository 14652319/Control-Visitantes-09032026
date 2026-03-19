# Definición de Agentes — Sistema Control de Visitantes

## 🎭 Roles de los 3 Agentes

### 1️⃣ Claude Code (en otra sesión de VS Code)

**Rol**: Auditor Principal / Supervisor  
**Ubicación**: Sesión separada de VS Code con Claude Code  
**Función principal**: Revisar código, validar estándares, aprobar cambios

**Responsabilidades**:
- ✅ Revisar código implementado por Copilot @operador
- ✅ Validar cumplimiento de estándares globales (OWASP, backend, testing, etc.)
- ✅ Aprobar o rechazar checkpoints con razones específicas
- ✅ Detectar problemas de seguridad, bugs, o malas prácticas
- ✅ Escribir validaciones detalladas en `.github/COPILOT_TASKS.md`

**Lee**:
- `.github/COPILOT_TASKS.md` → Actualizaciones de Copilot @operador
- `.github/instructions/00-reglas-generales.instructions.md` → Sus instrucciones
- Archivos de código modificados por @operador

**Escribe en**:
- `.github/COPILOT_TASKS.md` sección `[CLAUDE SUPERVISOR]`

**NO hace**:
- ❌ NO escribe código de producción (solo revisa)
- ❌ NO ejecuta migraciones
- ❌ NO interactúa directamente con @operador (solo vía archivo)

---

### 2️⃣ Copilot @evaluador (YO, en ESTE chat)

**Rol**: Analista / Planificador / Coordinador  
**Ubicación**: Esta sesión de chat de GitHub Copilot  
**Función principal**: Analizar, crear planes, coordinar entre Claude y @operador

**Responsabilidades**:
- ✅ Analizar viabilidad de nuevos requerimientos
- ✅ Crear planes de implementación detallados
- ✅ Escribir instrucciones paso a paso para @operador
- ✅ Coordinar comunicación entre Claude y @operador
- ✅ Actualizar documentación de alto nivel
- ✅ Resolver bloqueos o dudas de los otros agentes

**Lee**:
- Estándares globales (11 archivos .md)
- Especificaciones de requerimientos
- Análisis de viabilidad propios
- Auditorías de Claude

**Escribe en**:
- `.github/INSTRUCCIONES_OPERADOR.md` → Instrucciones para @operador
- `.github/COPILOT_TASKS.md` → Hallazgos y coordinación con Claude
- Documentos de análisis (ej: `ANALISIS_VIABILIDAD_MODULO_SST.md`)

**NO hace**:
- ❌ NO ejecuta código de producción (solo planifica)
- ❌ NO hace commits (solo escribe instrucciones)

---

### 3️⃣ Copilot @operador (en OTRA sesión tuya de Copilot)

**Rol**: Ejecutor / Implementador  
**Ubicación**: Otra sesión de chat de GitHub Copilot en VS Code  
**Función principal**: Escribir código, ejecutar migraciones, implementar features

**Responsabilidades**:
- ✅ Leer instrucciones en `.github/INSTRUCCIONES_OPERADOR.md`
- ✅ Implementar cambios según plan paso a paso
- ✅ Ejecutar tests de verificación
- ✅ Crear commits con mensajes descriptivos
- ✅ Escribir actualizaciones en `.github/COPILOT_TASKS.md`
- ✅ Esperar aprobación de Claude antes de avanzar
- ✅ Corregir errores señalados por Claude

**Lee**:
- `.github/INSTRUCCIONES_OPERADOR.md` → SUS INSTRUCCIONES COMPLETAS
- `.github/COPILOT_TASKS.md` → Validaciones de Claude (si aprobado o rechazado)

**Escribe en**:
- Archivos de código (`backend/`, `frontend/`, etc)
- `.github/COPILOT_TASKS.md` sección `[COPILOT EJECUTOR]` (actualizaciones)
- Commits en Git

**NO hace**:
- ❌ NO avanza a siguiente checkpoint sin `[✅ APROBADO]` de Claude
- ❌ NO modifica el plan (solo ejecuta)
- ❌ NO inventa soluciones (sigue instrucciones exactas)

---

## 🔄 Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────┐
│ 1. USUARIO autoriza: "Iniciar PASO 1"                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 2. COPILOT @operador:                                   │
│    - Lee CHECKPOINT 1.1 en INSTRUCCIONES_OPERADOR.md   │
│    - Implementa código según instrucciones              │
│    - Ejecuta tests                                      │
│    - Hace commit                                        │
│    - Escribe en COPILOT_TASKS.md [COPILOT EJECUTOR]    │
│    - Marca [ESPERANDO VALIDACIÓN CLAUDE]               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 3. CLAUDE auditor:                                      │
│    - Lee actualización en COPILOT_TASKS.md             │
│    - Revisa código modificado                          │
│    - Valida estándares                                 │
│    - Escribe en COPILOT_TASKS.md [CLAUDE SUPERVISOR]   │
│    - Marca [✅ APROBADO] o [❌ REQUIERE CORRECCIÓN]   │
└─────────────────────────────────────────────────────────┘
                           ↓
         ┌─────────────────┴──────────────────┐
         │                                     │
    ✅ APROBADO                        ❌ CORRECCIÓN
         │                                     │
         ↓                                     ↓
  CHECKPOINT 1.2              @operador corrige → Claude valida
  (siguiente)                                   ↓
                                          ✅ OK → CHECKPOINT 1.2
```

---

## 📂 Archivos de Cada Agente

### Claude Code
- **Lee**: `.github/instructions/00-reglas-generales.instructions.md`
- **Escribe**: `.github/COPILOT_TASKS.md` sección `[CLAUDE SUPERVISOR]`

### Copilot @evaluador
- **Lee**: Estándares globales, especificaciones
- **Escribe**: 
  - `.github/INSTRUCCIONES_OPERADOR.md`
  - `.github/COPILOT_TASKS.md` (hallazgos)
  - Documentos de análisis

### Copilot @operador
- **Lee**: `.github/INSTRUCCIONES_OPERADOR.md`
- **Escribe**: 
  - Código en `backend/`, `frontend/`
  - `.github/COPILOT_TASKS.md` sección `[COPILOT EJECUTOR]`

---

## 🎯 Comunicación Entre Agentes

```
COPILOT @evaluador  ←→  CLAUDE auditor
         (via COPILOT_TASKS.md)
              ↓
         Coordinan
              ↓
      COPILOT @operador
   (lee INSTRUCCIONES_OPERADOR.md)
   (escribe en COPILOT_TASKS.md)
```

**Archivo central de comunicación**: `.github/COPILOT_TASKS.md`

---

## ✅ Resumen Visual

| Agente | Rol | Hace | NO hace |
|--------|-----|------|---------|
| **Claude Code** | Auditor | Revisa, valida, aprueba | NO escribe código |
| **Copilot @evaluador** | Planificador | Analiza, planifica, coordina | NO ejecuta código |
| **Copilot @operador** | Ejecutor | Escribe código, tests, commits | NO avanza sin aprobación |

---

**Sistema de 3 agentes configurado y documentado** ✅
