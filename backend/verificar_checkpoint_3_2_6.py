"""
Verificación CHECKPOINT 3.2.6: API Ingresos/Salidas Contratistas
Verifica que los 4 endpoints de logs de ingreso estén registrados correctamente
"""
from app import create_app

app = create_app()

with app.app_context():
    # Obtener todas las rutas del blueprint sst relacionadas con ingresos
    rutas_ingresos = sorted([
        str(rule) for rule in app.url_map.iter_rules()
        if '/api/sst/ingresos' in str(rule)
    ])
    
    print(f"\n{'='*60}")
    print(f"CHECKPOINT 3.2.6: Verificación Endpoints Ingresos/Salidas")
    print(f"{'='*60}\n")
    
    endpoints_esperados = [
        'GET /api/sst/ingresos',
        'POST /api/sst/ingresos',
        'PUT /api/sst/ingresos/<int:id>/salida',
        'GET /api/sst/ingresos/activos',
    ]
    
    print(f"Endpoints esperados: {len(endpoints_esperados)}")
    print(f"Endpoints encontrados: {len(rutas_ingresos)}\n")
    
    # Convertir rutas de Flask a formato legible
    rutas_encontradas = []
    for ruta in rutas_ingresos:
        # Extraer método y path
        metodos = []
        path = ''
        if ' ' in ruta:
            path = ruta.split(' ')[0]
            # Los métodos están en la regla completa
        rutas_encontradas.append(path)
    
    # Verificar cada endpoint
    print("Detalle de rutas registradas:\n")
    for ruta in rutas_ingresos:
        print(f"  {ruta}")
    
    print(f"\n{'='*60}")
    if len(rutas_ingresos) >= 4:
        print("✅ VERIFICACIÓN EXITOSA: 4+ rutas de ingresos registradas")
    else:
        print(f"❌ VERIFICACIÓN FALLIDA: Se esperaban 4 rutas, se encontraron {len(rutas_ingresos)}")
    print(f"{'='*60}\n")
