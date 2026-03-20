"""
Script de verificación CHECKPOINT 3.2.3
Verifica que los 9 endpoints de empleados + certificados estén registrados
"""
import sys
sys.path.insert(0, 'backend')

from app import create_app

app = create_app()

print("\n" + "="*60)
print("VERIFICACIÓN CHECKPOINT 3.2.3 - Endpoints Empleados + Certificados SST")
print("="*60 + "\n")

# Rutas esperadas
rutas_esperadas = [
    ('GET', '/api/sst/empleados'),
    ('POST', '/api/sst/empleados'),
    ('GET', '/api/sst/empleados/<int:id>'),
    ('PUT', '/api/sst/empleados/<int:id>'),
    ('GET', '/api/sst/empleados/buscar'),
    ('GET', '/api/sst/certificados'),
    ('POST', '/api/sst/certificados'),
    ('GET', '/api/sst/certificados/empleado/<int:empleado_id>'),
    ('PUT', '/api/sst/certificados/<int:id>'),
]

rutas_encontradas = []
for rule in app.url_map.iter_rules():
    if '/api/sst/empleados' in rule.rule or '/api/sst/certificados' in rule.rule:
        for method in rule.methods:
            if method not in ('HEAD', 'OPTIONS'):
                rutas_encontradas.append((method, rule.rule))

print(f"✅ Rutas SST Empleados + Certificados registradas: {len(rutas_encontradas)}")
for metodo, ruta in sorted(rutas_encontradas):
    print(f"   {metodo:6} {ruta}")

print("\n" + "="*60)

# Verificar que todas las rutas esperadas estén presentes
faltantes = []
for metodo, ruta in rutas_esperadas:
    encontrado = any(
        m == metodo and (r == ruta or (('int' in ruta or 'empleado_id' in ruta) and ruta.split('/')[-1].replace('<int:', '<').replace('<int','<') in r))
        for m, r in rutas_encontradas
    )
    if not encontrado:
        faltantes.append(f"{metodo} {ruta}")

if faltantes:
    print("❌ FALTAN:")
    for f in faltantes:
        print(f"   {f}")
    sys.exit(1)
else:
    print("✅ TODOS LOS ENDPOINTS REGISTRADOS CORRECTAMENTE")
    print("\nEndpoints empleados: 5")
    print("Endpoints certificados: 4")
    print("\nREADY: CHECKPOINT 3.2.3 completo\n")
    sys.exit(0)
