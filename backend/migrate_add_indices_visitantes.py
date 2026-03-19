"""
Migración: Agregar índices para optimización de búsquedas
Fecha: 2026-03-19
Checkpoint: 1.1
"""
from app import create_app
from app.extensions import db

def agregar_indices():
    """Agregar índices faltantes para optimizar búsquedas"""
    print("Iniciando creación de índices...")
    
    indices = [
        # Índice para búsquedas por identificación (visitantes)
        """
        CREATE INDEX IF NOT EXISTS idx_visitante_identificacion 
        ON visitantes(tipo_identificacion, num_identificacion);
        """,
        
        # Índice para búsquedas por fecha (log_visitantes)
        """
        CREATE INDEX IF NOT EXISTS idx_log_visitantes_fecha 
        ON log_visitantes(fecha_ingreso);
        """,
        
        # Índice para búsquedas de autorizaciones por usuario y estado
        """
        CREATE INDEX IF NOT EXISTS idx_autorizacion_usuario_estado 
        ON autorizaciones_ingreso(usuario_id, estado);
        """,
    ]
    
    for i, sql in enumerate(indices, 1):
        print(f"  Creando índice {i}/3...")
        db.session.execute(db.text(sql))
    
    db.session.commit()
    print("✅ 3 índices creados exitosamente")

def rollback():
    """Revertir índices si es necesario"""
    print("Eliminando índices...")
    db.session.execute(db.text("DROP INDEX IF EXISTS idx_visitante_identificacion;"))
    db.session.execute(db.text("DROP INDEX IF EXISTS idx_log_visitantes_fecha;"))
    db.session.execute(db.text("DROP INDEX IF EXISTS idx_autorizacion_usuario_estado;"))
    db.session.commit()
    print("✅ Índices eliminados")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        try:
            agregar_indices()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Ejecutando rollback...")
            rollback()
