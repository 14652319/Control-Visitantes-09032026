# 🎯 PLAN DE ACCIÓN PRAGMÁTICO - Correcciones Control de Visitantes
**Fecha:** 18 de Marzo de 2026  
**Estrategia:** Quick wins primero → Correcciones sin reinicio → Bajo riesgo

> **Filosofía:** Priorizar correcciones rápidas, seguras y sin downtime. Evaluar impacto ANTES de cada cambio.

---

## 📊 METODOLOGÍA DE PRIORIZACIÓN

Cada corrección se evalúa por:

| Criterio | Peso | Escala |
|----------|------|--------|
| **Facilidad** | 30% | 1-5 (5 = muy fácil) |
| **Impacto en sistema** | 25% | 1-5 (5 = sin impacto) |
| **Requiere reinicio** | 20% | Sí (-2 pts) / No (+2 pts) |
| **Riesgo de romper** | 25% | 1-5 (5 = sin riesgo) |

**Score total:** 1-100 (mayor = mejor candidato)

---

## 🟢 GRUPO 1: QUICK WINS (Score 80-100)
### Correcciones seguras, rápidas, sin reinicio

---

### ✅ QW-01: Agregar límite máximo en paginación
**Score:** 95/100  
**Tiempo:** 5 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟢 Muy bajo  
**Severidad original:** 🟠 Alto

#### Análisis de impacto:
- ✅ Cambio en 1 solo archivo
- ✅ No modifica estructura de datos
- ✅ No afecta funcionalidad existente
- ✅ Mejora performance y seguridad
- ✅ Compatible con código actual

#### Archivos a modificar:
- `backend/app/routes/visitantes.py` (línea ~370)

#### Código actual:
```python
por_pagina = request.args.get('por_pagina', 100, type=int)
```

#### Código corregido:
```python
por_pagina = min(request.args.get('por_pagina', 100, type=int), 500)
```

#### Testing inmediato:
```bash
# Sin reiniciar el servidor:
curl "http://localhost:5000/api/visitantes/listar?por_pagina=999999"
# Debe devolver máximo 500 registros
```

#### ✅ APROBADO PARA IMPLEMENTACIÓN INMEDIATA

---

### ✅ QW-02: Reemplazar print() con logging
**Score:** 90/100  
**Tiempo:** 15-20 minutos  
**Requiere reinicio:** ❌ NO (con auto-reload)  
**Riesgo:** 🟢 Muy bajo  
**Severidad original:** 🟠 Alto

#### Análisis de impacto:
- ✅ Cambio cosmético (funcionalidad idéntica)
- ✅ No modifica lógica de negocio
- ✅ Mejora debugging y troubleshooting
- ✅ No afecta usuarios
- ⚠️ Afecta múltiples archivos (pero cambio simple)

#### Archivos a modificar:
1. `backend/app/routes/autorizaciones.py` (7 prints)
2. `backend/app/routes/visitantes.py` (posibles prints)
3. Otros archivos con prints

#### Patrón de reemplazo:
```python
# ❌ Antes:
print(f"🔍 [AUTORIZACIONES] Usuario: {current_user.usuario}")

# ✅ Después:
current_app.logger.info(f"[AUTORIZACIONES] Usuario: {current_user.usuario}")
```

#### Importación necesaria:
```python
from flask import current_app  # Ya importado en la mayoría
```

#### Testing inmediato:
```bash
# Verificar que los logs aparecen en backend/logs/app.log
tail -f backend/logs/app.log
```

#### ✅ APROBADO PARA IMPLEMENTACIÓN INMEDIATA

---

### ✅ QW-03: Corregir typo en frontend
**Score:** 95/100  
**Tiempo:** 2 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟢 Nulo  
**Severidad original:** 🟢 Bajo

#### Análisis de impacto:
- ✅ Solo texto visible
- ✅ No afecta funcionalidad
- ✅ Mejora UX

#### Archivo a modificar:
- `frontend/index.html` (línea 106)

#### Cambio:
```html
<!-- ❌ Antes: -->
<p>¿E res funcionario y no tienes cuenta?</p>

<!-- ✅ Después: -->
<p>¿Eres funcionario y no tienes cuenta?</p>
```

#### ✅ APROBADO PARA IMPLEMENTACIÓN INMEDIATA

---

### ✅ QW-04: Agregar validación de tipo de datos en paginación
**Score:** 88/100  
**Tiempo:** 10 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟢 Muy bajo  
**Severidad original:** 🟡 Medio

#### Análisis de impacto:
- ✅ Mejora robustez sin cambiar funcionalidad
- ✅ Previene errores futuros
- ✅ No modifica comportamiento normal

#### Archivos a modificar:
- `backend/app/routes/visitantes.py` (múltiples endpoints con paginación)

#### Código actual:
```python
pagina = request.args.get('pagina', 1, type=int)
por_pagina = request.args.get('por_pagina', 100, type=int)
```

#### Código mejorado:
```python
try:
    pagina = max(1, int(request.args.get('pagina', 1)))
    por_pagina = min(max(1, int(request.args.get('por_pagina', 100))), 500)
except (ValueError, TypeError):
    pagina = 1
    por_pagina = 100
```

#### ✅ APROBADO PARA IMPLEMENTACIÓN INMEDIATA

---

### ✅ QW-05: Ocultar errores internos al cliente (genérico)
**Score:** 85/100  
**Tiempo:** 30 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟢 Bajo  
**Severidad original:** 🟠 Alto

#### Análisis de impacto:
- ✅ Mejora seguridad sin afectar funcionalidad
- ✅ No cambia lógica de negocio
- ✅ Errores siguen registrándose en logs
- ⚠️ Usuarios ven mensajes genéricos (menos útil para debugging)

#### Patrón de reemplazo:

```python
# ❌ Antes:
except Exception as e:
    return jsonify({
        'success': False,
        'message': f'Error: {str(e)}'  # ← Expone detalles internos
    }), 500

# ✅ Después:
except Exception as e:
    current_app.logger.error(f"Error en [endpoint]: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'message': 'Error interno del servidor. Contáctenos si persiste.'
    }), 500
```

#### Excepciones donde SÍ mostrar detalles:
- Validaciones de negocio (usuario ya existe, etc.)
- Errores esperados (archivo no encontrado, etc.)

#### Testing:
```bash
# Provocar un error intencional y verificar respuesta genérica
curl -X POST http://localhost:5000/api/test-error
```

#### ⚠️ APROBADO CON PRECAUCIÓN
> Implementar gradualmente endpoint por endpoint, probando cada uno.

---

## 🟡 GRUPO 2: CORRECCIONES MEDIAS (Score 60-79)
### Requieren más cuidado pero siguen siendo seguras

---

### ⚠️ M-01: Corregir función rota Dependencias.to_dict()
**Score:** 75/100  
**Tiempo:** 10 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟡 Medio (funcionalidad rota, fix es seguro)  
**Severidad original:** 🔴 CRÍTICO

#### Análisis de impacto:
- ✅ Arregla funcionalidad rota actual
- ✅ No introduce nuevos comportamientos
- ⚠️ Afecta todas las llamadas a Dependencia.to_dict()
- ⚠️ Debe probarse el listado de dependencias

#### Archivo a modificar:
- `backend/app/models/dependencia.py`

#### Código actual (ROTO):
```python
def to_dict(self):
    return {
        'id': self.id,
        'prefijo_dependencia': self.prefijo_dependencia,
        'descripcion_dependencia': self.descripcion_dependencia,
        'estado': self.estado,
        'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
    }
```

#### Código corregido:
```python
def to_dict(self, incluir_sedes=False):
    data = {
        'id': self.id,
        'prefijo_dependencia': self.prefijo_dependencia,
        'descripcion_dependencia': self.descripcion_dependencia,
        'estado': self.estado,
        'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
    }
    
    # Incluir información de sedes si se solicita
    if incluir_sedes and hasattr(self, 'sede_id') and self.sede_id:
        try:
            from app.models.sede import Sede
            sede = Sede.query.get(self.sede_id)
            if sede:
                data['sede'] = {
                    'id': sede.id,
                    'descripcion': sede.descripcion_sede
                }
        except Exception as e:
            current_app.logger.warning(f"Error al incluir sede en to_dict: {e}")
    
    return data
```

#### Testing OBLIGATORIO:
```bash
# 1. Verificar listado de dependencias desde admin
# 2. Verificar creación de nueva dependencia
# 3. Verificar edición de dependencia existente
curl http://localhost:5000/api/dependencias/
```

#### ✅ APROBADO PARA IMPLEMENTACIÓN
> Probar ANTES en ambiente de desarrollo. Verificar visualmente en el panel de admin.

---

### ⚠️ M-02: Normalizar usuario a minúsculas consistentemente
**Score:** 70/100  
**Tiempo:** 15 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟡 Medio (puede afectar usuarios existentes)  
**Severidad original:** 🔴 CRÍTICO

#### Análisis de impacto:
- ⚠️ Afecta creación de nuevos usuarios
- ⚠️ NO afecta usuarios existentes (que ya están en mayúsculas)
- ⚠️ Necesita script de migración para usuarios existentes
- ✅ Login funciona con ambos

#### Decisión:
**POSPONER hasta tener script de migración de datos.**

#### Alternativa segura (solo para usuarios NUEVOS):
```python
# En usuarios.py al crear (línea ~125):
usuario = Usuario(
    usuario=data['usuario'].strip().lower()  # ← Cambio solo para nuevos
)
```

#### ⚠️ REQUIERE ANÁLISIS ADICIONAL
> No implementar sin script de migración para usuarios existentes.

---

### ⚠️ M-03: Agregar rate limiting a endpoints críticos
**Score:** 65/100  
**Tiempo:** 30 minutos  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🟡 Medio (puede bloquear usuarios legítimos)  
**Severidad original:** 🟡 Medio

#### Análisis de impacto:
- ✅ Mejora seguridad significativamente
- ⚠️ Puede bloquear operaciones legítimas si límite es muy bajo
- ⚠️ Necesita configuración conservadora

#### Endpoints a proteger:
```python
# visitantes.py:
@bp.route('/ingreso', methods=['POST'])
@limiter.limit("30 per minute")  # ← Agregar

# autorizaciones.py:
@bp.route('/', methods=['POST'])
@limiter.limit("20 per minute")  # ← Agregar

# auth.py:
@bp.route('/registro-funcionario', methods=['POST'])
@limiter.limit("5 per hour")  # ← Agregar (más restrictivo)
```

#### Testing necesario:
```bash
# Probar que operaciones normales no se bloquean
# Probar que abuso SÍ se bloquea
for i in {1..31}; do
  curl -X POST http://localhost:5000/api/visitantes/ingreso
done
```

#### ✅ APROBADO CON LÍMITES CONSERVADORES
> Empezar con límites altos, reducir gradualmente si es necesario.

---

## 🔴 GRUPO 3: CORRECCIONES COMPLEJAS (Score 40-59)
### Requieren más tiempo, testing y posiblemente reinicio

---

### 🔴 C-01: Eliminar credenciales hardcodeadas
**Score:** 50/100  
**Tiempo:** 30 minutos  
**Requiere reinicio:** ✅ SÍ (cambio en config)  
**Riesgo:** 🔴 Alto (puede romper el sistema)  
**Severidad original:** 🔴 CRÍTICO

#### Análisis de impacto:
- 🔴 Sistema NO arrancará sin .env configurado
- 🔴 Requiere actualización de .env en TODOS los ambientes
- 🔴 Puede dejar sistema inoperante si se hace mal
- ✅ Mejora seguridad crítica

#### Pre-requisitos OBLIGATORIOS:
1. Verificar que existe `.env` con todas las variables
2. Backup de configuración actual
3. Documentar valores actuales
4. Plan de rollback

#### Archivo a modificar:
- `backend/config.py`

#### Pasos seguros:

**Paso 1: Verificar .env actual**
```bash
cd backend
cat .env | grep -E "DATABASE_URL|MAIL_PASSWORD|MAIL_USERNAME"
```

**Paso 2: Documentar valores hardcodeados**
```bash
# Guardar en archivo seguro (NO en git)
echo "DATABASE_URL=postgresql://postgres:G3st0radm$2025.@localhost:5432/control_visitantes" > .env.backup
echo "MAIL_USERNAME=gestordocumentalsc01@gmail.com" >> .env.backup
echo "MAIL_PASSWORD=urjrkjlogcfdtynq" >> .env.backup
```

**Paso 3: Modificar config.py**
```python
# ❌ Antes:
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:G3st0radm$2025.@localhost:5432/control_visitantes'
)

# ✅ Después:
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
if not SQLALCHEMY_DATABASE_URI:
    raise ValueError(
        "❌ DATABASE_URL no configurada.\n"
        "Configure el archivo .env con:\n"
        "DATABASE_URL=postgresql://usuario:password@host:5432/database"
    )
```

**Paso 4: Testing**
```bash
# Probar que arranca con .env
python run.py

# Probar que falla sin .env (renombrar temporalmente)
mv .env .env.bkp
python run.py  # Debe fallar con mensaje claro
mv .env.bkp .env
```

#### ⚠️ REQUIERE COORDINACIÓN CON EQUIPO
> Implementar en horario de bajo tráfico. Tener plan de rollback.

---

### 🔴 C-02: Proteger endpoints de verificación públicos
**Score:** 45/100  
**Tiempo:** 2-4 horas  
**Requiere reinicio:** ❌ NO  
**Riesgo:** 🔴 Alto (puede romper registro de funcionarios)  
**Severidad original:** 🔴 CRÍTICO

#### Análisis de impacto:
- 🔴 Afecta flujo de registro de funcionarios
- 🔴 Requiere cambios en frontend
- 🔴 Necesita implementar sistema de tokens temporal
- ⚠️ Alternativa: agregar CAPTCHA (más simple)

#### Opciones de implementación:

**Opción A: Token temporal (compleja)**
- Generar token al cargar página de registro
- Token válido 15 minutos
- Validar token en cada verificación
- Tiempo: 4 horas

**Opción B: CAPTCHA + Rate limiting (simple)**
- Agregar reCAPTCHA v3 al formulario
- Rate limiting agresivo (3 req/min)
- Honeypot field
- Tiempo: 1 hora

#### ⚠️ POSPONER O USAR OPCIÓN B
> Requiere análisis de UX y testing extensivo.

---

### 🔴 C-03: Implementar protección CSRF
**Score:** 40/100  
**Tiempo:** 8-16 horas  
**Requiere reinicio:** ❌ NO (pero múltiples archivos)  
**Riesgo:** 🔴 Alto (puede romper TODOS los formularios)  
**Severidad original:** 🔴 CRÍTICO

#### Análisis de impacto:
- 🔴 Afecta TODOS los endpoints POST/PUT/DELETE
- 🔴 Requiere cambios en TODOS los formularios frontend
- 🔴 Alto riesgo de romper funcionalidad existente
- ✅ Mejora seguridad crítica

#### ⚠️ POSPONER PARA FASE MAYOR
> Requiere sprint dedicado con testing completo.

---

## 🎯 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### 📅 SESIÓN 1: Quick Wins (1-2 horas)

**Orden de ejecución:**
```
1. QW-03: Corregir typo (2 min)
2. QW-01: Límite paginación (5 min)
3. QW-04: Validación paginación (10 min)
4. QW-02: Reemplazar prints (20 min)
5. M-03: Rate limiting (30 min)
```

**Checklist:**
- [ ] Backup de archivos a modificar
- [ ] Crear branch de git: `git checkout -b fix/quick-wins`
- [ ] Implementar QW-03
- [ ] Probar en navegador
- [ ] Implementar QW-01
- [ ] Probar con curl
- [ ] Implementar QW-04
- [ ] Probar con valores extremos
- [ ] Implementar QW-02
- [ ] Verificar logs
- [ ] Implementar M-03
- [ ] Probar rate limiting
- [ ] Commit: `git commit -m "fix: quick wins - paginación, logging, rate limiting"`
- [ ] Merge a develop

**Downtime requerido:** ❌ CERO

---

### 📅 SESIÓN 2: Función rota + Ocultamiento de errores (2-3 horas)

**Orden de ejecución:**
```
1. M-01: Fix Dependencias.to_dict() (10 min)
2. Testing manual completo (30 min)
3. QW-05: Ocultar errores (30 min por archivo)
```

**Checklist:**
- [ ] Backup completo
- [ ] Crear branch: `git checkout -b fix/dependencias-y-errores`
- [ ] Implementar M-01
- [ ] **TESTING OBLIGATORIO:**
  - [ ] Listar dependencias desde admin
  - [ ] Crear dependencia nueva
  - [ ] Editar dependencia
  - [ ] Obtener detalle de dependencia
- [ ] Implementar QW-05 endpoint por endpoint
- [ ] Testing de cada endpoint modificado
- [ ] Commit y merge

**Downtime requerido:** ❌ CERO (con auto-reload)

---

### 📅 SESIÓN 3: Credenciales hardcodeadas (Coordinada con equipo)

**Pre-requisitos:**
- [ ] Backup de base de datos
- [ ] .env verificado en TODOS los ambientes
- [ ] Plan de rollback documentado
- [ ] Equipo notificado
- [ ] Ventana de mantenimiento (opcional pero recomendado)

**Orden de ejecución:**
```
1. Verificar .env (10 min)
2. Backup de config.py (1 min)
3. Rotar credenciales DB (15 min)
4. Actualizar .env (5 min)
5. Modificar config.py (5 min)
6. Reiniciar servidor (1 min)
7. Verificar que arranca (5 min)
8. Testing funcional completo (30 min)
```

**Downtime requerido:** ✅ 5-10 minutos (reinicio)

---

## 📋 CHECKLIST GENERAL ANTES DE CADA CAMBIO

### Pre-implementación:
- [ ] Leer el código actual completo
- [ ] Identificar todas las dependencias
- [ ] Verificar que no hay otros archivos que usen esa función
- [ ] Hacer backup del archivo
- [ ] Crear branch de git separado
- [ ] Documentar el cambio

### Durante implementación:
- [ ] Seguir el código exacto del plan
- [ ] No agregar "mejoras" adicionales no planificadas
- [ ] Comentar cambios importantes
- [ ] Mantener formato del código existente

### Post-implementación:
- [ ] Verificar que el servidor arranca sin errores
- [ ] Testing manual del feature afectado
- [ ] Verificar logs por errores
- [ ] Probar casos extremos
- [ ] Documentar lo que se cambió
- [ ] Commit con mensaje descriptivo

---

## 🔍 EVALUACIÓN DE IMPACTO - TEMPLATE

Usar ANTES de implementar cada cambio:

```markdown
### Cambio: [Descripción]

#### ¿Qué archivos se modifican?
- 

#### ¿Afecta otros archivos que importen/usen esto?
- 

#### ¿Requiere cambios en la base de datos?
- [ ] Sí / [ ] No

#### ¿Requiere cambios en el frontend?
- [ ] Sí / [ ] No

#### ¿Cambia el comportamiento visible para el usuario?
- [ ] Sí / [ ] No

#### ¿Qué puede salir mal?
1. 
2. 

#### Plan de rollback:
1. 
2. 

#### Testing mínimo requerido:
- [ ] 
- [ ] 

#### ¿Aprobado para implementar?
- [ ] Sí / [ ] No / [ ] Requiere más análisis
```

---

## 🚫 PROBLEMAS QUE NO TOCAR (Por Ahora)

| ID | Problema | Razón |
|----|----------|-------|
| C-03 | CSRF | Requiere sprint completo |
| C-05 | Timezone | Requiere migración de datos |
| M-02 | Normalización usuario | Necesita script de migración |
| C-02 | Endpoints públicos | Afecta flujo crítico |
| A-06 | Soft Delete | Cambio arquitectónico mayor |

Estos requieren planning, testing extensivo y coordinación.

---

## 📊 MÉTRICAS DE ÉXITO

Después de cada sesión, verificar:

- [ ] ✅ Sistema funciona igual o mejor que antes
- [ ] ✅ Sin errores nuevos en logs
- [ ] ✅ Tests manuales pasaron
- [ ] ✅ Performance no empeoró
- [ ] ✅ Usuarios no reportan problemas
- [ ] ✅ Código commiteado y mergeado

---

## 🎓 LECCIONES APRENDIDAS

Documentar después de cada implementación:

```markdown
**Fecha:** 
**Cambio:** 
**Tiempo real:** 
**Complicaciones:** 
**Lecciones:** 
**Para próxima vez:** 
```

---

## 📞 CONTACTO EN CASO DE EMERGENCIA

Si algo sale mal:

1. **NO PÁNICO**
2. Verificar logs: `tail -f backend/logs/app.log`
3. Rollback: `git checkout [archivo]`
4. Reiniciar servidor si es necesario
5. Documentar qué pasó
6. Analizar por qué falló
7. Ajustar plan para próxima vez

---

## ✅ RESUMEN EJECUTIVO

| Grupo | Cambios | Tiempo | Downtime | Prioridad |
|-------|---------|--------|----------|-----------|
| Quick Wins | 5 | 1-2h | ❌ NO | 🟢 ALTA |
| Medios | 3 | 2-3h | ❌ NO | 🟡 MEDIA |
| Complejos | 3 | 8-24h | ✅ SÍ | 🔴 COORDINAR |

**Recomendación:** Empezar con Grupo 1 (Quick Wins) en sesión de 2 horas. Evaluar resultados antes de continuar.

---

*Plan generado el 18 de Marzo de 2026 - Actualizar después de cada implementación*
