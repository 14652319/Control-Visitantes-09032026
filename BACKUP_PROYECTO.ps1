# ============================================================================
# SCRIPT DE BACKUP COMPLETO - Sistema Control de Visitantes
# Fecha: 18 Marzo 2026
# ============================================================================

# Configuracion
$FechaHora = Get-Date -Format "yyyyMMdd_HHmmss"
$ProyectoOrigen = "D:\0.A. Proyectos\1.1. Control de Acceso Visitantes"
$DestinoBackup = "D:\0.A. Proyectos\0.0. BackUp\BackUp 1.1. Control de Acceso Visitantes"
$NombreBackup = "backup_control_visitantes_$FechaHora"
$RutaBackupCompleto = Join-Path $DestinoBackup $NombreBackup

# Crear directorio de backup si no existe
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "BACKUP COMPLETO - Sistema Control de Visitantes" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $DestinoBackup)) {
    Write-Host "[1/5] Creando directorio de backup..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DestinoBackup -Force | Out-Null
    Write-Host "      ✓ Directorio creado: $DestinoBackup" -ForegroundColor Green
} else {
    Write-Host "[1/5] Directorio de backup existe" -ForegroundColor Green
}

# Crear carpeta específica para este backup
Write-Host ""
Write-Host "[2/5] Creando carpeta de backup: $NombreBackup" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $RutaBackupCompleto -Force | Out-Null
Write-Host "      ✓ Carpeta creada" -ForegroundColor Green

# ============================================================================
# PASO 1: COPIAR TODOS LOS ARCHIVOS DEL PROYECTO
# ============================================================================
Write-Host ""
Write-Host "[3/5] Copiando archivos del proyecto..." -ForegroundColor Yellow
Write-Host "      Origen: $ProyectoOrigen" -ForegroundColor Gray
Write-Host "      Destino: $RutaBackupCompleto\proyecto" -ForegroundColor Gray

$DestinoProyecto = Join-Path $RutaBackupCompleto "proyecto"

# Copiar con exclusiones (no copiar venv, node_modules, __pycache__, .git)
$ExcluirCarpetas = @(
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".pytest_cache",
    "*.pyc"
)

# Usar robocopy para copia eficiente
$RobocopyExclude = $ExcluirCarpetas -join " "
$RobocopyArgs = @(
    $ProyectoOrigen,
    $DestinoProyecto,
    "/MIR",  # Mirror (copia incremental)
    "/R:2",  # Reintentos
    "/W:3",  # Espera entre reintentos
    "/XD", ".venv", "venv", "node_modules", "__pycache__", ".git", ".pytest_cache",
    "/XF", "*.pyc",
    "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"  # Menos verbose
)

$result = robocopy @RobocopyArgs

if ($LASTEXITCODE -le 7) {  # Robocopy exitcode <= 7 = éxito
    Write-Host "      ✓ Archivos copiados exitosamente" -ForegroundColor Green
    
    # Contar archivos copiados
    $TotalArchivos = (Get-ChildItem -Path $DestinoProyecto -Recurse -File | Measure-Object).Count
    Write-Host "      → Total archivos: $TotalArchivos" -ForegroundColor Cyan
} else {
    Write-Host "      ⚠ Advertencia en copia (código: $LASTEXITCODE)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 2: EXPORTAR BASE DE DATOS POSTGRESQL
# ============================================================================
Write-Host ""
Write-Host "[4/5] Exportando base de datos PostgreSQL..." -ForegroundColor Yellow

$DestinoDB = Join-Path $RutaBackupCompleto "database"
New-Item -ItemType Directory -Path $DestinoDB -Force | Out-Null

# Configuración de PostgreSQL (leer del proyecto)
$DBName = "control_visitantes"
$DBUser = "postgres"
$DBPassword = "G3st0radm`$2025.@"
$DBHost = "localhost"
$DBPort = "5432"

# Establecer variable de entorno para password
$env:PGPASSWORD = $DBPassword

Write-Host "      Base de datos: $DBName" -ForegroundColor Gray
Write-Host "      Usuario: $DBUser" -ForegroundColor Gray
Write-Host "      Host: ${DBHost}:${DBPort}" -ForegroundColor Gray

# 1. Export completo con pg_dump (esquema + datos)
$ArchivoSQLCompleto = Join-Path $DestinoDB "backup_completo_${DBName}_${FechaHora}.sql"
Write-Host "      Exportando dump completo..." -ForegroundColor Gray

try {
    $pgDumpPath = "pg_dump"
    $pgDumpArgs = @(
        "-h", $DBHost,
        "-p", $DBPort,
        "-U", $DBUser,
        "-d", $DBName,
        "-F", "p",  # Plain text format
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
        Write-Host "      ADVERTENCIA No se pudo crear el dump SQL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ADVERTENCIA Error al exportar base de datos: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "      - Asegurate de que PostgreSQL este instalado y en PATH" -ForegroundColor Gray
}

# 2. Export en formato custom (más rápido para restaurar)
$ArchivoCustom = Join-Path $DestinoDB "backup_custom_${DBName}_${FechaHora}.backup"
Write-Host "      Exportando formato custom..." -ForegroundColor Gray

try {
    $pgDumpArgs = @(
        "-h", $DBHost,
        "-p", $DBPort,
        "-U", $DBUser,
        "-d", $DBName,
        "-F", "c",  # Custom format
        "--verbose",
        "-f", $ArchivoCustom
    )
    
    & $pgDumpPath @pgDumpArgs 2>&1 | Out-Null
    
    if (Test-Path $ArchivoCustom) {
        $TamañoMB = [math]::Round((Get-Item $ArchivoCustom).Length / 1MB, 2)
        Write-Host "      ✓ Backup custom creado: ${TamañoMB} MB" -ForegroundColor Green
    }
} catch {
    Write-Host "      ⚠ Error en backup custom" -ForegroundColor Yellow
}

# 3. Export solo el esquema (estructura sin datos)
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
        Write-Host "      ✓ Esquema exportado" -ForegroundColor Green
    }
} catch {
    Write-Host "      ⚠ Error en export de esquema" -ForegroundColor Yellow
}

# Limpiar variable de entorno
$env:PGPASSWORD = $null

# ============================================================================
# PASO 3: CREAR ARCHIVO DE INFORMACIÓN DEL BACKUP
# ============================================================================
Write-Host ""
Write-Host "[5/5] Creando archivo de información..." -ForegroundColor Yellow

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
1. Carpeta "proyecto/": Código fuente completo
   - Backend (Flask + Python)
   - Frontend (HTML/JS/CSS)
   - Configuraciones (.env, requirements.txt)
   - Documentación (README, docs)
   - Scripts de migración
   
2. Carpeta "database/": Exportaciones PostgreSQL
   - backup_completo_*.sql (dump completo en texto plano)
   - backup_custom_*.backup (formato custom para pg_restore)
   - schema_only_*.sql (solo estructura de tablas)

BASE DE DATOS:
--------------
Nombre: $DBName
Motor: PostgreSQL 15
Tablas incluidas:
  - usuarios
  - sedes
  - dependencias
  - visitantes
  - log_visitantes
  - autorizaciones_ingreso
  - log_eventos
  - configuracion_sistema

RESTAURACIÓN:
-------------
Para restaurar el proyecto:
1. Copiar carpeta "proyecto/" a la ubicación deseada
2. Restaurar base de datos:
   psql -U postgres -d control_visitantes -f backup_completo_*.sql
   O:
   pg_restore -U postgres -d control_visitantes backup_custom_*.backup

3. Instalar dependencias:
   cd proyecto/backend
   pip install -r requirements.txt

4. Ejecutar:
   python run.py

================================================
"@

$ArchivoInfo = Join-Path $RutaBackupCompleto "README_BACKUP.txt"
$InfoBackup | Out-File -FilePath $ArchivoInfo -Encoding UTF8
Write-Host "      ✓ Archivo de información creado" -ForegroundColor Green

# ============================================================================
# RESUMEN FINAL
# ============================================================================
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "BACKUP COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ubicación: $RutaBackupCompleto" -ForegroundColor Yellow
Write-Host ""

# Calcular tamaño total del backup
$TamañoTotal = (Get-ChildItem -Path $RutaBackupCompleto -Recurse -File | Measure-Object -Property Length -Sum).Sum
$TamañoTotalMB = [math]::Round($TamañoTotal / 1MB, 2)

Write-Host "Tamaño total: $TamañoTotalMB MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Contenido del backup:" -ForegroundColor White
Get-ChildItem -Path $RutaBackupCompleto -Directory | ForEach-Object {
    $CantArchivos = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object).Count
    $TamanioCarpeta = [math]::Round((Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Host "  - $($_.Name): $CantArchivos archivos ($TamanioCarpeta MB)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✓ Backup listo para usar" -ForegroundColor Green
Write-Host "  Consulta README_BACKUP.txt para instrucciones de restauración" -ForegroundColor Gray
Write-Host ""
