"""
Script de verificación CHECKPOINT 3.2.2
Verifica que los 5 endpoints de empresas contratistas estén registrados
"""
import sys
sys.path.insert(0, 'backend')

from app import create_app

app = create_app()

print("\n" + "="*60)
print("VERIFICACIÓN CHECKPOINT 3.2.2 - Endpoints Empresas SST")
print("="*60 + "\n")

# Rutas esperadas
rutas_esperadas = [
    ('GET', '/api/sst/empresas'),
    ('POST', '/api/sst/empresas'),
    ('GET', '/api/sst/empresas/<int:id>'),
    ('PUT', '/api/sst/empresas/<int:id>'),
    ('GET', '/api/sst/empresas/buscar'),
]

rutas_encontradas = []
for rule in app.url_map.iter_rules():
    if '/api/sst/empresas' in rule.rule:
        for method in rule.methods:
            if method not in ('HEAD', 'OPTIONS'):
                rutas_encontradas.append((method, rule.rule))

print(f"✅ Rutas SST Empresas registradas: {len(rutas_encontradas)}")
for metodo, ruta in sorted(rutas_encontradas):
    print(f"   {metodo:6} {ruta}")

print("\n" + "="*60)

# Verificar que todas las rutas esperadas estén presentes
faltantes = []
for metodo, ruta in rutas_esperadas:
    encontrado = any(
        m == metodo and (r == ruta or (ruta.endswith('>') and ruta.replace('<int:id>', '<id>') in r))
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
    print("\nREADY: CHECKPOINT 3.2.2 completo\n")
    sys.exit(0)
