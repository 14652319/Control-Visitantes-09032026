# Script para reparar entorno virtual corrupto
# Python 3.14.3 es incompatible con Flask

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "REPARANDO ENTORNO VIRTUAL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes"

Write-Host "[1/5] Eliminando entorno virtual corrupto..." -ForegroundColor Yellow
if (Test-Path .venv) {
    Remove-Item -Recurse -Force .venv
    Write-Host "✓ Entorno eliminado" -ForegroundColor Green
} else {
    Write-Host "✓ No hay entorno previo" -ForegroundColor Green
}
Write-Host ""

Write-Host "[2/5] Creando nuevo entorno virtual con Python 3.12..." -ForegroundColor Yellow
$result = & py -3.12 -m venv .venv 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Python 3.12 no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Intentando con Python 3.11..." -ForegroundColor Yellow
    $result = & py -3.11 -m venv .venv 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python 3.11 tampoco está disponible" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUCIÓN:" -ForegroundColor Yellow
        Write-Host "1. Descarga Python 3.12 desde: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Durante instalación, marca 'Add Python to PATH'" -ForegroundColor White
        Write-Host "3. Ejecuta este script nuevamente" -ForegroundColor White
        Write-Host ""
        pause
        exit 1
    }
}
Write-Host "✓ Entorno creado" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Actualizando pip..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
Write-Host "✓ Pip actualizado" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] Instalando dependencias (esto puede tardar 1-2 minutos)..." -ForegroundColor Yellow
& .\.venv\Scripts\pip.exe install Flask Flask-CORS Flask-SQLAlchemy Flask-Login Flask-Limiter Flask-Mail Flask-Migrate SQLAlchemy psycopg2-binary pandas openpyxl python-dotenv bcrypt --quiet
Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

Write-Host "[5/5] Verificando instalación..." -ForegroundColor Yellow
$pythonVersion = & .\.venv\Scripts\python.exe --version
$flaskVersion = & .\.venv\Scripts\python.exe -c "import flask; print(flask.__version__)"
Write-Host "  Python: $pythonVersion" -ForegroundColor Cyan
Write-Host "  Flask: $flaskVersion" -ForegroundColor Cyan
Write-Host ""

Write-Host "============================================================" -ForegroundColor Green
Write-Host "✓ ENTORNO REPARADO CON ÉXITO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar el servidor ejecuta:" -ForegroundColor Yellow
Write-Host "   .\.venv\Scripts\python.exe backend\run.py" -ForegroundColor White
Write-Host ""
pause
