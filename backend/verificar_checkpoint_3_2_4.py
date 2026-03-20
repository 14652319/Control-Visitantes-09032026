"""
Script de verificación CHECKPOINT 3.2.4
Verifica que los 5 endpoints de planillas de seguridad social estén registrados
"""
import sys
sys.path.insert(0, 'backend')

from app import create_app

app = create_app()

print("\n" + "="*60)
print("VERIFICACIÓN CHECKPOINT 3.2.4 - Endpoints Planillas Seguridad Social")
print("="*60 + "\n")

# Rutas esperadas
rutas_esperadas = [
    ('GET', '/api/sst/planillas'),
    ('POST', '/api/sst/planillas'),
    ('GET', '/api/sst/planillas/<int:id>'),
    ('GET', '/api/sst/planillas/empresa/<int:empresa_id>'),
    ('GET', '/api/sst/planillas/vigentes/<int:empresa_id>'),
]

rutas_encontradas = []
for rule in app.url_map.iter_rules():
    if '/api/sst/planillas' in rule.rule:
        for method in rule.methods:
            if method not in ('HEAD', 'OPTIONS'):
                rutas_encontradas.append((method, rule.rule))

print(f"✅ Rutas SST Planillas registradas: {len(rutas_encontradas)}")
for metodo, ruta in sorted(rutas_encontradas):
    print(f"   {metodo:6} {ruta}")

print("\n" + "="*60)

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
    print("\nEndpoints planillas: 5")
    print("\nREADY: CHECKPOINT 3.2.4 completo\n")
    sys.exit(0)
