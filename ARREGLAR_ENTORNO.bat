@echo off
echo ============================================================
echo REPARANDO ENTORNO VIRTUAL
echo ============================================================
echo.

cd /d "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes"

echo [1/5] Eliminando entorno virtual corrupto...
if exist .venv (
    rmdir /s /q .venv
    echo ✓ Entorno eliminado
) else (
    echo ✓ No hay entorno previo
)
echo.

echo [2/5] Creando nuevo entorno virtual con Python 3.12...
py -3.12 -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Error: Python 3.12 no está instalado
    echo.
    echo Por favor descarga Python 3.12 desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo ✓ Entorno creado
echo.

echo [3/5] Actualizando pip...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
echo ✓ Pip actualizado
echo.

echo [4/5] Instalando dependencias (esto puede tardar un poco)...
.\.venv\Scripts\pip.exe install Flask Flask-CORS Flask-SQLAlchemy Flask-Login Flask-Limiter Flask-Mail Flask-Migrate SQLAlchemy psycopg2-binary pandas openpyxl python-dotenv bcrypt
echo ✓ Dependencias instaladas
echo.

echo [5/5] Verificando instalación...
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import flask; print('Flask version:', flask.__version__)"
echo.

echo ============================================================
echo ✓ ENTORNO REPARADO CON ÉXITO
echo ============================================================
echo.
echo Para iniciar el servidor ejecuta:
echo    .\.venv\Scripts\python.exe backend\run.py
echo.
pause
