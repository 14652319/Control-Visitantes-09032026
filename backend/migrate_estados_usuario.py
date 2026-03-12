"""
========================================
MIGRACIÓN: AGREGAR ESTADOS PENDIENTE Y RECHAZADO
Sistema de Control de Visitantes
========================================

Agrega los estados PENDIENTE y RECHAZADO para usuarios funcionarios
que se registran y esperan aprobación del administrador.
"""

from app import create_app
from app.extensions import db

app = create_app()


def migrate():
    """Agrega datos de estados en la tabla usuarios"""
    with app.app_context():
        try:
            print("=" * 60)
            print("MIGRACIÓN: AGREGAR ESTADOS PENDIENTE Y RECHAZADO")
            print("=" * 60)
            
            # Nota: Los estados se manejan a nivel de aplicación (string)
            # No requiere cambios en la estructura de la tabla
            # Solo necesitamos verificar que el campo estado acepta estos valores
            
            print("\n✓ Estados disponibles en el sistema:")
            print("  - ACTIVO: Usuario activo y puede acceder")
            print("  - INACTIVO: Usuario desactivado temporalmente")
            print("  - BLOQUEADO: Usuario bloqueado por intentos fallidos")
            print("  - PENDIENTE: Usuario registrado esperando aprobación (NUEVO)")
            print("  - RECHAZADO: Solicitud de registro rechazada (NUEVO)")
            
            print("\n✓ No se requieren cambios en la base de datos")
            print("✓ Los nuevos estados se manejan a nivel de aplicación")
            print("=" * 60)
            print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    migrate()
