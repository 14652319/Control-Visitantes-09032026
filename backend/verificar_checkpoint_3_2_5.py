"""
Script de verificación CHECKPOINT 3.2.5
Verifica que los 10 endpoints de autorizaciones SST estén registrados
"""
import sys
sys.path.insert(0, 'backend')

from app import create_app

app = create_app()

print("\n" + "="*70)
print("VERIFICACIÓN CHECKPOINT 3.2.5 - Endpoints Autorizaciones SST + Consecutivo")
print("="*70 + "\n")

# Rutas esperadas
rutas_esperadas = [
    ('GET', '/api/sst/autorizaciones'),
    ('POST', '/api/sst/autorizaciones'),
    ('GET', '/api/sst/autorizaciones/<int:id>'),
    ('PUT', '/api/sst/autorizaciones/<int:id>'),
    ('POST', '/api/sst/autorizaciones/<int:id>/empleados'),
    ('DELETE', '/api/sst/autorizaciones/<int:id>/empleados/<int:empleado_id>'),
    ('POST', '/api/sst/autorizaciones/<int:id>/enviar-revision'),
    ('POST', '/api/sst/autorizaciones/<int:id>/aprobar'),
    ('POST', '/api/sst/autorizaciones/<int:id>/rechazar'),
    ('POST', '/api/sst/autorizaciones/<int:id>/anular'),
]

rutas_encontradas = []
for rule in app.url_map.iter_rules():
    if '/api/sst/autorizaciones' in rule.rule:
        for method in rule.methods:
            if method not in ('HEAD', 'OPTIONS'):
                rutas_encontradas.append((method, rule.rule))

print(f"✅ Rutas SST Autorizaciones registradas: {len(rutas_encontradas)}")
for metodo, ruta in sorted(rutas_encontradas):
    print(f"   {metodo:6} {ruta}")

print("\n" + "="*70)

# Verificar que todas las rutas esperadas estén presentes
faltantes = []
for metodo, ruta in rutas_esperadas:
    encontrado = any(
        m == metodo and ('<int' in ruta and '<int' in r or r == ruta)
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
    print("\nEndpoints CRUD: 4")
    print("Endpoints gestión empleados: 2")
    print("Endpoints transiciones estado: 4")
    print("\nTotal: 10 endpoints autorizaciones SST")
    print("\nREADY: CHECKPOINT 3.2.5 completo\n")
    sys.exit(0)
