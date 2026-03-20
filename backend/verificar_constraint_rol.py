#!/usr/bin/env python3
"""
Verificar constraint de rol en tabla usuarios
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    result = db.session.execute(text("""
        SELECT constraint_name, check_clause 
        FROM information_schema.check_constraints
        WHERE constraint_schema = 'public'
        AND constraint_name LIKE '%rol%'
    """)).fetchall()
    
    if result:
        print("CHECK constraints encontrados:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
    else:
        print("✅ No hay CHECK constraint en columna rol — cualquier valor es aceptado")
