# Changelog
Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-13

### 🎉 Release Inicial - Aplicación Full Stack Completa

#### ✨ Added - Nuevas Funcionalidades

##### Backend
- **Sistema de Autenticación**: Implementación completa con Flask-Login
  - Login con validación de credenciales
  - Bloqueo automático después de 10 intentos fallidos
  - Sistema de roles: Master, Operador, Funcionario
  - Sesiones con timeout de 45 minutos
  - Endpoints de recuperación de contraseña

- **Gestión de Visitantes**: CRUD completo
  - Registro de visitantes con datos personales y empresariales
  - Búsqueda por identificación (CC, CE, TI, PA, NIT)
  - Búsqueda por NIT de empresa (autocompletado)
  - Captura de fotografía del visitante
  - Sistema de nomenclatura: {TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg
  - Filtros avanzados: búsqueda, fecha, estado
  - Paginación: 100 registros por página
  - Sistema de pestañas en interfaz operador

- **Control de Acceso**:
  - Registro de entrada con dependencia destino
  - Registro de salida con timestamps
  - Estados: EN_INSTALACIONES / SALIO
  - Log completo de visitas con auditoría

- **Sistema de Pre-autorizaciones**:
  - Creación de autorizaciones por funcionarios
  - Estados: PENDIENTE / APROBADA / RECHAZADA / EXPIRADA
  - Validación al momento del ingreso
  - Notificaciones de contacto

- **Gestión Administrativa**:
  - CRUD de usuarios con validación de roles
  - CRUD de sedes (multi-sede)
  - CRUD de dependencias asociadas a sedes
  - Configuración del sistema

- **Reportes y Auditoría**:
  - Exportación a Excel con todos los campos
  - Estadísticas de visitas
  - Log de eventos del sistema con 5 niveles (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Auditoría completa de acciones de usuario

##### Frontend
- **Interfaz de Usuario Moderna**:
  - Login responsivo con logo corporativo
  - Dashboard de operador con sistema de pestañas
  - Panel de administración completo
  - Portal de funcionario para autorizaciones
  - Diseño con TailwindCSS 3.3
  - Reactividad con Alpine.js 3.x

- **Componentes**:
  - Formularios con validación en tiempo real
  - Búsqueda con debounce (500ms)
  - Filtros de fecha y estado
  - Paginación interactiva
  - Captura de foto con cámara web
  - Feedback visual (success, error, warning)

##### Base de Datos
- **8 Tablas Relacionadas**:
  - `usuarios`: Gestión de usuarios del sistema
  - `sedes`: Múltiples ubicaciones
  - `dependencias`: Áreas dentro de sedes
  - `visitantes`: Registro de visitantes
  - `log_visitantes`: Historial de visitas
  - `autorizaciones_ingreso`: Pre-autorizaciones
  - `log_eventos`: Auditoría del sistema
  - `configuracion_sistema`: Parámetros configurables

- **Índices Optimizados**:
  - Índice en `visitantes.num_identificacion`
  - Índice compuesto en `(tipo_identificacion, num_identificacion)`
  - Índice en `log_visitantes.fecha_hora_entrada`
  - Índice en `usuarios.username`

#### 🔒 Security - Seguridad

- **Contraseñas**:
  - Hash con bcrypt (12 salt rounds)
  - Validación fuerte: mínimo 8 caracteres, mayúscula, minúscula, número, carácter especial
  - SECRET_KEY y JWT_SECRET_KEY con valores aleatorios de 64 caracteres

- **Autenticación**:
  - Flask-Login para gestión de sesiones
  - Cookies httponly y secure
  - Regeneración de session_id post-login
  - Timeout automático de sesión

- **Rate Limiting**:
  - 2000 requests/día por IP
  - 500 requests/hora por IP
  - Protección contra fuerza bruta

- **Protecciones**:
  - SQL Injection: Prevención via SQLAlchemy ORM
  - XSS: Sanitización de inputs
  - CORS configurado correctamente

#### 📝 Documentation - Documentación

- **README.md**: Guía completa de instalación y uso (550+ líneas)
- **DOCUMENTACION_ESTADO_ACTUAL.md**: Estado completo del sistema (18,000+ líneas)
  - Estructura de base de datos
  - Todos los 47 endpoints API
  - Frontend y backend completos
  - Métricas y estadísticas
- **docs/ARQUITECTURA.md**: Documentación de arquitectura técnica
  - Diagramas de componentes
  - Flujos de datos
  - Decisiones de diseño
  - Plan de escalabilidad
- **docs/CONTRIBUTING.md**: Guía de contribución
  - Estándares de código
  - Proceso de pull request
  - Templates de issues
- **docs/api-spec.yaml**: Especificación OpenAPI 3.0
  - 47 endpoints documentados
  - Esquemas de datos
  - Ejemplos de requests/responses

#### 🧪 Testing - Pruebas

- **Setup de Testing**:
  - pytest configurado
  - Coverage con pytest-cov
  - Tests unitarios para auth y visitantes
  - Fixtures para datos de prueba
  - Base de datos SQLite en memoria para tests

- **Tests Implementados** (15+ tests):
  - `test_auth.py`: 8 tests de autenticación
  - `test_visitantes.py`: 10 tests de visitantes
  - Coverage objetivo: 70%+

#### 🐳 DevOps - Infraestructura

- **Docker**:
  - `Dockerfile` para backend con Python 3.11
  - `docker-compose.yml` con 4 servicios
  - PostgreSQL con persistencia de datos
  - Nginx como reverse proxy (opcional)
  - Redis para cache y rate limiting (opcional)
  - Health checks configurados

- **CI/CD**:
  - GitHub Actions pipeline completo
  - Tests automáticos en cada push
  - Linting con flake8
  - Coverage reporting
  - Build y push de imágenes Docker
  - Deploy automático a producción (main branch)
  - Security scanning con Trivy

#### 🛠️ Tools - Herramientas

- **Sistema de Logging**:
  - Logger estructurado con rotación de archivos
  - 3 archivos de log: app.log, error.log, debug.log
  - Formato colorizado en consola
  - Rotación automática (10MB, 10 backups)
  - Helpers para logging: `log_request`, `log_user_action`, `log_error`

- **Scripts de Utilidad**:
  - `scripts/backup.ps1`: Backup automático de DB y archivos
    - Dump de PostgreSQL comprimido
    - Backup de carpeta uploads
    - Retención de 30 días
    - Logs de operaciones
  - `init_db.py`: Inicialización de base de datos
  - `create_usuario_funcionario.py`: Crear usuarios funcionarios

#### 📦 Dependencies - Dependencias

**Backend** (requirements.txt):
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.1
pandas==2.1.4
openpyxl==3.1.2
gunicorn==21.2.0
```

**Testing**:
```
pytest==7.4.3
pytest-cov==4.1.0
flake8==7.0.0
black==23.12.1
```

---

## [0.9.0] - 2026-03-06

### ✨ Added
- Integración de logo corporativo en todas las páginas HTML
- Sistema de pestañas en interfaz de operador
  - Pestaña "Registrar Visitante"
  - Pestaña "Visitantes de Hoy" con contador de badge

### 🔧 Changed
- Nomenclatura de archivos de fotos: {TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg
- Configuración centralizada de uploads en .env (UPLOAD_FOLDER)
- Eliminación de botón "Subir Archivo", solo captura con cámara

### 📝 Documentation
- Actualización de levantamiento de requerimientos (Secciones 31-33)
  - Sección 31: Sistema de pestañas
  - Sección 32: Configuración de fotos
  - Sección 33: Búsqueda, filtros y paginación

---

## [0.8.0] - 2026-03-05

### ✨ Added
- Sistema de búsqueda por identificación con debounce (500ms)
- Filtros de fecha (desde/hasta) con default al día actual
- Filtro por estado (EN_INSTALACIONES / SALIO / todos)
- Paginación de 100 registros por página
- Botón "Limpiar Filtros"
- Contador de total de registros

### 🔧 Changed
- Endpoint `/api/visitantes/listar` actualizado con nuevos parámetros
- Respuesta incluye: total, pagina, por_pagina, total_paginas

---

## [0.7.0] - 2026-03-04

### ✨ Added
- Sistema de pre-autorizaciones de ingreso
- CRUD completo de autorizaciones
- Estado de autorizaciones: PENDIENTE, APROBADA, RECHAZADA, EXPIRADA
- Validación de autorización al momento del ingreso

---

## [0.6.0] - 2026-03-01

### ✨ Added
- Sistema de captura de fotografía con cámara web
- Almacenamiento automático de fotos en uploads/visitantes/
- Validación de dispositivos de cámara disponibles

---

## [0.5.0] - 2026-02-28

### ✨ Added
- Exportación de reportes a Excel con pandas
- Filtros de fecha para reportes
- Estadísticas de visitas

---

## [0.4.0] - 2026-02-25

### ✨ Added
- Sistema de gestión de dependencias
- Asociación de dependencias a sedes
- CRUD completo de dependencias

---

## [0.3.0] - 2026-02-20

### ✨ Added
- Sistema multi-sede
- CRUD de sedes
- Asociación de usuarios a sedes

---

## [0.2.0] - 2026-02-15

### ✨ Added
- Sistema de gestión de usuarios
- Roles: Master, Operador, Funcionario
- Bloqueo automático por intentos fallidos

---

## [0.1.0] - 2026-02-10

### ✨ Added
- Implementación inicial del backend con Flask
- Sistema base de autenticación
- CRUD básico de visitantes
- Base de datos PostgreSQL
- Frontend con HTML/TailwindCSS/Alpine.js

---

## Tipos de Cambios

- **Added**: Nuevas funcionalidades
- **Changed**: Cambios en funcionalidad existente
- **Deprecated**: Funcionalidades que serán eliminadas
- **Removed**: Funcionalidades eliminadas
- **Fixed**: Corrección de bugs
- **Security**: Mejoras de seguridad

---

[1.0.0]: https://github.com/supertiendas/control-visitantes/releases/tag/v1.0.0
[0.9.0]: https://github.com/supertiendas/control-visitantes/releases/tag/v0.9.0
[0.8.0]: https://github.com/supertiendas/control-visitantes/releases/tag/v0.8.0
