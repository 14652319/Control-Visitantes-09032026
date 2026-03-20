"""
========================================
APLICACIÓN PRINCIPAL FLASK
Sistema de Control de Visitantes
========================================
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import config
import os

# Importar Sentry solo si está disponible
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Configurar Flask con carpeta estática del frontend
    frontend_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'frontend')
    app = Flask(__name__, 
                static_folder=frontend_folder,
                static_url_path='')
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    from app.extensions import init_extensions
    init_extensions(app)
    
    # Configurar sistema de logging
    from app.utils.logger import setup_logger
    logger = setup_logger(app)
    
    # Configurar Sentry para monitoreo de errores (Producción)
    if SENTRY_AVAILABLE and app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=app.config.get('FLASK_ENV', 'development'),
            release=f"control-visitantes@1.0.0"
        )
        logger.info("✅ Sentry inicializado correctamente para monitoreo de errores")
    elif not SENTRY_AVAILABLE:
        logger.info("ℹ️  Sentry no está instalado (pip install sentry-sdk[flask])")
    else:
        logger.info("ℹ️  Sentry no configurado (SENTRY_DSN no encontrado en .env)")
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Registrar blueprints PRIMERO (mayor prioridad)
    from app.routes import auth, usuarios, sedes, dependencias, visitantes, reportes, autorizaciones, configuracion
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(sedes.bp)
    app.register_blueprint(dependencias.bp)
    app.register_blueprint(visitantes.bp)
    app.register_blueprint(reportes.bp)
    app.register_blueprint(autorizaciones.bp)
    app.register_blueprint(configuracion.bp)
    
    # Ruta de health check
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    # Servir index.html en la raíz
    @app.route('/')
    def index():
        """Servir el index.html del frontend"""
        return send_from_directory(frontend_folder, 'index.html')
    
    # Servir archivos HTML del frontend directamente
    @app.route('/<page>.html')
    def serve_html(page):
        """Servir archivos HTML"""
        return send_from_directory(frontend_folder, f'{page}.html')
    
    # Manejador de errores
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Error interno del servidor'}, 500
    
    return app


# Para desarrollo
if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )
