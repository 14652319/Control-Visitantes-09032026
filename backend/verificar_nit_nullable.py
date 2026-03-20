#!/usr/bin/env python3
"""
Script temporal para verificar que nit es nullable
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    result = db.session.execute(text(
        "SELECT column_name, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_name='empresas_contratistas' AND column_name='nit'"
    )).fetchone()
    
    if result:
        print(f"✅ Verificación exitosa:")
        print(f"   Columna: {result[0]}")
        print(f"   Nullable: {result[1]}")
        
        if result[1] == 'YES':
            print("✅ CORRECTO: nit permite NULL")
        else:
            print("❌ ERROR: nit no permite NULL")
    else:
        print("❌ No se encontró la columna nit")
