# 🚀 INICIO RÁPIDO

## Para Iniciar el Sistema en 5 Pasos

### 1. Crear entorno virtual
```powershell
cd "d:\0.A. Proyectos\1.1. Control de Acceso Visitantes\backend"
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Preparar archivo de configuración
```powershell
copy .env.example .env
```

### 4. Inicializar base de datos
Asegúrate de que PostgreSQL esté corriendo, luego ejecuta:
```powershell
python init_db.py
```

### 5. Iniciar el servidor
```powershell
python run.py
```

## Abrir el Frontend

Navega a: `frontend\index.html` en tu navegador

O usa un servidor local:
```powershell
cd ..\frontend
python -m http.server 3000
```

Luego abre: http://localhost:3000

## Credenciales de Prueba

- **Administrador:** `admin` / `Admin@2025`
- **Operador:** `operador` / `Oper@2025`

## ¡Listo para usar! 🎉

Para más detalles, consulta:
- `README.md` - Documentación completa
- `INSTRUCCIONES.md` - Instrucciones detalladas paso a paso
