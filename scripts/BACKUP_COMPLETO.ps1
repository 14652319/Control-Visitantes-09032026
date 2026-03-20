# ===========================================================================
# BACKUP COMPLETO - Sistema Control de Visitantes
# Fecha: 18 Marzo 2026
# ===========================================================================

$FechaHora = Get-Date -Format "yyyyMMdd_HHmmss"
$ProyectoOrigen = "D:\0.A. Proyectos\1.1. Control de Acceso Visitantes"
$DestinoBackup = "D:\0.A. Proyectos\0.0. BackUp\BackUp 1.1. Control de Acceso Visitantes"
$NombreBackup = "backup_control_visitantes_$FechaHora"
$RutaBackupCompleto = Join-Path $DestinoBackup $NombreBackup

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "BACKUP COMPLETO - Control de Visitantes" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Crear directorio de backup
if (-not (Test-Path $DestinoBackup)) {
    Write-Host "[1/5] Creando directorio de backup..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DestinoBackup -Force | Out-Null
    Write-Host "      OK Directorio creado" -ForegroundColor Green
} else {
    Write-Host "[1/5] Directorio de backup existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Creando carpeta: $NombreBackup" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $RutaBackupCompleto -Force | Out-Null
Write-Host "      OK Carpeta creada" -ForegroundColor Green

# ===========================================================================
# COPIAR ARCHIVOS DEL PROYECTO
# ===========================================================================
Write-Host ""
Write-Host "[3/5] Copiando archivos del proyecto..." -ForegroundColor Yellow
Write-Host "      Origen: $ProyectoOrigen" -ForegroundColor Gray

$DestinoProyecto = Join-Path $RutaBackupCompleto "proyecto"

# Usar robocopy para copia eficiente
$RobocopyArgs = @(
    $ProyectoOrigen,
    $DestinoProyecto,
    "/MIR",
    "/R:2",
    "/W:3",
    "/XD", ".venv", "venv", "node_modules", "__pycache__", ".git", ".pytest_cache",
    "/XF", "*.pyc",
    "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"
)

$result = robocopy @RobocopyArgs

if ($LASTEXITCODE -le 7) {
    Write-Host "      OK Archivos copiados exitosamente" -ForegroundColor Green
    $TotalArchivos = (Get-ChildItem -Path $DestinoProyecto -Recurse -File | Measure-Object).Count
    Write-Host "      Total archivos: $TotalArchivos" -ForegroundColor Cyan
} else {
    Write-Host "      ADVERTENCIA en copia (codigo: $LASTEXITCODE)" -ForegroundColor Yellow
}

# ===========================================================================
# EXPORTAR BASE DE DATOS POSTGRESQL
# ===========================================================================
Write-Host ""
Write-Host "[4/5] Exportando base de datos PostgreSQL..." -ForegroundColor Yellow

$DestinoDB = Join-Path $RutaBackupCompleto "database"
New-Item -ItemType Directory -Path $DestinoDB -Force | Out-Null

$DBName = "control_visitantes"
$DBUser = "postgres"
$DBPassword = "G3st0radm`$2025.@"
$DBHost = "localhost"
$DBPort = "5432"

$env:PGPASSWORD = $DBPassword

Write-Host "      Base de datos: $DBName" -ForegroundColor Gray
Write-Host "      Usuario: $DBUser" -ForegroundColor Gray

# Export completo SQL
$ArchivoSQLCompleto = Join-Path $DestinoDB "backup_completo_${DBName}_${FechaHora}.sql"
Write-Host "      Exportando dump completo..." -ForegroundColor Gray

try {
    $pgDumpPath = "pg_dump"
    $pgDumpArgs = @(
        "-h", $DBHost,
        "-p", $DBPort,
        "-U", $DBUser,
        "-d", $DBName,
        "-F", "p",
        "--verbose",
        "--no-owner",
        "--no-acl",
        "-f", $ArchivoSQLCompleto
    )
    
    & $pgDumpPath @pgDumpArgs 2>&1 | Out-Null
    
    if (Test-Path $ArchivoSQLCompleto) {
        $TamanioMB = [math]::Round((Get-Item $ArchivoSQLCompleto).Length / 1MB, 2)
        Write-Host "      OK Dump SQL creado: ${TamanioMB} MB" -ForegroundColor Green
    } else {
        Write-Host "      ADVERTENCIA No se pudo crear dump SQL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ADVERTENCIA Error en export: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "      Verifica que PostgreSQL este en PATH" -ForegroundColor Gray
}

# Export formato custom
$ArchivoCustom = Join-Path $DestinoDB "backup_custom_${DBName}_${FechaHora}.backup"
Write-Host "      Exportando formato custom..." -ForegroundColor Gray

try {
    $pgDumpArgs = @(
        "-h", $DBHost,
        "-p", $DBPort,
        "-U", $DBUser,
        "-d", $DBName,
        "-F", "c",
        "--verbose",
        "-f", $ArchivoCustom
    )
    
    & $pgDumpPath @pgDumpArgs 2>&1 | Out-Null
    
    if (Test-Path $ArchivoCustom) {
        $TamanioMB = [math]::Round((Get-Item $ArchivoCustom).Length / 1MB, 2)
        Write-Host "      OK Backup custom creado: ${TamanioMB} MB" -ForegroundColor Green
    }
} catch {
    Write-Host "      ADVERTENCIA Error en backup custom" -ForegroundColor Yellow
}

# Export solo esquema
$ArchivoEsquema = Join-Path $DestinoDB "schema_only_${DBName}_${FechaHora}.sql"
Write-Host "      Exportando solo esquema..." -ForegroundColor Gray

try {
    $pgDumpArgs = @(
        "-h", $DBHost,
        "-p", $DBPort,
        "-U", $DBUser,
        "-d", $DBName,
        "-F", "p",
        "--schema-only",
        "--no-owner",
        "--no-acl",
        "-f", $ArchivoEsquema
    )
    
    & $pgDumpPath @pgDumpArgs 2>&1 | Out-Null
    
    if (Test-Path $ArchivoEsquema) {
        Write-Host "      OK Esquema exportado" -ForegroundColor Green
    }
} catch {
    Write-Host "      ADVERTENCIA Error en export esquema" -ForegroundColor Yellow
}

$env:PGPASSWORD = $null

# ===========================================================================
# CREAR ARCHIVO DE INFORMACION
# ===========================================================================
Write-Host ""
Write-Host "[5/5] Creando archivo de informacion..." -ForegroundColor Yellow

$InfoBackup = @"
================================================
BACKUP COMPLETO - Sistema Control de Visitantes
================================================

Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Usuario: $env:USERNAME
Computadora: $env:COMPUTERNAME

UBICACIONES:
------------
Proyecto origen: $ProyectoOrigen
Backup destino:  $RutaBackupCompleto

CONTENIDO:
----------
1. Carpeta "proyecto/": Codigo fuente completo
   - Backend (Flask + Python)
   - Frontend (HTML/JS/CSS)
   - Configuraciones (.env, requirements.txt)
   - Documentacion
   - Scripts de migracion
   
2. Carpeta "database/": Exportaciones PostgreSQL
   - backup_completo_*.sql (dump completo)
   - backup_custom_*.backup (formato custom)
   - schema_only_*.sql (solo estructura)

BASE DE DATOS:
--------------
Nombre: $DBName
Motor: PostgreSQL 15
Tablas: usuarios, sedes, dependencias, visitantes,
        log_visitantes, autorizaciones_ingreso,
        log_eventos, configuracion_sistema

RESTAURACION:
-------------
1. Copiar carpeta "proyecto/" a ubicacion deseada
2. Restaurar base de datos:
   psql -U postgres -d control_visitantes -f backup_completo_*.sql
   O:
   pg_restore -U postgres -d control_visitantes backup_custom_*.backup
3. Instalar dependencias:
   cd proyecto/backend
   pip install -r requirements.txt
4. Ejecutar: python run.py

================================================
"@

$ArchivoInfo = Join-Path $RutaBackupCompleto "README_BACKUP.txt"
$InfoBackup | Out-File -FilePath $ArchivoInfo -Encoding UTF8
Write-Host "      OK Archivo de informacion creado" -ForegroundColor Green

# ===========================================================================
# RESUMEN FINAL
# ===========================================================================
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "BACKUP COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ubicacion: $RutaBackupCompleto" -ForegroundColor Yellow
Write-Host ""

$TamanioTotal = (Get-ChildItem -Path $RutaBackupCompleto -Recurse -File | Measure-Object -Property Length -Sum).Sum
$TamanioTotalMB = [math]::Round($TamanioTotal / 1MB, 2)

Write-Host "Tamanio total: $TamanioTotalMB MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Contenido:" -ForegroundColor White
Get-ChildItem -Path $RutaBackupCompleto -Directory | ForEach-Object {
    $CantArchivos = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object).Count
    $TamanioCarpeta = [math]::Round((Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Host "  - $($_.Name): $CantArchivos archivos ($TamanioCarpeta MB)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "OK Backup listo para usar" -ForegroundColor Green
Write-Host "   Consulta README_BACKUP.txt para restauracion" -ForegroundColor Gray
Write-Host ""
