#!/usr/bin/env python3
"""
Verificar que las rutas SST están registradas
"""
from app import create_app

app = create_app()

with app.app_context():
    rules = [str(r) for r in app.url_map.iter_rules() if '/api/sst' in str(r)]
    
    if rules:
        print('✅ Rutas SST registradas:')
        for r in sorted(rules):
            print(f'  {r}')
    else:
        print('❌ No se encontraron rutas SST')
