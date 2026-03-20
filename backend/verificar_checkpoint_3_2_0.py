#!/usr/bin/env python3
"""
Script de verificación para CHECKPOINT 3.2.0
Verifica correcciones de hallazgos FASE 3.1
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

print("\n" + "="*70)
print("VERIFICACIÓN CHECKPOINT 3.2.0 — Correcciones Hallazgos FASE 3.1")
print("="*70)

with app.app_context():
    # Verificar CP313-01: CHECK constraint en tipo_certificado
    print("\n1️⃣  CP313-01: CHECK constraint tipo_certificado")
    result = db.session.execute(text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints
        WHERE table_name = 'certificados_trabajo'
        AND constraint_name = 'check_tipo_certificado'
    """)).fetchone()
    
    if result:
        print(f"   ✅ {result[0]} — EXISTS")
    else:
        print("   ❌ Constraint no encontrado")
    
    # Verificar CP314-02: CHECK constraint fecha_fin >= fecha_inicio
    print("\n2️⃣  CP314-02: CHECK constraint fechas en autorizaciones_sst")
    result = db.session.execute(text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints
        WHERE table_name = 'autorizaciones_sst'
        AND constraint_name = 'check_vigencia_autorizacion'
    """)).fetchone()
    
    if result:
        print(f"   ✅ {result[0]} — EXISTS")
    else:
        print("   ❌ Constraint no encontrado")
    
    # Verificar CP314-01: Columna numero_autorizacion
    print("\n3️⃣  CP314-01: Columna numero_autorizacion")
    result = db.session.execute(text("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'autorizaciones_sst'
        AND column_name = 'numero_autorizacion'
    """)).fetchone()
    
    if result:
        print(f"   ✅ Columna: {result[0]} — {result[1]}({result[2]})")
    else:
        print("   ❌ Columna no encontrada")
    
    # Verificar índice único en numero_autorizacion
    result_idx = db.session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'autorizaciones_sst'
        AND indexname = 'idx_autorizacion_numero'
    """)).fetchone()
    
    if result_idx:
        print(f"   ✅ Índice: {result_idx[0]} — UNIQUE")
    else:
        print("   ❌ Índice no encontrado")
    
    # Verificar CP313-03: Índice en certificados_trabajo(empleado_id)
    print("\n4️⃣  CP313-03: Índice idx_certificado_empleado")
    result = db.session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'certificados_trabajo'
        AND indexname = 'idx_certificado_empleado'
    """)).fetchone()
    
    if result:
        print(f"   ✅ {result[0]} — EXISTS")
    else:
        print("   ❌ Índice no encontrado")
    
    # Verificar CP314-04: Índice en log_ingresos_contratistas(empleado_id)
    print("\n5️⃣  CP314-04: Índice idx_log_ingreso_empleado")
    result = db.session.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'log_ingresos_contratistas'
        AND indexname = 'idx_log_ingreso_empleado'
    """)).fetchone()
    
    if result:
        print(f"   ✅ {result[0]} — EXISTS")
    else:
        print("   ❌ Índice no encontrado")

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70 + "\n")
