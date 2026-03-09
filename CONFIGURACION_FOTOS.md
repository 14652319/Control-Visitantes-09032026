# 📸 Configuración de Almacenamiento de Fotografías

## Descripción General

El sistema almacena las fotografías de los visitantes según lo especificado en el **Levantamiento de Requerimientos**:

> "fotografia_visitante campo obligatorio no, cadena de texto de 5000 longitud (guardará la ruta donde se guardará la foto del visitante)"

## Configuración desde `.env`

La ubicación donde se guardan las fotos se configura en el archivo `.env` del backend:

```env
# Ubicación de Uploads (Fotografías de Visitantes)
# Ruta donde se guardarán las fotos capturadas automáticamente
# Puede ser relativa (../uploads/visitantes) o absoluta (D:/uploads/visitantes)
# Estructura de nombre de archivo: {TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg
# Ejemplo: CC-12345678-06032026_143052.jpg
# Esta carpeta se crea automáticamente si no existe
UPLOAD_FOLDER=../uploads/visitantes

# Tamaño máximo de archivo en bytes (5MB = 5242880 bytes)
MAX_FILE_SIZE=5242880
```

## Ventajas de Esta Configuración

✅ **No requiere modificar código**: Solo cambias el `.env`  
✅ **Fácil de cambiar en producción**: Cada ambiente puede tener su propia ruta  
✅ **Rutas absolutas o relativas**: Flexibilidad según necesidades  
✅ **Documentado**: El `.env` explica qué hace cada variable  

## Estructura de Nombres de Archivo

Las fotos se guardan automáticamente con el siguiente formato de nombre:

```
{TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg
```

**Ejemplo:**
```
CC-12345678-06032026_143052.jpg
```

Donde:
- **CC**: Tipo de identificación (Cédula de Ciudadanía)
- **12345678**: Número de identificación
- **06032026**: Fecha en formato DDMMYYYY (06 de marzo de 2026)
- **143052**: Hora en formato HHMMSS (14:30:52)
- **.jpg**: Extensión (siempre JPEG para optimizar tamaño)

### Otros Ejemplos

```
TI-98765432-06032026_150230.jpg    (Tarjeta de Identidad)
CE-A1234567-06032026_161545.jpg    (Cédula de Extranjería)
PS-AB123456-06032026_172035.jpg    (Pasaporte)
```

### Ventajas de Esta Estructura

✅ **Único**: Cada archivo tiene un nombre único (documento + fecha/hora exacta)  
✅ **Informativo**: El nombre del archivo identifica al visitante y momento de ingreso  
✅ **Ordenable**: Los archivos se organizan automáticamente por fecha  
✅ **Sin conflictos**: Imposible que dos archivos tengan el mismo nombre  
✅ **Fácil búsqueda**: Se puede buscar por número de documento directamente  

## Formatos Aceptados

El sistema acepta los siguientes formatos de imagen:
- ✅ JPG / JPEG
- ✅ PNG
- ✅ GIF

**Tamaño máximo**: 5MB (configurable en `.env`)

## Cómo Cambiar la Ubicación

### Opción 1: Ruta Relativa (Recomendado para desarrollo)

```env
UPLOAD_FOLDER=../uploads/visitantes
```

Esto guardará las fotos en:
```
proyecto/
  ├─ backend/
  └─ uploads/
      └─ visitantes/
          └─ CC-12345678-06032026_143052.jpg
```

### Opción 2: Ruta Absoluta (Recomendado para producción)

**Windows:**
```env
UPLOAD_FOLDER=C:/visitantes/fotos
```

**Linux/Mac:**
```env
UPLOAD_FOLDER=/var/www/visitantes/fotos
```

### Opción 3: Red / NAS (Para compartir entre servidores)

**Windows:**
```env
UPLOAD_FOLDER=//servidor/fotos/visitantes
```

**Linux:**
```env
UPLOAD_FOLDER=/mnt/nas/visitantes
```

## Almacenamiento en Base de Datos

El campo `fotografia_visitante` en la tabla `log_visitantes` almacena:

```sql
fotografia_visitante VARCHAR(500) NULL
```

**Ejemplo de valor guardado:**
```
../uploads/visitantes/CC-12345678-06032026_143052.jpg
```

## Permisos Requeridos

Asegúrate de que el usuario que ejecuta la aplicación tenga permisos de:

- ✅ **Lectura** en el directorio configurado
- ✅ **Escritura** para crear archivos
- ✅ **Creación de directorios** (el sistema crea carpetas automáticamente)

### Windows (PowerShell)
```powershell
# Verificar permisos
icacls "C:\uploads\visitantes"

# Dar permisos completos
icacls "C:\uploads\visitantes" /grant Users:F
```

### Linux
```bash
# Verificar permisos
ls -la /var/www/visitantes/fotos

# Dar permisos
sudo chmod 755 /var/www/visitantes/fotos
sudo chown www-data:www-data /var/www/visitantes/fotos
```

## Respaldo de Fotografías

Se recomienda configurar respaldos automáticos del directorio de fotos:

### Windows (Tarea Programada)
```powershell
# Copiar a otro disco
robocopy "C:\uploads\visitantes" "D:\backup\visitantes" /MIR /R:3 /W:10
```

### Linux (Cron)
```bash
# Agregar a crontab
0 2 * * * rsync -av /var/www/visitantes/fotos /backup/visitantes/
```

## Verificación del Sistema

Para verificar que la configuración está funcionando:

1. **Revisar el log de inicio**:
   ```
   [INFO] Upload folder configurado: ../uploads/visitantes
   ```

2. **Verificar que el directorio existe**:
   ```powershell
   # Windows
   Test-Path "../uploads/visitantes"
   
   # Linux
   ls -la ../uploads/visitantes
   ```

3. **Probar captura de foto** en el panel de operador

## Solución de Problemas

### Error: "Permission denied"
**Causa**: El usuario no tiene permisos de escritura  
**Solución**: Dar permisos al directorio (ver sección de Permisos)

### Error: "No such file or directory"
**Causa**: La ruta configurada no existe  
**Solución**: Crear el directorio manualmente o verificar la ruta en `.env`

### Las fotos no se guardan
**Causa**: Ruta incorrecta o permisos insuficientes  
**Solución**: 
1. Verificar `.env` → `UPLOAD_FOLDER`
2. Verificar permisos del directorio
3. Revisar logs del backend para ver el error exacto

## Migración de Fotos

Si necesitas cambiar la ubicación de fotos existentes:

1. **Copiar archivos** al nuevo directorio
2. **Actualizar `.env`** con la nueva ruta
3. **Actualizar base de datos**:

```sql
-- Cambiar rutas en la base de datos
UPDATE log_visitantes 
SET fotografia_visitante = REPLACE(fotografia_visitante, '../uploads/visitantes', 'C:/nueva/ruta')
WHERE fotografia_visitante IS NOT NULL;
```

4. **Reiniciar el servidor** backend

## ⚙️ Funcionamiento Automático del Guardado

### ✅ El sistema hace AUTOMÁTICAMENTE:

1. **Toma la ruta** de la variable `UPLOAD_FOLDER` del archivo `.env`
2. **Crea la carpeta** si no existe (sin intervención manual)
3. **Genera el nombre** del archivo siguiendo la estructura: `{TIPO_ID}-{NUM_ID}-{DDMMYYYY}_{HHMMSS}.jpg`
4. **Guarda la foto** en la ubicación configurada
5. **Registra la ruta** en la base de datos (campo `fotografia_visitante`)
6. **Muestra confirmación** de éxito al operador

### ❌ El operador NO necesita:

- ❌ Seleccionar la ubicación de guardado manualmente
- ❌ Escribir el nombre del archivo
- ❌ Especificar la ruta cada vez que captura una foto
- ❌ Crear carpetas manualmente

### 🎯 Proceso desde la vista del operador:

1. Operador abre formulario de registro de visitante
2. Ingresa datos del visitante
3. En la sección de fotografía:
   - **Opción A**: Hace clic en "Usar Cámara" → captura foto → muestra preview
   - **Opción B**: Hace clic en "Subir Archivo" → selecciona imagen → muestra preview
4. Si está conforme, hace clic en "Registrar Ingreso"
5. El sistema **automáticamente**:
   - Guarda la foto con el nombre correcto
   - En la ubicación configurada en `.env`
   - Sin preguntar nada al operador

### 🔧 Cambio de ubicación (solo administradores):

Para cambiar dónde se guardan las fotos:
1. Editar `backend/.env`
2. Cambiar el valor de `UPLOAD_FOLDER`
3. Reiniciar servidor backend
4. ¡Listo! Todas las fotos nuevas se guardarán en la nueva ubicación

**Nota importante**: Las fotos existentes permanecen en su ubicación original. Si deseas mover todas las fotos, sigue la sección "Migración de Fotos".

## Notas Adicionales

- Las fotos son **opcionales** al registrar un visitante
- El sistema crea el directorio automáticamente si no existe
- Las fotos se comprimen a calidad 85% en formato JPEG
- No hay límite de cantidad de fotos (limitado por espacio en disco)
- Se recomienda implementar limpieza de fotos antiguas según políticas de la empresa

---

## 🧹 Limpieza Automática de Fotografías

### Configuración de Retención

El sistema incluye un mecanismo para eliminar fotografías antiguas automáticamente, configurado en el archivo `.env`:

```env
# Retención y Limpieza de Fotografías
# DIAS_RETENCION_FOTOS: Número de días que se conservan las fotos antes de eliminarlas
# El sistema lee la fecha del nombre del archivo (formato: DDMMYYYY)
# Ejemplo: CC-14652319-09032026_120335.jpg → Fecha: 09/03/2026
DIAS_RETENCION_FOTOS=90

# BORRADO_AUTOMATICO_FOTOS: Activa/desactiva el borrado automático al iniciar servidor
# true: Al iniciar el servidor, elimina fotos antiguas automáticamente
# false: No elimina automáticamente, solo manual con el script limpieza_fotos.py
BORRADO_AUTOMATICO_FOTOS=false
```

### Cómo Funciona

1. **Extracción de fecha**: El sistema lee la fecha del nombre del archivo
   - Formato: `CC-14652319-09032026_120335.jpg`
   - Fecha extraída: `09/03/2026` (posición 11-18 del nombre)

2. **Cálculo de antigüedad**: Compara la fecha de la foto con la fecha actual

3. **Decisión de eliminación**: Si la foto tiene más de `DIAS_RETENCION_FOTOS` días, se elimina

### Script Manual de Limpieza

**Ubicación**: `backend/limpieza_fotos.py`

#### Modo Simulación (recomendado primero)
```bash
cd backend
python limpieza_fotos.py --dry-run
```
Muestra qué archivos se eliminarían **sin borrar nada**.

#### Limpieza Real
```bash
cd backend
python limpieza_fotos.py
```
Elimina realmente las fotos antiguas según `DIAS_RETENCION_FOTOS`.

#### Retención Personalizada
```bash
python limpieza_fotos.py --dias 30
```
Usa 30 días en lugar de la configuración del `.env`.

#### Ejemplo de Salida
```
======================================================================
🧹 LIMPIEZA DE FOTOGRAFÍAS DE VISITANTES
======================================================================
📁 Carpeta: D:\...\uploads\visitantes
📅 Fecha límite: 09/12/2025
⏳ Retención: 90 días
🔍 Modo: ELIMINACIÓN REAL
======================================================================

🗑️  ELIMINAR: CC-14652319-06122025_172150.jpg
   └─ Fecha: 06/12/2025 (94 días)
   └─ ✅ Eliminado

✅ CONSERVAR: CC-14652319-09032026_120335.jpg
   └─ Fecha: 09/03/2026 (0 días)

======================================================================
📊 RESUMEN DE LIMPIEZA
======================================================================
📁 Total archivos analizados: 2
🗑️  Archivos eliminados: 1
✅ Archivos conservados: 1
⚠️  Errores: 0
======================================================================
```

### Automatización con Tarea Programada (Recomendado)

#### Windows - Programador de Tareas

1. Abrir **Programador de Tareas** (Task Scheduler)
2. Click derecho → **Crear tarea básica**
3. **Nombre**: `Limpieza Fotos Visitantes`
4. **Desencadenador**: Diariamente a las **2:00 AM**
5. **Acción**: Iniciar un programa
   - **Programa**: `python.exe` (ruta completa, ej: `C:\Users\Usuario\AppData\Local\pythoncore-3.14-64\python.exe`)
   - **Argumentos**: `limpieza_fotos.py`
   - **Iniciar en**: `D:\0.A. Proyectos\1.1. Control de Acceso Visitantes\backend`
6. **Configuración adicional** (pestaña Configuración):
   - ✅ Ejecutar con los privilegios más altos
   - ✅ Ejecutar tanto si el usuario inició sesión como si no

#### Script Batch Alternativo

Crear archivo `limpieza_programada.bat` en la carpeta backend:
```batch
@echo off
cd /d "%~dp0"
python limpieza_fotos.py >> logs\limpieza_fotos.log 2>&1
```

Luego agregar este `.bat` al Programador de Tareas en lugar del comando Python directo.

### Opciones de Automatización

| Opción | Ventajas | Desventajas | Recomendado |
|--------|----------|-------------|-------------|
| **Tarea Programada** | Control preciso del horario, logs separados, no afecta inicio del servidor | Requiere configuración inicial | ✅ **SÍ** |
| **Al iniciar servidor** (`BORRADO_AUTOMATICO_FOTOS=true`) | No requiere configuración externa | Retrasa el inicio del servidor, se ejecuta múltiples veces si hay reinicios | ❌ No |
| **Manual** | Control total, verificación visual | Requiere recordar ejecutarlo, puede olvidarse | 🔶 Solo para pruebas |

### Recomendaciones

✅ **Usar tarea programada diaria a las 2:00 AM**  
✅ **Mantener `BORRADO_AUTOMATICO_FOTOS=false`**  
✅ **Configurar `DIAS_RETENCION_FOTOS` según política de la empresa**  
✅ **Hacer backups periódicos antes de ejecutar limpieza masiva**  
✅ **Siempre probar con `--dry-run` primero**

### Cambio de Retención

Para cambiar cuánto tiempo se guardan las fotos:

1. Editar `backend/.env`:
```env
DIAS_RETENCION_FOTOS=180  # Cambiar de 90 a 180 días
```

2. Reiniciar el servidor Flask (si se usa borrado automático)

3. La próxima ejecución del script usará el nuevo valor

### Advertencias

⚠️ **El borrado es PERMANENTE** - No se mueve a papelera de reciclaje  
⚠️ **Hacer backup antes de limpieza masiva**  
⚠️ **Verificar con `--dry-run` antes de ejecutar limpieza real**  
⚠️ **El formato del nombre de archivo debe ser exacto**: `{TIPO}-{NUM}-{DDMMYYYY}_{HHMMSS}.jpg`

## Referencia de Código

- **Configuración**: `backend/config.py`
- **Endpoint de subida**: `backend/app/routes/visitantes.py` → `guardar_foto()`
- **Frontend**: `frontend/operador.html` → Sección "Fotografía del Visitante"
- **Script de limpieza**: `backend/limpieza_fotos.py`

---

**Última actualización**: Marzo 9, 2026  
**Versión del sistema**: 1.0.0
