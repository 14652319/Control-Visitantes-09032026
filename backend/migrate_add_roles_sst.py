"""
Migración: Agregar roles admin_sst y operador_seguridad
Fecha: 2026-03-19
Checkpoint: 2.2
Relacionado: Módulo SST para gestión de contratistas
"""
from app.extensions import db
from sqlalchemy import text

def migrate():
    """Agregar nuevos roles a tabla usuarios"""
    print("=" * 60)
    print("MIGRACIÓN: Agregar roles SST a tabla usuarios")
    print("=" * 60)
    
    try:
        # Paso 1: Ampliar tipo de columna rol
        print("\n[1/3] Ampliando tipo de columna 'rol' a VARCHAR(50)...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            ALTER COLUMN rol TYPE VARCHAR(50);
        """))
        print("  ✅ Columna ampliada")
        
        # Paso 2: Eliminar constraint viejo
        print("\n[2/3] Eliminando constraint antiguo...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            DROP CONSTRAINT IF EXISTS check_rol_valido;
        """))
        print("  ✅ Constraint antiguo eliminado")
        
        # Paso 3: Crear constraint nuevo con roles adicionales
        print("\n[3/3] Creando constraint nuevo con 5 roles...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            ADD CONSTRAINT check_rol_valido 
            CHECK (rol IN (
                'usuario_master',
                'usuario_operador',
                'usuario_funcionario',
                'admin_sst',
                'operador_seguridad'
            ));
        """))
        print("  ✅ Constraint nuevo creado")
        
        db.session.commit()
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA: Roles SST agregados exitosamente")
        print("=" * 60)
        print("\nRoles ahora disponibles:")
        print("  1. usuario_master")
        print("  2. usuario_operador")
        print("  3. usuario_funcionario")
        print("  4. admin_sst (NUEVO)")
        print("  5. operador_seguridad (NUEVO)")
        
    except Exception as e:
        print(f"\n❌ ERROR durante migración: {e}")
        print("Ejecutando rollback...")
        db.session.rollback()
        rollback()
        raise

def rollback():
    """Revertir cambios si algo falla"""
    print("\n" + "=" * 60)
    print("ROLLBACK: Revirtiendo migración de roles SST")
    print("=" * 60)
    
    try:
        print("\n[1/2] Eliminando constraint nuevo...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            DROP CONSTRAINT IF EXISTS check_rol_valido;
        """))
        print("  ✅ Constraint eliminado")
        
        print("\n[2/2] Restaurando constraint antiguo (3 roles)...")
        db.session.execute(text("""
            ALTER TABLE usuarios 
            ADD CONSTRAINT check_rol_valido 
            CHECK (rol IN (
                'usuario_master', 
                'usuario_operador', 
                'usuario_funcionario'
            ));
        """))
        print("  ✅ Constraint restaurado")
        
        db.session.commit()
        print("\n✅ ROLLBACK COMPLETADO: Sistema restaurado a 3 roles")
        
    except Exception as e:
        print(f"\n❌ ERROR durante rollback: {e}")
        db.session.rollback()

def verificar():
    """Verificar que migración fue exitosa"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: Comprobando migración")
    print("=" * 60)
    
    result = db.session.execute(text("""
        SELECT conname, pg_get_constraintdef(oid) AS definition
        FROM pg_constraint 
        WHERE conrelid = 'usuarios'::regclass 
        AND conname = 'check_rol_valido';
    """))
    
    row = result.fetchone()
    if row:
        print(f"\nConstraint encontrado: {row[0]}")
        print(f"Definición: {row[1]}")
        
        # Verificar que incluye los 5 roles
        definition = row[1]
        roles_esperados = ['admin_sst', 'operador_seguridad']
        todos_presentes = all(rol in definition for rol in roles_esperados)
        
        if todos_presentes:
            print("\n✅ VERIFICACIÓN EXITOSA: Todos los roles nuevos presentes")
            return True
        else:
            print("\n❌ VERIFICACIÓN FALLIDA: Faltan roles nuevos")
            return False
    else:
        print("\n❌ VERIFICACIÓN FALLIDA: Constraint no encontrado")
        return False

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            migrate()
            verificar()
        except Exception as e:
            print(f"\n❌ Error fatal: {e}")
            exit(1)
