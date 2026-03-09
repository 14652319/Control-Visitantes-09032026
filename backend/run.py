"""
========================================
PUNTO DE ENTRADA DE LA APLICACIÓN
Sistema de Control de Visitantes
Supertiendas Cañaveral SAS
========================================
"""

import os
from app import create_app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Configurar el puerto y host
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print("="*60)
    print("SISTEMA DE CONTROL DE VISITANTES")
    print("Supertiendas Cañaveral SAS")
    print("="*60)
    print(f"🚀 Servidor corriendo en http://{host}:{port}")
    print(f"🌐 Abre tu navegador en: http://localhost:{port}")
    print(f"🔧 Modo debug: {debug}")
    print("="*60)
    
    # Iniciar servidor
    app.run(
        host=host,
        port=port,
        debug=debug
    )
