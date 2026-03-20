# 🚀 PLAN COMPLETO FULLSTACK - Control de Visitantes
**Fecha:** 18 de Marzo de 2026  
**Objetivo:** Completar TODO el sistema fullstack con todas las funcionalidades

---

## 📊 VISIÓN GENERAL

Este documento complementa [PLAN_ACCION_CORRECCIONES.md](PLAN_ACCION_CORRECCIONES.md) agregando la **FASE 2: Completar Funcionalidades Faltantes**

### Estado Actual vs Objetivo:

| Aspecto | Actual | Después FASE 1 | Después FASE 2 |
|---------|--------|----------------|----------------|
| **Bugs críticos** | 🔴 4 activos | 🟢 0 | 🟢 0 |
| **Seguridad** | 🔴 Vulnerable | 🟡 Mejorada | 🟢 Completa |
| **Backend** | 🟢 Completo | 🟢 Completo | 🟢 Completo |
| **Frontend** | 🟡 80% | 🟡 80% | 🟢 100% |
| **Features completos** | 🟡 85% | 🟡 85% | 🟢 100% |

---

## 🎯 ROADMAP COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: CORRECCIONES (5-8 horas)                            │
│ ✅ Corregir bugs                                             │
│ ✅ Mejorar seguridad básica                                  │
│ ✅ Optimizar código                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ FASE 2: COMPLETAR FULLSTACK (80-120 horas)                  │
│ 🔨 UI de Configuración del Sistema                          │
│ 🔨 Visor de Logs de Auditoría                               │
│ 🔨 Validación contraseña en tiempo real                     │
│ 🔨 Protección CSRF                                          │
│ 🔨 Corregir Timezone                                        │
│ 🔨 Documentación API                                        │
│ 🔨 Soft Delete                                              │
│ 🔨 Testing completo                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ RESULTADO: SISTEMA FULLSTACK 100% COMPLETO                  │
│ ✅ Listo para producción                                     │
│ ✅ Todas las funcionalidades implementadas                   │
│ ✅ Seguridad profesional                                     │
│ ✅ Testing completo                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 FASE 2: FEATURES FALTANTES (80-120 horas)

---

### 🎨 F2-01: UI de Configuración del Sistema
**Tiempo estimado:** 24 horas  
**Prioridad:** 🔴 CRÍTICA  
**Backend:** ✅ Ya existe ([backend/app/routes/configuracion.py](backend/app/routes/configuracion.py))  
**Frontend:** ❌ Falta implementar

#### Análisis actual:

```javascript
// En admin.html - Sidebar tiene el link:
<button @click="seccionActiva = 'configuracion'">
    <i class="fas fa-cog"></i> Configuración
</button>

// Pero la sección está vacía o incompleta:
<div x-show="seccionActiva === 'configuracion'">
    <!-- ❌ NO IMPLEMENTADO -->
</div>
```

#### Funcionalidades a implementar:

1. **Tabla de configuraciones** (6h)
   - Listar todas las configuraciones del sistema
   - Mostrar: clave, valor, descripción, tipo
   - Diseño responsive con Tailwind CSS

2. **Formulario de edición inline** (8h)
   ```html
   <tr>
       <td>dias_vigencia_autorizacion</td>
       <td>
           <input type="number" x-model="config.valor" 
                  @change="guardarConfiguracion('dias_vigencia_autorizacion')">
       </td>
       <td>Días de vigencia para autorizaciones de ingreso</td>
   </tr>
   ```

3. **Validaciones específicas** (4h)
   - `dias_vigencia_autorizacion`: 1-365
   - `max_intentos_login`: 3-20
   - `requiere_foto_visitante`: boolean
   - `requiere_numero_carnet`: boolean

4. **Confirmación de cambios** (2h)
   - SweetAlert2 al guardar
   - Loading state durante actualización
   - Feedback visual de éxito/error

5. **Historial de cambios** (4h)
   - Mostrar quién modificó qué y cuándo
   - Integrar con LogEvento

#### Endpoints API a usar:
```javascript
// Ya existen en backend:
GET  /api/configuracion/              // Listar todas
GET  /api/configuracion/<clave>       // Obtener una
PUT  /api/configuracion/<clave>       // Actualizar
PUT  /api/configuracion/batch         // Actualizar múltiples
```

#### Diseño UI sugerido:

```
┌─────────────────────────────────────────────────────────────┐
│ CONFIGURACIÓN DEL SISTEMA                           [Guardar]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Parámetro                │ Valor │ Descripción          │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ Días vigencia autoriza   │ [1] ▼ │ Días válida la auto  │ │
│ │ Máx intentos login       │ [10]▼ │ Antes de bloquear    │ │
│ │ Requiere foto visitante  │ [✓]   │ Foto obligatoria     │ │
│ │ Requiere número carnet   │ [ ]   │ Carnet obligatorio   │ │
│ │ Nombre del sistema       │ [...] │ Nombre mostrado      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ Última modificación: Usuario Master - 18/03/2026 14:30       │
└─────────────────────────────────────────────────────────────┘
```

#### Testing requerido:
- [ ] Listar configuraciones
- [ ] Editar cada parámetro
- [ ] Validar límites (no aceptar valores inválidos)
- [ ] Verificar que cambios se persisten
- [ ] Verificar que cambios afectan el sistema

---

### 📊 F2-02: Visor de Logs de Auditoría
**Tiempo estimado:** 24 horas  
**Prioridad:** 🔴 CRÍTICA  
**Backend:** ✅ Ya existe (modelo LogEvento)  
**Frontend:** ❌ Falta implementar

#### Estado actual:

```python
# Backend registra TODO:
LogEvento.registrar_evento(
    tipo_evento='LOGIN_EXITOSO',
    descripcion=f'Usuario {usuario.usuario} inició sesión',
    usuario=usuario,
    ip_address=request.remote_addr,
    nivel='INFO'
)

# Pero NO hay UI para consultarlo
```

#### Funcionalidades a implementar:

1. **Tabla de eventos** (8h)
   - Columnas: Fecha/Hora, Usuario, Tipo, Descripción, IP, Nivel
   - Paginación (100 eventos por página)
   - Orden descendente por fecha

2. **Filtros avanzados** (8h)
   ```javascript
   - Rango de fechas (desde/hasta)
   - Usuario específico
   - Tipo de evento (LOGIN, CREAR_USUARIO, etc.)
   - Nivel (INFO, WARNING, ERROR)
   - Búsqueda de texto libre en descripción
   ```

3. **Exportar a Excel** (4h)
   - Botón "Exportar resultados"
   - Usar endpoint existente de reportes
   - Incluir filtros aplicados

4. **Vista detallada** (4h)
   - Modal con información completa del evento
   - Incluir: User-Agent, detalles adicionales, stack trace si es error

#### Endpoint API a crear:

```python
# backend/app/routes/log_eventos.py (NUEVO ARCHIVO)

@bp.route('/logs', methods=['GET'])
@login_required
@role_required('usuario_master')
def listar_logs():
    """Listar logs con filtros avanzados"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    usuario_id = request.args.get('usuario_id')
    tipo_evento = request.args.get('tipo_evento')
    nivel = request.args.get('nivel')
    busqueda = request.args.get('busqueda')
    
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = min(request.args.get('por_pagina', 100, type=int), 500)
    
    query = LogEvento.query
    
    # Aplicar filtros...
    
    logs = query.order_by(LogEvento.timestamp.desc()).paginate(
        page=pagina, per_page=por_pagina
    )
    
    return jsonify({
        'success': True,
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'paginas': logs.pages
    })
```

#### Diseño UI sugerido:

```
┌─────────────────────────────────────────────────────────────┐
│ LOGS DE AUDITORÍA                            [Exportar Excel]│
├─────────────────────────────────────────────────────────────┤
│ Filtros:                                                      │
│ [Desde: __/__/____] [Hasta: __/__/____] [Usuario: Todos ▼]  │
│ [Tipo: Todos ▼] [Nivel: Todos ▼] [Buscar: _____________] 🔍  │
├─────────────────────────────────────────────────────────────┤
│ Fecha/Hora        │Usuario    │Tipo           │Nivel│IP     │
├─────────────────────────────────────────────────────────────┤
│ 18/03 14:30:25   │admin      │LOGIN_EXITOSO  │INFO │192... │
│ 18/03 14:25:10   │operador1  │CREAR_VISITA   │INFO │192... │
│ 18/03 14:20:05   │admin      │CAMBIO_CONFIG  │WARN │192... │
│ ...                                                           │
├─────────────────────────────────────────────────────────────┤
│ Mostrando 1-100 de 1,523 eventos      [< 1 2 3 ... 16 >]    │
└─────────────────────────────────────────────────────────────┘
```

#### Testing requerido:
- [ ] Listar todos los logs
- [ ] Filtrar por fecha
- [ ] Filtrar por usuario
- [ ] Filtrar por tipo de evento
- [ ] Búsqueda de texto
- [ ] Paginación funciona
- [ ] Exportar a Excel

---

### 🔐 F2-03: Validación de Contraseña en Tiempo Real
**Tiempo estimado:** 8 horas  
**Prioridad:** 🟡 MEDIA  
**Backend:** ✅ Ya valida  
**Frontend:** ❌ Sin feedback visual

#### Estado actual:

```html
<!-- registro-funcionario.html -->
<input type="password" id="password" minlength="8" required>
<!-- El usuario NO sabe los requisitos hasta que falla -->
```

Backend valida:
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 minúscula
- Al menos 1 número
- Al menos 1 carácter especial

#### Funcionalidades a implementar:

1. **Indicador de requisitos** (4h)
   ```html
   <div class="password-requirements">
       <p>La contraseña debe contener:</p>
       <ul>
           <li :class="{'text-green-500': requisitos.longitud, 'text-gray-400': !requisitos.longitud}">
               <i :class="requisitos.longitud ? 'fas fa-check' : 'fas fa-times'"></i>
               Mínimo 8 caracteres
           </li>
           <li :class="{'text-green-500': requisitos.mayuscula, 'text-gray-400': !requisitos.mayuscula}">
               <i :class="requisitos.mayuscula ? 'fas fa-check' : 'fas fa-times'"></i>
               Al menos una mayúscula
           </li>
           <!-- ... más requisitos ... -->
       </ul>
   </div>
   ```

2. **Validación en tiempo real** (2h)
   ```javascript
   function validarPassword(password) {
       return {
           longitud: password.length >= 8,
           mayuscula: /[A-Z]/.test(password),
           minuscula: /[a-z]/.test(password),
           numero: /[0-9]/.test(password),
           especial: /[!@#$%^&*(),.?":{}|<>]/.test(password)
       };
   }
   ```

3. **Barra de fuerza** (2h)
   ```html
   <div class="password-strength">
       <div class="strength-bar" :class="fuerzaColor">
           <div class="strength-fill" :style="{width: fuerzaPorcentaje + '%'}"></div>
       </div>
       <span class="strength-text">{{ fuerzaTexto }}</span>
   </div>
   ```

#### Testing requerido:
- [ ] Escribir password débil → mostrar requisitos faltantes
- [ ] Cumplir cada requisito → check verde
- [ ] Barra de fuerza actualiza
- [ ] No permite submit si no cumple requisitos

---

### 🛡️ F2-04: Protección CSRF Completa
**Tiempo estimado:** 16 horas  
**Prioridad:** 🔴 CRÍTICA  
**Riesgo:** Alto (afecta todos los formularios)

#### Implementación:

1. **Backend - Flask-WTF** (8h)
   ```python
   # Instalar: pip install Flask-WTF
   
   from flask_wtf.csrf import CSRFProtect
   
   csrf = CSRFProtect()
   csrf.init_app(app)
   
   # Excluir endpoints públicos:
   @bp.route('/login', methods=['POST'])
   @csrf.exempt
   def login():
       pass
   ```

2. **Frontend - Agregar tokens** (6h)
   ```javascript
   // Obtener token CSRF al cargar página
   const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
   
   // Agregar a todas las peticiones:
   fetch('/api/usuarios', {
       method: 'POST',
       headers: {
           'X-CSRFToken': csrfToken
       },
       body: JSON.stringify(data)
   });
   ```

3. **Testing exhaustivo** (2h)
   - Probar TODOS los formularios
   - Verificar que sin token falla
   - Verificar que con token funciona

#### ⚠️ ALTO RIESGO
> Puede romper TODA la funcionalidad. Requiere testing completo.

---

### 🕒 F2-05: Corregir Timezone (UTC → America/Bogota)
**Tiempo estimado:** 8 horas  
**Prioridad:** 🔴 CRÍTICA  
**Riesgo:** Medio (requiere migración de datos)

#### Problema actual:

```python
# Todos los modelos:
fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # UTC

# Pero config dice:
TIMEZONE = 'America/Bogota'  # No se usa
```

#### Solución:

1. **Crear función centralizada** (2h)
   ```python
   # backend/app/utils/timezone.py
   import pytz
   from datetime import datetime
   
   COL_TZ = pytz.timezone('America/Bogota')
   
   def get_colombia_time():
       """Obtiene la hora actual de Colombia"""
       return datetime.now(COL_TZ)
   
   def utc_to_colombia(utc_dt):
       """Convierte UTC a hora de Colombia"""
       if utc_dt.tzinfo is None:
           utc_dt = pytz.utc.localize(utc_dt)
       return utc_dt.astimezone(COL_TZ)
   ```

2. **Actualizar todos los modelos** (2h)
   ```python
   from app.utils.timezone import get_colombia_time
   
   fecha_creacion = db.Column(db.DateTime, default=get_colombia_time)
   ```

3. **Script de migración** (3h)
   ```python
   # migrate_timezone_fix.py
   # Convertir TODOS los timestamps existentes de UTC a COT
   ```

4. **Testing** (1h)
   - Crear nuevo registro → verificar hora correcta
   - Ver registros viejos → verificar hora correcta
   - Reportes → verificar horas correctas

---

### 📚 F2-06: Documentación API (Swagger)
**Tiempo estimado:** 8 horas  
**Prioridad:** 🟡 MEDIA

#### Implementación:

1. **Instalar flasgger** (1h)
   ```bash
   pip install flasgger
   ```

2. **Configurar Swagger** (2h)
   ```python
   from flasgger import Swagger
   
   swagger = Swagger(app)
   ```

3. **Documentar endpoints** (4h)
   ```python
   @bp.route('/login', methods=['POST'])
   def login():
       """
       Endpoint de autenticación
       ---
       tags:
         - Autenticación
       parameters:
         - name: body
           in: body
           required: true
           schema:
             properties:
               usuario:
                 type: string
               password:
                 type: string
       responses:
         200:
           description: Login exitoso
         401:
           description: Credenciales inválidas
       """
       pass
   ```

4. **Testing y refinamiento** (1h)
   - Verificar que /api/docs funciona
   - Probar endpoints desde Swagger UI

---

### 🗑️ F2-07: Implementar Soft Delete
**Tiempo estimado:** 16 horas  
**Prioridad:** 🟡 MEDIA  
**Riesgo:** Medio (cambio arquitectónico)

#### Implementación:

1. **Agregar campo a modelos** (4h)
   ```python
   # En Sede, Dependencia, Usuario:
   fecha_eliminacion = db.Column(db.DateTime, nullable=True)
   eliminado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
   
   @property
   def activo(self):
       return self.fecha_eliminacion is None
   ```

2. **Crear mixin reutilizable** (2h)
   ```python
   class SoftDeleteMixin:
       fecha_eliminacion = db.Column(db.DateTime)
       eliminado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
       
       def soft_delete(self, usuario_id):
           self.fecha_eliminacion = get_colombia_time()
           self.eliminado_por_id = usuario_id
       
       def restaurar(self):
           self.fecha_eliminacion = None
           self.eliminado_por_id = None
   ```

3. **Actualizar queries** (6h)
   ```python
   # Filtrar registros NO eliminados por defecto:
   Sede.query.filter_by(fecha_eliminacion=None).all()
   ```

4. **UI para restaurar** (4h)
   - Sección "Papelera" en admin
   - Botón "Restaurar" para cada registro

---

### ✅ F2-08: Testing Completo
**Tiempo estimado:** 24 horas  
**Prioridad:** 🔴 CRÍTICA

#### Áreas a testear:

1. **Tests unitarios** (8h)
   - Modelos
   - Utilidades
   - Validaciones

2. **Tests de integración** (8h)
   - Flujo completo de registro de visitante
   - Flujo de autorizaciones
   - CRUD de cada entidad

3. **Tests de seguridad** (4h)
   - Intentar bypass de autenticación
   - SQL injection
   - XSS
   - CSRF

4. **Tests de UI** (4h)
   - Selenium para flujos críticos
   - Verificar todos los formularios

---

## 📅 CRONOGRAMA SUGERIDO

### Sprint 1: Correcciones (5-8 horas)
**Semana 1 - Días 1-2**
- ✅ Quick Wins
- ✅ Función rota
- ✅ Ocultar errores

### Sprint 2: Features Críticos (48 horas)
**Semana 2 - Días 3-8**
- 🔨 UI Configuración (24h)
- 🔨 Visor Logs (24h)

### Sprint 3: Seguridad (24 horas)
**Semana 3 - Días 9-11**
- 🔨 CSRF (16h)
- 🔨 Timezone (8h)

### Sprint 4: Features Medios (24 horas)
**Semana 4 - Días 12-14**
- 🔨 Validación password (8h)
- 🔨 Soft Delete (16h)

### Sprint 5: Testing (24 horas)
**Semana 5 - Días 15-17**
- 🔨 Testing completo (24h)

### Sprint 6: Documentación (8 horas)
**Semana 5 - Día 18**
- 🔨 Swagger (8h)

---

## 💰 ESTIMACIÓN DE COSTOS

| Sprint | Horas | @ $50/hr |
|--------|-------|----------|
| Sprint 1 (Correcciones) | 8 | $400 |
| Sprint 2 (Features críticos) | 48 | $2,400 |
| Sprint 3 (Seguridad) | 24 | $1,200 |
| Sprint 4 (Features medios) | 24 | $1,200 |
| Sprint 5 (Testing) | 24 | $1,200 |
| Sprint 6 (Docs) | 8 | $400 |
| **TOTAL** | **136** | **$6,800** |

---

## ✅ CHECKLIST DE COMPLETITUD FULLSTACK

Al terminar FASE 2, verificar:

### Backend
- [ ] Todos los endpoints documentados (Swagger)
- [ ] Protección CSRF en todos los endpoints
- [ ] Testing >70% cobertura
- [ ] Logging completo
- [ ] Timezone correcto
- [ ] Soft delete implementado
- [ ] Rate limiting en todos los endpoints críticos

### Frontend
- [ ] UI de configuración completa y funcional
- [ ] Visor de logs de auditoría completo
- [ ] Validación de contraseña en tiempo real
- [ ] Todas las validaciones client-side
- [ ] Feedback visual en todas las operaciones
- [ ] Responsive design verificado
- [ ] Compatibilidad cross-browser

### Seguridad
- [ ] OWASP Top 10 mitigado
- [ ] Pen testing básico realizado
- [ ] Credenciales rotadas
- [ ] HTTPS configurado
- [ ] Headers de seguridad configurados

### Calidad
- [ ] Sin errores en consola
- [ ] Sin warnings en logs
- [ ] Performance optimizada
- [ ] Documentación completa
- [ ] README actualizado

---

## 🎯 RESULTADO FINAL

Sistema fullstack 100% completo con:
- ✅ Todas las funcionalidades implementadas
- ✅ Seguridad nivel profesional
- ✅ Testing completo
- ✅ Documentación completa
- ✅ Listo para producción

**Tiempo total:** 136 horas (~3-4 semanas con 1 desarrollador full-time)

---

## 📞 PRÓXIMOS PASOS

1. **Revisar este plan con el equipo**
2. **Priorizar features según necesidad del cliente**
3. **Asignar recursos (desarrolladores)**
4. **Comenzar con Sprint 1 (Correcciones)**
5. **Evaluar y ajustar plan según resultados**

---

*Plan generado el 18 de Marzo de 2026 - Listo para revisión con Claude*
