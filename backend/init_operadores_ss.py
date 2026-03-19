"""
Seeder: Operadores de Seguridad Social (EPS, AFP, ARL)
Fecha: 2026-03-19
Checkpoint: 2.3
IMPORTANTE: Este script se ejecutará en FASE 3.1.3 cuando exista la tabla operadores_aportes
"""
from app.extensions import db
from app.models.operador_aportes import OperadorAportes

# Lista de 13 operadores de seguridad social en Colombia
# Datos validados para 2026
OPERADORES = [
    # ==========================================
    # EPS - Entidades Promotoras de Salud (5)
    # ==========================================
    {'nombre': 'NUEVA EPS', 'tipo': 'EPS', 'nit': '900156264', 'activo': True},
    {'nombre': 'COMPENSAR EPS', 'tipo': 'EPS', 'nit': '860066942', 'activo': True},
    {'nombre': 'SANITAS EPS', 'tipo': 'EPS', 'nit': '800251440', 'activo': True},
    {'nombre': 'SALUD TOTAL EPS', 'tipo': 'EPS', 'nit': '800130907', 'activo': True},
    {'nombre': 'SURA EPS', 'tipo': 'EPS', 'nit': '800088702', 'activo': True},
    
    # ==========================================
    # AFP - Administradoras de Fondos de Pensiones (4)
    # ==========================================
    {'nombre': 'PORVENIR', 'tipo': 'AFP', 'nit': '800144331', 'activo': True},
    {'nombre': 'PROTECCION', 'tipo': 'AFP', 'nit': '900280884', 'activo': True},
    {'nombre': 'COLFONDOS', 'tipo': 'AFP', 'nit': '800200517', 'activo': True},
    {'nombre': 'OLD MUTUAL', 'tipo': 'AFP', 'nit': '860051894', 'activo': True},
    
    # ==========================================
    # ARL - Administradoras de Riesgos Laborales (4)
    # ==========================================
    {'nombre': 'ARL SURA', 'tipo': 'ARL', 'nit': '800088702', 'activo': True},
    {'nombre': 'POSITIVA', 'tipo': 'ARL', 'nit': '800140949', 'activo': True},
    {'nombre': 'LIBERTY', 'tipo': 'ARL', 'nit': '860024118', 'activo': True},
    {'nombre': 'BOLIVAR', 'tipo': 'ARL', 'nit': '860002400', 'activo': True},
]

def seed():
    """Insertar operadores en base de datos"""
    print("=" * 70)
    print("SEEDER: Operadores de Seguridad Social")
    print("=" * 70)
    print(f"\n📦 Total operadores a insertar: {len(OPERADORES)}")
    print(f"   - EPS: 5")
    print(f"   - AFP: 4")
    print(f"   - ARL: 4")
    print("\n🔄 Insertando operadores...\n")
    
    contador = {'insertados': 0, 'existentes': 0}
    
    for data in OPERADORES:
        # Verificar si ya existe (por NIT y tipo)
        existe = OperadorAportes.query.filter_by(
            nit=data['nit'], 
            tipo=data['tipo']
        ).first()
        
        if not existe:
            # Crear nuevo operador
            operador = OperadorAportes(**data)
            db.session.add(operador)
            print(f"  ✅ {data['tipo']:<4} | {data['nombre']:<25} | NIT: {data['nit']}")
            contador['insertados'] += 1
        else:
            print(f"  ⏭️  {data['tipo']:<4} | {data['nombre']:<25} | Ya existe")
            contador['existentes'] += 1
    
    # Commit de todos los cambios
    db.session.commit()
    
    print("\n" + "=" * 70)
    print("✅ SEEDER COMPLETADO")
    print("=" * 70)
    print(f"\n📊 Resumen:")
    print(f"   - Insertados: {contador['insertados']}")
    print(f"   - Ya existían: {contador['existentes']}")
    print(f"   - Total procesados: {len(OPERADORES)}\n")

def rollback():
    """Eliminar todos los operadores insertados (usar solo en desarrollo)"""
    print("=" * 70)
    print("ROLLBACK: Eliminando operadores de seguridad social")
    print("=" * 70)
    
    for data in OPERADORES:
        operador = OperadorAportes.query.filter_by(
            nit=data['nit'],
            tipo=data['tipo']
        ).first()
        
        if operador:
            db.session.delete(operador)
            print(f"  🗑️  Eliminado: {data['nombre']}")
    
    db.session.commit()
    print("\n✅ ROLLBACK COMPLETADO: Operadores eliminados\n")

def verificar():
    """Verificar que todos los operadores fueron insertados"""
    print("=" * 70)
    print("VERIFICACIÓN: Operadores en base de datos")
    print("=" * 70)
    
    total_db = OperadorAportes.query.count()
    print(f"\n📊 Total operadores en DB: {total_db}")
    
    # Contar por tipo
    eps = OperadorAportes.query.filter_by(tipo='EPS').count()
    afp = OperadorAportes.query.filter_by(tipo='AFP').count()
    arl = OperadorAportes.query.filter_by(tipo='ARL').count()
    
    print(f"   - EPS: {eps} (esperados: 5)")
    print(f"   - AFP: {afp} (esperados: 4)")
    print(f"   - ARL: {arl} (esperados: 4)")
    
    # Validar
    if eps == 5 and afp == 4 and arl == 4:
        print("\n✅ VERIFICACIÓN EXITOSA: Todos los operadores presentes\n")
        return True
    else:
        print("\n❌ VERIFICACIÓN FALLIDA: Faltan operadores\n")
        return False

if __name__ == "__main__":
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            print("\n⚠️  NOTA: Este seeder requiere que exista la tabla 'operadores_aportes'")
            print("Se ejecutará en FASE 3.1.3 del módulo SST\n")
            
            # Descomentar la siguiente línea para ejecutar cuando la tabla exista:
            # seed()
            # verificar()
            
            print("✅ Script preparado. Listo para ejecutar en FASE 3.1.3\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            exit(1)
