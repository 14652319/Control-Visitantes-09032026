# Sistema de Control de Visitantes
# Supertiendas Cañaveral SAS

## 🎯 Descripción

Sistema completo de control de acceso de visitantes desarrollado con Python/Flask (backend) y HTML/JavaScript/TailwindCSS (frontend).

### Características Principales

✅ **Autenticación y Autorización**
- Login seguro con bcrypt
- Dos roles: `usuario_master` y `usuario_operador`
- Bloqueo automático después de 10 intentos fallidos
- Sesiones con tiempo de expiración (45 minutos)

✅ **Gestión de Visitantes**
- Registro completo de datos personales y empresariales
- Búsqueda rápida por tipo y número de identificación
- Captura de fotografía del visitante
- Control de entrada y salida
- Registro de elementos ingresados (tecnología, herramientas, etc.)

✅ **Multi-sede y Dependencias**
- Gestión de múltiples sedes de la empresa
- Dependencias asociadas a sedes específicas
- Control de acceso por sede según rol de usuario

✅ **Reportes y Auditoría**
- Listado de visitas en tiempo real
- Exportación a Excel
- Log completo de eventos del sistema
- Estadísticas de visitas

✅ **Diseño Profesional**
- Interfaz moderna con TailwindCSS y Alpine.js
- Diseño responsivo (móvil, tablet, desktop)
- Colores corporativos verde (Supertiendas Cañaveral)
- Experiencia de usuario optimizada

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.9+**
- **Flask 3.0** - Framework web
- **PostgreSQL** - Base de datos
- **SQLAlchemy** - ORM
- **Flask-Login** - Autenticación
- **bcrypt** - Hash de contraseñas
- **Pandas** - Generación de reportes Excel

### Frontend
- **HTML5**
- **TailwindCSS 3.0** - Framework CSS
- **Alpine.js** - Reactividad
- **Font Awesome 6.4** - Iconos

---

## 📋 Requisitos Previos

- Python 3.9 o superior
- PostgreSQL 12 o superior
- Navegador web moderno (Chrome, Firefox, Edge)

---

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes"
```

### 2. Configurar PostgreSQL

Asegúrate de que PostgreSQL esté instalado y corriendo.

**Credenciales por defecto:**
- Usuario: `postgres`
- Contraseña: `G3st0radm$2025.`
- Puerto: `5432`

**Crear la base de datos:**

```sql
CREATE DATABASE control_visitantes;
```

### 3. Configurar el entorno virtual

```bash
cd backend
python -m venv venv
```

**Activar el entorno virtual:**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:

```bash
copy .env.example .env
```

Edita `.env` si necesitas cambiar alguna configuración.

### 6. Inicializar la base de datos

```bash
python init_db.py
```

Este script:
- Creará todas las tablas necesarias
- Insertará datos de prueba
- Creará usuarios por defecto

**Usuarios creados:**
- **Master:** Usuario: `admin` | Contraseña: `Admin@2025`
- **Operador:** Usuario: `operador` | Contraseña: `Oper@2025`

---

## ▶️ Ejecución

### Iniciar el servidor backend

```bash
cd backend
python run.py
```

El servidor estará disponible en: `http://localhost:5000`

### Abrir el frontend

Abre el archivo `frontend/index.html` en tu navegador web, o usa un servidor local:

**Con Python:**
```bash
cd frontend
python -m http.server 3000
```

Luego abre: `http://localhost:3000`

**Con Node.js (http-server):**
```bash
cd frontend
npx http-server -p 3000
```

---

## 👥 Uso del Sistema

### Operador (usuario_operador)

1. **Iniciar sesión** con credenciales de operador
2. **Registrar visitante:**
   - Ingresar tipo y número de identificación
   - Si el visitante no existe, registrarlo
   - Completar datos de la visita
   - Seleccionar dependencia destino
   - Indicar elementos ingresados
   - (Opcional) Capturar fotografía
   - Guardar el ingreso
3. **Registrar salida:** Marcar cuando el visitante abandona las instalaciones
4. **Ver listado:** Consultar visitas del día

### Administrador (usuario_master)

1. **Iniciar sesión** con credenciales de master
2. **Gestión de usuarios:**
   - Crear operadores
   - Crear otros administradores
   - Resetear contraseñas
   - Desbloquear usuarios
3. **Gestión de sedes:**
   - Crear nuevas sedes
   - Modificar sedes existentes
4. **Gestión de dependencias:**
   - Crear dependencias
   - Asociar a sedes específicas
5. **Reportes:**
   - Ver estadísticas
   - Exportar a Excel
   - Consultar logs de eventos

---

## 📁 Estructura del Proyecto

```
Control de Acceso Visitantes/
│
├── backend/
│   ├── app/
│   │   ├── models/          # Modelos de base de datos
│   │   ├── routes/          # Endpoints API
│   │   ├── services/        # Lógica de negocio
│   │   ├── utils/           # Utilidades
│   │   ├── extensions.py    # Extensiones Flask
│   │   └── __init__.py      # Factory app
│   │
│   ├── migrations/          # Migraciones de DB (generadas)
│   ├── config.py            # Configuración
│   ├── init_db.py           # Inicialización de BD
│   ├── run.py               # Punto de entrada
│   ├── requirements.txt     # Dependencias Python
│   └── .env.example         # Variables de entorno
│
├── frontend/
│   ├── assets/
│   │   ├── js/
│   │   │   └── app.js       # API client y utilidades
│   │   ├── css/
│   │   └── images/
│   │
│   ├── index.html           # Login
│   ├── operador.html        # Dashboard operador
│   └── admin.html           # Dashboard admin
│
├── uploads/
│   └── visitantes/          # Fotografías de visitantes
│
├── Levantamiento de requerimientos control visitantes.txt
└── README.md
```

---

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Validación de sesiones
- ✅ Protección CSRF
- ✅ Control de acceso basado en roles
- ✅ Bloqueo de usuarios por intentos fallidos
- ✅ Timeout de sesión por inactividad
- ✅ Logs de auditoría completos
- ✅ Validación de inputs (SQL injection prevention)

---

## 📊 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Obtener usuario actual
- `GET /api/auth/check-session` - Verificar sesión

### Visitantes
- `GET /api/visitantes/buscar` - Buscar visitante
- `POST /api/visitantes/registrar` - Registrar visitante
- `POST /api/visitantes/ingreso` - Registrar ingreso
- `PUT /api/visitantes/salida/:id` - Registrar salida
- `GET /api/visitantes/listar` - Listar visitas
- `POST /api/visitantes/foto/:id` - Guardar fotografía

### Usuarios (solo master)
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/usuarios/` - Crear usuario
- `PUT /api/usuarios/:id` - Actualizar usuario
- `POST /api/usuarios/:id/resetear-password` - Resetear contraseña

### Sedes (master)
- `GET /api/sedes/` - Listar sedes
- `POST /api/sedes/` - Crear sede
- `PUT /api/sedes/:id` - Actualizar sede

### Dependencias (master)
- `GET /api/dependencias/` - Listar dependencias
- `POST /api/dependencias/` - Crear dependencia
- `PUT /api/dependencias/:id` - Actualizar dependencia

### Reportes
- `GET /api/reportes/visitas` - Reporte de visitas
- `POST /api/reportes/visitas/excel` - Exportar a Excel
- `GET /api/reportes/estadisticas` - Estadísticas

---

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL

```
psycopg2.OperationalError: could not connect to server
```

**Solución:**
- Verifica que PostgreSQL esté corriendo
- Confirma las credenciales en `.env`
- Verifica que la base de datos `control_visitantes` exista

### Error de CORS

```
Access-Control-Allow-Origin error
```

**Solución:**
- Asegúrate de que Flask-CORS esté instalado
- Verifica que el frontend use el puerto correcto
- Revisa la configuración de CORS en `config.py`

### Sesión expira inmediatamente

**Solución:**
- Verifica que las cookies estén habilitadas en el navegador
- Asegúrate de usar `credentials: 'include'` en las peticiones fetch
- Revisa la configuración de cookies en `config.py`

---

## 📝 Licencia

© 2026 Supertiendas Cañaveral SAS - Todos los derechos reservados

---

## 👨‍💻 Desarrollo

Desarrollado con las mejores prácticas de programación:
- Clean Architecture
- SOLID Principles
- RESTful API Design
- Security Best Practices
- Responsive Design
- Code Documentation

---

## 📞 Soporte

Para soporte o consultas sobre el sistema, contactar al administrador del sistema.

---

**¡Sistema listo para usar!** 🎉
