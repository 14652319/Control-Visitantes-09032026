# Instrucciones para iniciar el sistema

## Paso 1: Preparar el entorno

1. Abrir PowerShell o CMD como Administrador
2. Navegar a la carpeta del proyecto:
   ```
   cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\backend"
   ```

## Paso 2: Crear entorno virtual

```powershell
python -m venv venv
```

## Paso 3: Activar entorno virtual

```powershell
venv\Scripts\activate
```

## Paso 4: Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Paso 5: Configurar variables de entorno

1. Copiar el archivo .env.example a .env:
   ```powershell
   copy .env.example .env
   ```

2. (Opcional) Editar .env si necesitas cambiar configuraciones

## Paso 6: Verificar PostgreSQL

1. Asegúrate de que PostgreSQL esté corriendo
2. Verifica que puedas conectarte con las credenciales:
   - Usuario: postgres
   - Contraseña: G3st0radm$2025.
   - Puerto: 5432

## Paso 7: Crear base de datos

Abre pgAdmin o psql y ejecuta:

```sql
CREATE DATABASE control_visitantes;
```

## Paso 8: Inicializar la base de datos

```powershell
python init_db.py
```

Esto creará:
- Todas las tablas necesarias
- Datos de prueba
- Usuarios por defecto:
  * admin / Admin@2025 (usuario_master)
  * operador / Oper@2025 (usuario_operador)

## Paso 9: Iniciar el servidor

```powershell
python run.py
```

El servidor estará disponible en: http://localhost:5000

## Paso 10: Abrir el frontend

### Opción A: Directamente en el navegador
1. Navegar a: "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\frontend"
2. Hacer doble clic en index.html

### Opción B: Con servidor local (recomendado)

En otra terminal:

```powershell
cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\frontend"
python -m http.server 3000
```

Luego abrir: http://localhost:3000

## ¡Listo para usar!

Credenciales de prueba:
- **Administrador:** admin / Admin@2025
- **Operador:** operador / Oper@2025

## Comandos útiles

### Para detener el servidor
Presiona `Ctrl + C`

### Para desactivar el entorno virtual
```powershell
deactivate
```

### Para reiniciar todo desde cero
```powershell
python init_db.py
```
(Esto borrará todos los datos y volverá a crear las tablas)

## Solución de problemas

### Si no se puede conectar a PostgreSQL:
1. Verifica que el servicio de PostgreSQL esté corriendo
2. Confirma las credenciales en el archivo .env
3. Verifica que el puerto 5432 esté disponible

### Si hay errores de módulos no encontrados:
```powershell
pip install -r requirements.txt --upgrade
```

### Si el frontend no se conecta al backend:
1. Verifica que el backend esté corriendo en localhost:5000
2. Revisa la consola del navegador para ver errores
3. Asegúrate de que no haya problemas de CORS
