#!/usr/bin/env python3
"""
Script de verificación para CHECKPOINT 3.1.6 - FASE 3.1 completa
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

print("\n" + "="*70)
print("VERIFICACIÓN CHECKPOINT 3.1.6 - FASE 3.1 COMPLETA")
print("="*70)

with app.app_context():
    # 1. Verificar que existen las 8 tablas SST
    print("\n1️⃣  VERIFICANDO TABLAS SST:")
    tablas_sst = [
        'operadores_aportes',
        'empresas_contratistas',
        'empleados_contratistas',
        'certificados_trabajo',
        'planillas_ss',
        'autorizaciones_sst',
        'log_ingresos_contratistas'
    ]
    
    for tabla in tablas_sst:
        result = db.session.execute(text(
            f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='{tabla}')"
        )).scalar()
        
        estado = "✅" if result else "❌"
        print(f"   {estado} {tabla}")
    
    # 2. Verificar datos seeder de operadores_aportes
    print("\n2️⃣  VERIFICANDO DATOS SEEDER (13 operadores):")
    result = db.session.execute(text(
        "SELECT tipo, COUNT(*) FROM operadores_aportes GROUP BY tipo ORDER BY tipo"
    )).fetchall()
    
    total = 0
    for tipo, cantidad in result:
        print(f"   ✅ {tipo}: {cantidad}")
        total += cantidad
    
    print(f"   Total: {total} operadores")
    
    if total == 13:
        print("   ✅ CORRECTO: 13 operadores insertados")
    else:
        print(f"   ⚠️  ADVERTENCIA: Se esperaban 13, encontrados {total}")
    
    # 3. Verificar relaciones FK
    print("\n3️⃣  VERIFICANDO RELACIONES (FOREIGN KEYS):")
    fks = [
        ("empleados_contratistas", "empresa_id → empresas_contratistas"),
        ("empleados_contratistas", "eps_id → operadores_aportes"),
        ("empleados_contratistas", "afp_id → operadores_aportes"),
        ("empleados_contratistas", "arl_id → operadores_aportes"),
        ("certificados_trabajo", "empleado_id → empleados_contratistas"),
        ("planillas_ss", "empleado_id → empleados_contratistas"),
        ("autorizaciones_sst", "empresa_id → empresas_contratistas"),
        ("autorizaciones_sst", "funcionario_id → usuarios"),
        ("log_ingresos_contratistas", "empleado_id → empleados_contratistas"),
        ("log_ingresos_contratistas", "operador_id → usuarios")
    ]
    
    query_fk = """
        SELECT COUNT(*) 
        FROM information_schema.table_constraints 
        WHERE constraint_type = 'FOREIGN KEY' 
        AND table_name = :tabla
    """
    
    fks_por_tabla = {}
    for tabla, descripcion in fks:
        if tabla not in fks_por_tabla:
            fks_por_tabla[tabla] = []
        fks_por_tabla[tabla].append(descripcion)
    
    for tabla, relaciones in fks_por_tabla.items():
        count = db.session.execute(text(query_fk), {'tabla': tabla}).scalar()
        print(f"   ✅ {tabla}: {count} FK(s)")
        for rel in relaciones:
            print(f"      - {rel}")
    
    # 4. Verificar índices creados
    print("\n4️⃣  VERIFICANDO ÍNDICES ESPECIALES:")
    
    # Índice parcial para nit
    idx_nit = db.session.execute(text(
        "SELECT indexname FROM pg_indexes WHERE tablename='empresas_contratistas' AND indexname LIKE '%nit%'"
    )).fetchall()
    
    if idx_nit:
        for (idx,) in idx_nit:
            print(f"   ✅ {idx}")
    else:
        print("   ⚠️  No se encontró índice para nit")
    
    # Índice único para num_identificacion
    idx_identificacion = db.session.execute(text(
        "SELECT indexname FROM pg_indexes WHERE tablename='empresas_contratistas' AND indexname LIKE '%identificacion%'"
    )).fetchall()
    
    if idx_identificacion:
        for (idx,) in idx_identificacion:
            print(f"   ✅ {idx}")

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70 + "\n")
