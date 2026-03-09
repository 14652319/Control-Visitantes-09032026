# ⚡ COMANDOS RÁPIDOS

## Instalación Inicial (una sola vez)

```powershell
# 1. Navegar al backend
cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\backend"

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Copiar configuración
copy .env.example .env

# 6. Inicializar base de datos (asegúrate que PostgreSQL esté corriendo)
python init_db.py
```

## Uso Diario

```powershell
# Activar entorno virtual (si no está activo)
cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\backend"
venv\Scripts\activate

# Iniciar servidor
python run.py
```

## Frontend

```powershell
# Opción 1: Abrir directamente
# Doble clic en: frontend\index.html

# Opción 2: Servidor local (recomendado)
cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\frontend"
python -m http.server 3000
# Luego abrir: http://localhost:3000
```

## Mantenimiento

```powershell
# Detener servidor
Ctrl + C

# Desactivar entorno virtual
deactivate

# Reiniciar base de datos (BORRA TODOS LOS DATOS)
cd backend
python init_db.py

# Ver logs en tiempo real
# Los logs se muestran en la consola donde corre el servidor
```

## Credenciales Predeterminadas

**Administrador:** `admin` / `Admin@2025`  
**Operador:** `operador` / `Oper@2025`

## URLs Importantes

- **Backend API:** http://localhost:5000
- **Frontend:** http://localhost:3000 (o abrir index.html)
- **Health Check:** http://localhost:5000/health

## Solución Rápida de Problemas

**Error de conexión a BD:**
```powershell
# Verificar que PostgreSQL esté corriendo
# Servicios de Windows > PostgreSQL
```

**Error de módulos:**
```powershell
pip install -r requirements.txt --upgrade
```

**Puerto 5000 ocupado:**
```powershell
# Cambiar en .env:
# PORT=5001
```

## Para Producción

```powershell
# Cambiar en .env:
FLASK_ENV=production
FLASK_DEBUG=False

# Usar un servidor WSGI como Gunicorn (Linux) o Waitress (Windows)
pip install waitress
waitress-serve --port=5000 run:app
```

---

**Consulta README.md para documentación completa**
