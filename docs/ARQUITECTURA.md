# Arquitectura del Sistema
# Sistema de Control de Visitantes

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
3. [Componentes del Sistema](#componentes-del-sistema)
4. [Base de Datos](#base-de-datos)
5. [Seguridad](#seguridad)
6. [Escalabilidad](#escalabilidad)
7. [Dependencias](#dependencias)

---

## 🎯 Visión General

El Sistema de Control de Visitantes es una aplicación web full-stack diseñada para gestionar el acceso de visitantes en las instalaciones de Supertiendas Cañaveral SAS.

### Características Principales

- ✅ **Autenticación y Autorización**: 3 roles (Master, Operador, Funcionario)
- ✅ **Registro de Visitantes**: Captura de datos personales y fotografía
- ✅ **Control de Acceso**: Registro de entrada/salida
- ✅ **Pre-autorizaciones**: Sistema de autorizaciones previas
- ✅ **Auditoría Completa**: Logs de todos los eventos
- ✅ **Reportes**: Exportación a Excel y estadísticas

---

## 🏗️ Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  index.html  │  │operador.html │  │  admin.html  │          │
│  │   (Login)    │  │  (Registro)  │  │  (Gestión)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
│                  ┌─────────▼─────────┐                          │
│                  │   API Client      │                          │
│                  │    (app.js)       │                          │
│                  └─────────┬─────────┘                          │
└────────────────────────────┼──────────────────────────────────┘
                             │ HTTP/HTTPS
                             │ (JSON API)
┌────────────────────────────▼──────────────────────────────────┐
│                          BACKEND                               │
│  ┌───────────────────────────────────────────────────────────┐│
│  │                     Flask Application                      ││
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          ││
│  │  │   Routes   │  │  Services  │  │  Models    │          ││
│  │  │ (API REST) │→ │ (Lógica)   │→ │(SQLAlchemy)│          ││
│  │  └────────────┘  └────────────┘  └────┬───────┘          ││
│  └──────────────────────────────────────────┼────────────────┘│
│                                              │                  │
│  ┌────────────┐  ┌────────────┐  ┌─────────▼──────┐          │
│  │  Logging   │  │Flask-Login │  │  Extensions    │          │
│  │  (Logger)  │  │  (Auth)    │  │  (CORS, etc)   │          │
│  └────────────┘  └────────────┘  └────────────────┘          │
└────────────────────────────┬───────────────────────────────────┘
                             │ PostgreSQL Protocol
┌────────────────────────────▼───────────────────────────────────┐
│                      BASE DE DATOS                             │
│                    PostgreSQL 15                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
│  │ Usuarios  │  │Visitantes │  │   Sedes   │  │  Logs     │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐                  │
│  │Dependencias│ │Autorizac. │  │LogEventos │                  │
│  └───────────┘  └───────────┘  └───────────┘                  │
└─────────────────────────────────────────────────────────────────┘

                             │
┌────────────────────────────▼───────────────────────────────────┐
│                     ALMACENAMIENTO                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Uploads    │  │     Logs     │  │   Backups    │        │
│  │   (Fotos)    │  │  (Archivos)  │  │   (DB/Files) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes del Sistema

### 1. Frontend

**Tecnologías:**
- HTML5 + CSS3 (TailwindCSS 3.3)
- Alpine.js 3.x (reactividad)
- JavaScript Vanilla (API client)

**Páginas:**
- `index.html`: Login y recuperación de contraseña
- `operador.html`: Registro de visitantes (sistema de pestañas)
- `admin.html`: Panel de administración completo
- `funcionario.html`: Portal de autorizaciones

**API Client (`app.js`):**
```javascript
const apiClient = {
  auth: { login, logout, checkSession, getCurrentUser },
  visitantes: { buscar, registrar, registrarIngreso, registrarSalida, listar },
  usuarios: { listar, crear, actualizar, resetearPassword },
  sedes: { listar, crear, actualizar },
  dependencias: { listar, crear, actualizar },
  autorizaciones: { listar, crear, aprobar, rechazar },
  reportes: { obtener, exportarExcel, estadisticas }
}
```

### 2. Backend

**Framework:** Flask 3.0

**Estructura de Directorios:**
```
backend/
├── app/
│   ├── __init__.py          # Factory de aplicación
│   ├── extensions.py        # Inicialización de extensiones
│   ├── models/              # Modelos SQLAlchemy (8 modelos)
│   │   ├── usuario.py
│   │   ├── sede.py
│   │   ├── dependencia.py
│   │   ├── visitante.py
│   │   ├── log_visitante.py
│   │   ├── autorizacion_ingreso.py
│   │   ├── log_evento.py
│   │   └── configuracion_sistema.py
│   ├── routes/              # Blueprints API REST (9 módulos)
│   │   ├── auth.py          # 5 endpoints
│   │   ├── visitantes.py    # 12 endpoints
│   │   ├── usuarios.py      # 8 endpoints
│   │   ├── sedes.py         # 6 endpoints
│   │   ├── dependencias.py  # 6 endpoints
│   │   ├── autorizaciones.py# 4 endpoints
│   │   ├── reportes.py      # 5 endpoints
│   │   └── configuracion.py # 1 endpoint
│   └── utils/
│       └── logger.py        # Sistema de logging
├── config.py                # Configuraciones
├── run.py                   # Punto de entrada
└── requirements.txt         # Dependencias
```

**Extensiones:**
- Flask-SQLAlchemy: ORM
- Flask-Login: Autenticación
- Flask-CORS: Cross-Origin Resource Sharing
- Flask-Limiter: Rate limiting (2000/día, 500/hora)
- Werkzeug: Seguridad (password hashing)

### 3. Base de Datos

**Motor:** PostgreSQL 15

**Modelos de Datos:**

#### Usuarios
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tipo_usuario VARCHAR(50) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    num_identificacion VARCHAR(50) UNIQUE NOT NULL,
    telefono VARCHAR(50),
    correo VARCHAR(100) UNIQUE,
    sede_id INTEGER REFERENCES sedes(id),
    estado VARCHAR(50) DEFAULT 'ACTIVO',
    intentos_fallidos INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW()
);
```

#### Visitantes
```sql
CREATE TABLE visitantes (
    id SERIAL PRIMARY KEY,
    tipo_identificacion VARCHAR(50) NOT NULL,
    num_identificacion VARCHAR(50) NOT NULL,
    primer_nombre VARCHAR(100) NOT NULL,
    segundo_nombre VARCHAR(100),
    primer_apellido VARCHAR(100) NOT NULL,
    segundo_apellido VARCHAR(100),
    num_telefono VARCHAR(100) NOT NULL,
    dir_correo VARCHAR(100) NOT NULL,
    empresa VARCHAR(100) NOT NULL,
    nit_empresa VARCHAR(50) NOT NULL,
    estado VARCHAR(50) DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uk_visitante_id UNIQUE (tipo_identificacion, num_identificacion)
);
CREATE INDEX idx_visitante_identificacion 
    ON visitantes(tipo_identificacion, num_identificacion);
```

#### Log de Visitas
```sql
CREATE TABLE log_visitantes (
    id SERIAL PRIMARY KEY,
    visitante_id INTEGER REFERENCES visitantes(id),
    usuario_registro_id INTEGER REFERENCES usuarios(id),
    sede_id INTEGER REFERENCES sedes(id),
    dependencia_id INTEGER REFERENCES dependencias(id),
    fecha_hora_entrada TIMESTAMP DEFAULT NOW(),
    fecha_hora_salida TIMESTAMP,
    motivo_visita TEXT,
    elementos_ingresados TEXT,
    observaciones TEXT,
    estado VARCHAR(50) DEFAULT 'EN_INSTALACIONES',
    ruta_foto VARCHAR(500)
);
CREATE INDEX idx_log_fecha_entrada ON log_visitantes(fecha_hora_entrada);
```

**Relaciones:**
- Usuario → Sede (many-to-one)
- Dependencia → Sede (many-to-one)
- LogVisitante → Visitante (many-to-one)
- LogVisitante → Usuario (many-to-one)
- AutorizacionIngreso → Dependencia (many-to-one)

---

## 🔒 Seguridad

### Autenticación y Autorización

**Flujo de Autenticación:**
```
1. Usuario envía credenciales → POST /api/auth/login
2. Backend valida usuario y contraseña
3. Si válido: Flask-Login crea sesión (cookie httponly)
4. Frontend almacena estado en localStorage
5. Cada request incluye cookie de sesión
6. Backend valida sesión con @login_required
```

**Roles y Permisos:**

| Rol | Permisos |
|-----|----------|
| **usuario_master** | Acceso total: gestión de usuarios, sedes, dependencias, configuración, reportes |
| **usuario_operador** | Registro de visitantes, ingresos/salidas, consultas básicas |
| **usuario_funcionario** | Pre-autorizaciones, consulta de visitantes autorizados |

**Medidas de Seguridad:**

1. **Contraseñas:**
   - Hash con bcrypt (salt rounds: 12)
   - Validación: mínimo 8 caracteres, mayúscula, minúscula, número, carácter especial
   - No se almacenan en texto plano

2. **Sesiones:**
   - Timeout: 45 minutos de inactividad
   - Cookie httponly (no accesible desde JavaScript)
   - Cookie SameSite=Lax
   - Regeneración de session_id después del login

3. **Rate Limiting:**
   - 2000 requests/día por IP
   - 500 requests/hora por IP
   - Límite especial login: 5 intentos/15 minutos

4. **Protección contra ataques:**
   - SQL Injection: Prevención via SQLAlchemy ORM
   - XSS: Sanitización de inputs en frontend
   - CSRF: Flask-WTF (en formularios)
   - Clickjacking: Headers X-Frame-Options

5. **Auditoría:**
   - Todos los eventos se registran en `log_eventos`
   - Información: usuario, acción, IP, timestamp, detalles

---

## 📈 Escalabilidad

### Arquitectura Actual

**Capacidad:**
- 10-100 usuarios concurrentes ✅
- 10,000-50,000 visitantes/año ✅
- 1-3 sedes ✅

### Plan de Escalabilidad

#### Fase 1: Optimización (100-500 usuarios)
```
┌────────────┐
│   NGINX    │ ← Load Balancer
└─────┬──────┘
      │
      ├─────┬─────┬─────┐
      │     │     │     │
   ┌──▼─┐┌──▼─┐┌──▼─┐ │
   │Flask││Flask││Flask│ │ ← Múltiples instancias
   └────┘└────┘└────┘ │
      │        │       │
      └────┬───┴───────┘
           │
      ┌────▼────┐
      │PostgreSQL│ ← Master-Replica
      │  +Redis │ ← Cache + Sessions
      └─────────┘
```

**Cambios necesarios:**
- Docker Swarm o Kubernetes
- Redis para sesiones y cache
- PostgreSQL con réplicas read-only
- CDN para archivos estáticos (fotos)

#### Fase 2: Alta Disponibilidad (500-5000 usuarios)
- PostgreSQL con Patroni (failover automático)
- Redis Sentinel (3 nodos)
- Celery para tareas asíncronas
- S3/MinIO para almacenamiento de fotos
- Prometheus + Grafana para monitoreo
- ELK Stack para logs centralizados

---

## 📦 Dependencias

### Backend (Python 3.11)
```
Flask==3.0.0              # Framework web
Flask-SQLAlchemy==3.1.1   # ORM
Flask-Login==0.6.3        # Autenticación
Flask-CORS==4.0.0         # CORS
psycopg2-binary==2.9.9    # Driver PostgreSQL
python-dotenv==1.0.0      # Variables de entorno
Werkzeug==3.0.1           # Utilidades (hashing)
pandas==2.1.4             # Exportación Excel
openpyxl==3.1.2           # Excel
gunicorn==21.2.0          # Servidor WSGI producción
pytest==7.4.3             # Testing
pytest-cov==4.1.0         # Coverage
```

### Frontend
```
TailwindCSS 3.3.0 (CDN)
Alpine.js 3.x (CDN)
Font Awesome 6.4.0 (CDN)
```

### Base de Datos
```
PostgreSQL 15.x
```

### DevOps
```
Docker 24.x
Docker Compose 2.x
```

---

## 🚀 Deployment

### Desarrollo
```bash
cd backend
python run.py
```

### Producción (Docker)
```bash
docker-compose up -d
```

### Producción (Manual)
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

## 📊 Métricas del Sistema

**Código:**
- Líneas de código Python: ~5,500
- Líneas de código Frontend: ~5,300
- Líneas de documentación: ~25,000+
- Tests: 15+ tests (cobertura estimada 60%)

**Base de Datos:**
- Tablas: 8
- Índices: 6
- Foreign Keys: 5
- Triggers: 0

**API:**
- Endpoints: 47
- Blueprints: 9
- Middleware: 3 (CORS, Rate Limiting, Session Management)

---

**Versión:** 1.0.0  
**Fecha:** Marzo 13, 2026  
**Autor:** Supertiendas Cañaveral SAS
