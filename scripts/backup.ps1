# ========================================
# SCRIPT DE BACKUP AUTOMÁTICO
# Sistema de Control de Visitantes
# Supertiendas Cañaveral SAS
# ========================================

<#
.SYNOPSIS
    Script de backup automático para PostgreSQL y archivos de uploads

.DESCRIPTION
    Este script crea backups diarios de:
    1. Base de datos PostgreSQL (control_visitantes)
    2. Carpeta de uploads (fotos de visitantes)
    
    Los backups se almacenan en la carpeta 'backups/' con fecha y hora
    Se mantienen los últimos 30 días de backups automáticamente

.NOTES
    Autor: Sistema Control Visitantes
    Fecha: 13 de marzo de 2026
    
.EXAMPLE
    # Ejecutar backup manualmente
    .\scripts\backup.ps1
    
    # Programar backup diario (Administrador de Tareas de Windows)
    1. Abrir "Programador de tareas"
    2. Crear tarea básica
    3. Nombre: "Backup Control Visitantes"
    4. Repetir: Diariamente a las 2:00 AM
    5. Acción: Iniciar programa
    6. Programa: powershell.exe
    7. Argumentos: -File "D:\0.A. Proyectos\1.1. Control de Acceso Visitantes\scripts\backup.ps1"
#>

# ========================================
# CONFIGURACIÓN
# ========================================

# Rutas (ajustar según tu instalación)
$PROYECTO_DIR = "D:\0.A. Proyectos\1.1. Control de Acceso Visitantes"
$BACKUP_DIR = Join-Path $PROYECTO_DIR "backups"
$UPLOADS_DIR = Join-Path $PROYECTO_DIR "uploads"
$LOG_FILE = Join-Path $PROYECTO_DIR "backups\backup.log"

# Configuración PostgreSQL
$PG_HOST = "localhost"
$PG_PORT = "5432"
$PG_USER = "postgres"
$PG_PASSWORD = "G3st0radm`$2025."
$PG_DATABASE = "control_visitantes"
$PG_BIN = "C:\Program Files\PostgreSQL\15\bin"  # Ajustar según versión instalada

# Días de retención de backups
$DIAS_RETENCION = 30

# Timestamp para nombres de archivo
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$FECHA_LEGIBLE = Get-Date -Format "dd/MM/yyyy HH:mm:ss"

# ========================================
# FUNCIONES
# ========================================

function Write-Log {
    param([string]$Message)
    $LogMessage = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LOG_FILE -Value $LogMessage
}

function Test-PostgreSQL {
    try {
        $pgDumpPath = Join-Path $PG_BIN "pg_dump.exe"
        if (-not (Test-Path $pgDumpPath)) {
            Write-Log "ERROR: pg_dump.exe no encontrado en $PG_BIN"
            Write-Log "Por favor, ajusta la variable PG_BIN con la ruta correcta de PostgreSQL"
            return $false
        }
        return $true
    }
    catch {
        Write-Log "ERROR al verificar PostgreSQL: $_"
        return $false
    }
}

# ========================================
# INICIO DEL SCRIPT
# ========================================

Write-Host "`n=========================================="
Write-Host "  BACKUP CONTROL DE VISITANTES" -ForegroundColor Green
Write-Host "  Supertiendas Cañaveral SAS"
Write-Host "=========================================="
Write-Host "Fecha: $FECHA_LEGIBLE`n"

# Crear carpeta de backups si no existe
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    Write-Log "Carpeta de backups creada: $BACKUP_DIR"
}

# Verificar PostgreSQL
if (-not (Test-PostgreSQL)) {
    Write-Host "`n❌ ERROR: No se puede continuar sin acceso a PostgreSQL`n" -ForegroundColor Red
    exit 1
}

# ========================================
# 1. BACKUP DE BASE DE DATOS
# ========================================

Write-Host "`n[1/3] Backup de Base de Datos PostgreSQL..."

$DB_BACKUP_FILE = Join-Path $BACKUP_DIR "db_$TIMESTAMP.sql"
$DB_BACKUP_GZ = "$DB_BACKUP_FILE.gz"

try {
    # Configurar password para pg_dump
    $env:PGPASSWORD = $PG_PASSWORD
    
    # Ejecutar pg_dump
    $pgDumpPath = Join-Path $PG_BIN "pg_dump.exe"
    $dumpArgs = @(
        "-h", $PG_HOST
        "-p", $PG_PORT
        "-U", $PG_USER
        "-d", $PG_DATABASE
        "-f", $DB_BACKUP_FILE
        "--no-password"
    )
    
    & $pgDumpPath $dumpArgs 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $DB_BACKUP_FILE)) {
        $fileSize = (Get-Item $DB_BACKUP_FILE).Length / 1MB
        Write-Host "   ✅ Backup de BD creado: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        Write-Log "Backup de BD exitoso: $DB_BACKUP_FILE ($([math]::Round($fileSize, 2)) MB)"
        
        # Comprimir el backup
        Write-Host "   Comprimiendo backup..."
        Compress-Archive -Path $DB_BACKUP_FILE -DestinationPath $DB_BACKUP_GZ -Force
        Remove-Item $DB_BACKUP_FILE
        
        $gzSize = (Get-Item $DB_BACKUP_GZ).Length / 1MB
        Write-Host "   ✅ Backup comprimido: $([math]::Round($gzSize, 2)) MB" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Error al crear backup de BD" -ForegroundColor Red
        Write-Log "ERROR: Falló el backup de BD"
    }
}
catch {
    Write-Host "   ❌ Excepción: $_" -ForegroundColor Red
    Write-Log "ERROR en backup de BD: $_"
}
finally {
    # Limpiar variable de entorno
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

# ========================================
# 2. BACKUP DE UPLOADS (FOTOS)
# ========================================

Write-Host "`n[2/3] Backup de Archivos (uploads/visitantes)..."

$UPLOADS_BACKUP = Join-Path $BACKUP_DIR "uploads_$TIMESTAMP.zip"

try {
    if (Test-Path $UPLOADS_DIR) {
        Compress-Archive -Path $UPLOADS_DIR -DestinationPath $UPLOADS_BACKUP -Force
        
        $uploadSize = (Get-Item $UPLOADS_BACKUP).Length / 1MB
        Write-Host "   ✅ Backup de uploads creado: $([math]::Round($uploadSize, 2)) MB" -ForegroundColor Green
        Write-Log "Backup de uploads exitoso: $UPLOADS_BACKUP ($([math]::Round($uploadSize, 2)) MB)"
    }
    else {
        Write-Host "   ⚠️  Carpeta uploads no encontrada" -ForegroundColor Yellow
        Write-Log "ADVERTENCIA: Carpeta uploads no encontrada"
    }
}
catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    Write-Log "ERROR en backup de uploads: $_"
}

# ========================================
# 3. LIMPIEZA DE BACKUPS ANTIGUOS
# ========================================

Write-Host "`n[3/3] Limpiando backups antiguos (>$DIAS_RETENCION días)..."

try {
    $fechaLimite = (Get-Date).AddDays(-$DIAS_RETENCION)
    $backupsAntiguos = Get-ChildItem -Path $BACKUP_DIR -Filter "*.gz" | Where-Object { $_.LastWriteTime -lt $fechaLimite }
    $backupsAntiguos += Get-ChildItem -Path $BACKUP_DIR -Filter "*.zip" | Where-Object { $_.LastWriteTime -lt $fechaLimite }
    
    if ($backupsAntiguos.Count -gt 0) {
        foreach ($backup in $backupsAntiguos) {
            Remove-Item $backup.FullName -Force
            Write-Host "   🗑️  Eliminado: $($backup.Name)" -ForegroundColor Gray
            Write-Log "Backup antiguo eliminado: $($backup.Name)"
        }
        Write-Host "   ✅ $($backupsAntiguos.Count) backup(s) antiguo(s) eliminado(s)" -ForegroundColor Green
    }
    else {
        Write-Host "   ℹ️  No hay backups antiguos que eliminar" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    Write-Log "ERROR en limpieza de backups: $_"
}

# ========================================
# RESUMEN FINAL
# ========================================

Write-Host "`n=========================================="
Write-Host "  ✅ BACKUP COMPLETADO" -ForegroundColor Green
Write-Host "=========================================="

# Listar backups actuales
$backupsActuales = Get-ChildItem -Path $BACKUP_DIR -Include "*.gz", "*.zip" -Recurse | Sort-Object LastWriteTime -Descending

Write-Host "`nBackups disponibles:" -ForegroundColor Cyan
foreach ($backup in $backupsActuales) {
    $edad = (Get-Date) - $backup.LastWriteTime
    $tamano = $backup.Length / 1MB
    Write-Host "  📦 $($backup.Name) - $([math]::Round($tamano, 2)) MB (hace $([math]::Round($edad.TotalDays, 0)) días)"
}

Write-Host "`nBackups totales: $($backupsActuales.Count)" -ForegroundColor Cyan
Write-Host "Espacio usado: $([math]::Round((($backupsActuales | Measure-Object -Property Length -Sum).Sum / 1MB), 2)) MB`n"

Write-Log "========== Proceso de backup completado =========="

# ========================================
# FIN DEL SCRIPT
# ========================================
