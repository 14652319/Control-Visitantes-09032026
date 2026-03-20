"""Quick test script for SST routes."""
import sys, os
sys.path.insert(0, '.')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()
with app.test_client() as client:
    # Login
    resp = client.post('/api/auth/login', json={'usuario': 'admin', 'password': 'Admin2025*'})
    d = resp.get_json()
    print(f"Login: {resp.status_code}, success={d.get('success')}, msg={d.get('message')}")
    
    if not d.get('success'):
        # Try other passwords
        for pwd in ['Admin123*', 'admin', 'Admin2024*']:
            resp = client.post('/api/auth/login', json={'usuario': 'admin', 'password': pwd})
            d = resp.get_json()
            print(f"  Try '{pwd}': {d.get('success')}, msg={d.get('message')}")
            if d.get('success'):
                break
    
    if d.get('success'):
        # Test SST endpoints
        resp = client.get('/api/sst/health')
        print(f"Health: {resp.status_code} {resp.get_json()}")
        
        resp = client.get('/api/sst/operadores?tipo=EPS')
        print(f"Operadores EPS: {resp.status_code} {resp.get_json()}")
        
        resp = client.get('/api/sst/empresas')
        print(f"Empresas: {resp.status_code} {resp.get_json()}")
        
        resp = client.get('/api/sst/empleados')
        print(f"Empleados: {resp.status_code} {resp.get_json()}")
    else:
        print("Could not login, skipping SST tests")
