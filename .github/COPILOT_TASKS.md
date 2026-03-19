# COPILOT_TASKS — Canal de Comunicación Claude ↔ Copilot @evaluador
# Sistema: Control de Visitantes — Supertiendas Cañaveral SAS

> **ESTE ARCHIVO ES SOLO PARA COMUNICACIÓN**
> 
> **Copilot @operador**: TUS instrucciones están en `.github/INSTRUCCIONES_OPERADOR.md`  
> **Claude auditor**: TUS instrucciones están en `.github/instructions/00-reglas-generales.instructions.md`

---

## 📊 Roles de los Agentes

### 1️⃣ Claude Code (en otra sesión de VS Code)
- **Rol**: Auditor principal / Supervisor
- **Función**: Revisa código, valida estándares, aprueba cambios
- **Lee**: Este archivo para ver actualizaciones de Copilot @operador
- **Escribe**: Sección `[CLAUDE SUPERVISOR]` con validaciones

### 2️⃣ Copilot @evaluador (YO, el que hizo análisis de viabilidad)
- **Rol**: Analista / Planificador / Coordinador
- **Función**: Analizo, creo planes, coordino entre Claude y el ejecutor
- **Lee**: Estándares globales, especificaciones, análisis de viabilidad
- **Comunica con Claude**: A través de este archivo
- **Comunica con @operador**: A través de `INSTRUCCIONES_OPERADOR.md`

### 3️⃣ Copilot @operador (en OTRA sesión tuya de Copilot)
- **Rol**: Ejecutor / Implementador
- **Función**: Escribe código, ejecuta migraciones, implementa features
- **Lee**: `.github/INSTRUCCIONES_OPERADOR.md` (TUS INSTRUCCIONES COMPLETAS)
- **Escribe**: Sección `[COPILOT EJECUTOR]` de este archivo con actualizaciones

---

## 📋 Estado del Proyecto

- **Rama activa**: `master`
- **Último commit**: `ec1f883` (commit 12 03 2026)
- **FASE activa**: ⏸️ **ESPERANDO AUTORIZACIÓN USUARIO**
- **Próxima acción**: Iniciar **PASO 1: FASE 1** (5-8 horas)

### 🎯 Plan Aprobado

```
┌─────────────────────────────────────────────────────────┐
│ ✅ APROBADO: Implementar Módulo SST                    │
│ ⚠️  CONDICIÓN: Después de completar FASE 1             │
│ ⏱️  Tiempo total: 5-8h (FASE 1) + 80-120 días (SST)    │
└─────────────────────────────────────────────────────────┘

PASO 1: FASE 1 - Correcciones críticas (5-8 horas)
PASO 2: Preparación Módulo SST (2-3 días)
PASO 3: Módulo SST - 7 Fases (80-120 días)
```

**📖 Instrucciones detalladas**: Ver `.github/INSTRUCCIONES_OPERADOR.md`

**📊 Análisis completo**: Ver `ANALISIS_VIABILIDAD_MODULO_SST.md` (30 páginas)

---

## 📝 Hallazgos y Análisis (Copilot @evaluador)

### ✅ Análisis de Viabilidad Módulo SST — COMPLETADO

**Fecha**: 2026-03-19  
**Analista**: Copilot @evaluador  
**Documento**: `ANALISIS_VIABILIDAD_MODULO_SST.md` (30 páginas)

**Veredicto**: ✅ **VIABLE** (4/5 estrellas)

**Resumen ejecutivo**:
- Arquitectura modular 100% independiente ✅
- Cero impacto en sistema actual ✅
- Cumple OWASP + Ley 100 + Resolución 4272 ✅
- 8 tablas nuevas + 38 endpoints + 2 roles ✅
- Tiempo realista: 80-120 días (no 48-68 como documento) ⚠️
- Riesgos: 1 alto, 2 medios, 1 bajo ⚠️

**Recomendaciones clave**:
1. Usar xhtml2pdf (no WeasyPrint)
2. Implementar validación NIT automática
3. Validar archivos PDF con seguridad
4. Implementar por 7 fases iterativas
5. Backup obligatorio antes de iniciar

**Estado**: ✅ Análisis aprobado por ambos agentes (Copilot + Claude)

---

## 📝 SECCIONES DE COMUNICACIÓN

### [COPILOT EJECUTOR] — @operador escribe aquí después de cada checkpoint

**Copilot @operador**: Después de completar cada checkpoint en `INSTRUCCIONES_OPERADOR.md`, copiá y pegá esto aquí:

```markdown
---
CHECKPOINT X.Y.Z - [Título del checkpoint]
Fecha: 2026-03-19 HH:MM
Commit: <hash del commit>

QUÉ HICE:
- [Acción 1 completada]
- [Acción 2 completada]
- [Archivo creado/modificado]

ARCHIVOS MODIFICADOS/CREADOS:
- backend/archivo1.py (creado/modificado)
- backend/archivo2.py (creado/modificado)

TESTS EJECUTADOS:
```powershell
# Comando ejecutado
pytest backend/tests/ -v
```
Resultado: ✅ PASS / ❌ FAIL

COMMIT REALIZADO:
```bash
git add .
git commit -m "feat: descripción del cambio (CHECKPOINT X.Y.Z)"
git push origin [rama]
```

ESTADO: [ESPERANDO VALIDACIÓN CLAUDE]
---
```

**Instrucciones completas**: `.github/INSTRUCCIONES_OPERADOR.md`

---

### [CLAUDE SUPERVISOR] — Claude escribe aquí después de revisar

**Claude**: Después de que Copilot @operador marque `[ESPERANDO VALIDACIÓN]`, revisá y escribí:

```markdown
---
CHECKPOINT X.Y.Z - REVISIÓN CLAUDE

FECHA REVISIÓN: 2026-03-19 HH:MM

VALIDACIONES REALIZADAS:
- [ ] Código cumple estándares globales: ✅ OK / ❌ FALLA
- [ ] Tests pasan 100%: ✅ OK / ❌ FALLA
- [ ] Seguridad OWASP: ✅ OK / ❌ FALLA
- [ ] Commits descriptivos: ✅ OK / ❌ FALLA
- [ ] Sin regresiones: ✅ OK / ❌ FALLA

ARCHIVOS REVISADOS:
- backend/archivo1.py: [Observaciones específicas]
- backend/archivo2.py: [Observaciones específicas]

CUMPLIMIENTO ESTÁNDARES:
- 03-seguridad.md: ✅ OK / ❌ FALLA (razón)
- 04-backend.md: ✅ OK / ❌ FALLA (razón)
- 07-testing.md: ✅ OK / ❌ FALLA (razón)

DECISIÓN FINAL:
[✅ APROBADO - Copilot @operador puede avanzar a siguiente checkpoint]

O

[❌ REQUIERE CORRECCIÓN:
- Corrección 1: [Detalle específico]
- Corrección 2: [Detalle específico]
Copilot @operador: Corregí estos puntos y volvé a marcar [ESPERANDO VALIDACIÓN]]

Firma: Claude Code (Auditor)
---
```

**Tus instrucciones completas**: `.github/instructions/00-reglas-generales.instructions.md`

---

## 🚦 Estado Actual del Trabajo

### ⏸️ ESPERANDO AUTORIZACIÓN USUARIO PARA INICIAR

**Próximo paso**: Usuario debe decir **"Iniciar PASO 1"** o **"Comenzar FASE 1"**

Una vez autorizado:
1. **Copilot @operador** lee CHECKPOINT 1.1 en `INSTRUCCIONES_OPERADOR.md`
2. **Copilot @operador** implementa cambios
3. **Copilot @operador** escribe actualización en sección `[COPILOT EJECUTOR]` de este archivo
4. **Claude** lee actualización y escribe validación en `[CLAUDE SUPERVISOR]`
5. Si ✅ aprobado → siguiente checkpoint
6. Si ❌ corrección → @operador corrige y vuelve a paso 3

---

## 📚 Documentos de Referencia

| Documento | Contiene | Para quién |
|-----------|----------|------------|
| `.github/INSTRUCCIONES_OPERADOR.md` | Instrucciones paso a paso para implementar | Copilot @operador |
| `.github/COPILOT_TASKS.md` | Este archivo (comunicación) | Claude + @evaluador |
| `.github/instructions/00-reglas-generales.instructions.md` | Reglas y estándares del proyecto | Claude auditor |
| `ANALISIS_VIABILIDAD_MODULO_SST.md` | Análisis técnico completo (30 páginas) | Todos (referencia) |
| `PLAN_ACCION_CORRECCIONES.md` | Plan FASE 1 (Quick Wins) | Referencia |
| `Levantamiento de requerimientos control visitantes.txt` | Especificación completa (líneas 3090-5782 = SST) | Referencia |

---

## 🆘 Si Necesitás Ayuda

**Copilot @operador**: Si encontrás un error o tenés dudas:
1. Escribí en sección `[COPILOT EJECUTOR]` el problema exacto
2. Marcá `[❓ PREGUNTA]` o `[❌ ERROR]`
3. Claude o @evaluador te ayudarán

**Claude**: Si detectás algo incorrecto en el plan:
1. Escribí en sección `[CLAUDE SUPERVISOR]`
2. Mencioná a @evaluador para ajustar `INSTRUCCIONES_OPERADOR.md`

---

**✅ Sistema de coordinación configurado y listo**

**Esperando señal del usuario para iniciar PASO 1** 🚀
