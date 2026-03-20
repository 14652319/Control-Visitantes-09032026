# 🎯 Configuración de Sentry - Monitoreo de Errores

## ¿Qué es Sentry?

Sentry es una plataforma de monitoreo de errores que captura automáticamente excepciones, errores y performance issues en producción.

**Qué hace por ti:**
- 🐛 Captura todos los errores automáticamente
- 📧 Te envía notificaciones por email/Slack
- 🔍 Muestra stack traces completos
- 📊 Gráficas de errores por tiempo
- 👥 Muestra qué usuarios afecta cada error
- 🚀 Tracking de performance (APM)

---

## 🚀 Setup Rápido (5 minutos)

### 1. Crear Cuenta en Sentry

```bash
# Ir a: https://sentry.io/signup/
# Crear cuenta gratis (10,000 eventos/mes)
```

### 2. Crear Proyecto

1. Click en "Create Project"
2. Seleccionar: **Flask**
3. Nombre del proyecto: `control-visitantes`
4. Copiar el **DSN** (empieza con `https://...@sentry.io/...`)

Ejemplo de DSN:
```
https://a1b2c3d4e5f6g7h8i9j0@o123456.ingest.sentry.io/7891011
```

### 3. Configurar en tu Proyecto

**Editar `backend/.env`:**

```bash
# Agregar al final del archivo .env
SENTRY_DSN=https://TU_DSN_AQUI@o123456.ingest.sentry.io/7891011
```

**¡Eso es todo!** 🎉 Sentry ya está activo.

---

## ✅ Verificar que Funciona

### Opción 1: Error de Prueba

Crear archivo `backend/test_sentry.py`:

```python
from app import create_app

app = create_app()

with app.app_context():
    # Esto enviará un error a Sentry
    try:
        1 / 0
    except Exception as e:
        app.logger.error("Error de prueba para Sentry", exc_info=True)
        raise

print("✅ Error enviado a Sentry. Revisa tu dashboard.")
```

Ejecutar:
```bash
cd backend
python test_sentry.py
```

### Opción 2: Desde la Aplicación

1. Iniciar servidor: `python run.py`
2. Navegar a un endpoint que no existe: `http://localhost:5000/api/error-test`
3. Ver el error en Sentry Dashboard

---

## 📊 Dashboard de Sentry

Una vez configurado, verás en Sentry:

```
┌─────────────────────────────────────────────────────────┐
│  SENTRY DASHBOARD                                        │
├─────────────────────────────────────────────────────────┤
│  🐛 Errores Recientes:                                   │
│                                                          │
│  1. ZeroDivisionError                                    │
│     backend/app/routes/visitantes.py:142                │
│     Hace 5 minutos - Afectó a 3 usuarios                │
│     [Ver Stack Trace] [Asignar] [Resolver]              │
│                                                          │
│  2. KeyError: 'visitante_id'                            │
│     backend/app/routes/reportes.py:89                   │
│     Hace 1 hora - Afectó a 1 usuario                    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  📈 Gráfica de Errores (últimas 24h):                   │
│  │                                                       │
│  │     ▄▄                                               │
│  │    ██                                                │
│  │  ▄▄██▄▄                                              │
│  └─────────────────────────────────────────────────────│
│                                                          │
│  Total errores hoy: 12                                   │
│  Usuarios afectados: 5                                   │
│  Tasa de error: 0.3%                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔔 Configurar Alertas

### Email
1. Ir a Settings → Alerts
2. Crear regla: "Enviar email cuando haya nuevo error"
3. Configurar destinatarios

### Slack
1. Integrar Slack: Settings → Integrations → Slack
2. Seleccionar canal (ej: #errores-produccion)
3. Configurar notificaciones

---

## 🎯 Casos de Uso

### 1. Error de Usuario No Encontrado

**Sin Sentry:**
```
Usuario reporta: "No puedo hacer login"
Tú: ¿Qué error da? ¿Cuándo pasó? ¿Qué hiciste?
Usuario: No sé, solo no funciona
```

**Con Sentry:**
```
Sentry te muestra:
- Error: User.DoesNotExist en auth.py línea 123
- Usuario: juan.perez@empresa.com
- Timestamp: 2026-03-13 10:42:15
- Request: POST /api/auth/login
- Variables locales: username='juan.perez', password=***
- Stack trace completo
```

### 2. Error Intermitente en Producción

**Sin Sentry:**
```
"A veces falla el registro de visitantes"
← No sabes cuándo, ni por qué
```

**Con Sentry:**
```
Sentry te muestra:
- Falla cuando num_identificacion tiene espacios
- Ocurrió 15 veces en las últimas 3 horas
- Afectó a 8 usuarios
- Gráfica muestra pico a las 2pm
→ Ahora sabes el patrón y puedes arreglarlo
```

---

## 📈 Métricas de Performance (APM)

Sentry también mide performance:

```python
# Ya configurado en app/__init__.py (traces_sample_rate=1.0)

# Sentry automáticamente mide:
- Tiempo de respuesta de cada endpoint
- Queries SQL lentas (>100ms)
- Llamadas HTTP externas
- Tiempo de renderizado
```

**Dashboard de Performance:**
```
Endpoints más lentos:
1. POST /api/visitantes/registrar - 450ms (⚠️ lento)
2. GET /api/reportes/excel - 320ms
3. GET /api/visitantes/listar - 180ms
```

---

## 🔒 Seguridad y Privacidad

### Datos que NO se envían:
- ❌ Contraseñas (filtradas automáticamente)
- ❌ Tokens JWT
- ❌ Variables con nombre "password", "secret", "token"

### Datos que SÍ se envían:
- ✅ Stack traces
- ✅ Variables locales (excepto sensibles)
- ✅ Request data (headers, query params)
- ✅ User context (username, email)

### Configurar filtros adicionales:

```python
# En app/__init__.py, agregar a sentry_sdk.init():
before_send=lambda event, hint: scrub_sensitive_data(event)

def scrub_sensitive_data(event):
    # Eliminar datos sensibles
    if 'request' in event:
        if 'headers' in event['request']:
            event['request']['headers'].pop('Authorization', None)
    return event
```

---

## 💰 Planes

| Plan | Eventos/mes | Precio | Ideal para |
|------|-------------|--------|-----------|
| **Developer** | 10,000 | Gratis | Desarrollo y MVP |
| **Team** | 50,000 | $26/mes | Pequeñas empresas |
| **Business** | 100,000 | $80/mes | Empresas medianas |

**Tu proyecto con 50-100 usuarios:** Plan Developer (gratis) es suficiente.

---

## 🚀 Estado Actual

```
✅ Sentry SDK instalado (requirements.txt)
✅ Integración en app/__init__.py
✅ Configuración en .env (SENTRY_DSN)
✅ Logger integrado
✅ Performance tracking activado
✅ Flask integration configurada
```

**Para activar:**
1. Crear cuenta en https://sentry.io
2. Crear proyecto Flask
3. Copiar DSN al .env
4. Reiniciar servidor

**¡Listo!** Sentry capturará todos los errores automáticamente.

---

## 📞 Recursos

- **Dashboard**: https://sentry.io/organizations/tu-org/issues/
- **Documentación**: https://docs.sentry.io/platforms/python/guides/flask/
- **Integración Flask**: https://docs.sentry.io/platforms/python/guides/flask/

---

## ✨ Beneficios Inmediatos

1. **Ver errores antes que los usuarios reporten**
2. **Datos completos para debugging** (no más "no sé qué pasó")
3. **Alertas instantáneas** por email/Slack
4. **Métricas de estabilidad** (tasa de error, usuarios afectados)
5. **Performance insights** (endpoints lentos, queries SQL)

**¡Monitoreo profesional en 5 minutos!** 🎉

---

**Versión:** 1.0.0  
**Fecha:** Marzo 13, 2026  
**Integrado en:** backend/app/__init__.py línea 32-43
