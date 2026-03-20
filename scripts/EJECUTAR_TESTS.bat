@echo off
echo ====================================
echo EJECUTANDO TESTS
echo Sistema de Control de Visitantes
echo ====================================
echo.

cd /d "%~dp0..\backend"

echo [1/2] Activando entorno virtual...
call ..\.venv\Scripts\activate.bat

echo.
echo [2/2] Ejecutando tests con pytest...
echo.

python -m pytest tests/ -v --tb=short --maxfail=5

echo.
echo ====================================
echo TESTS COMPLETADOS
echo ====================================
echo.
echo Para ver reporte de cobertura:
echo   pytest tests/ --cov=app --cov-report=html
echo   start htmlcov\index.html
echo.
pause
