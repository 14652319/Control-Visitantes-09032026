"""
========================================
CONFIGURACIÓN DE LA APLICACIÓN
Sistema de Control de Visitantes
Supertiendas Cañaveral SAS
========================================
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base de la aplicación"""
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import warnings
        warnings.warn('SECRET_KEY no configurada — usando valor inseguro para desarrollo local', stacklevel=2)
        SECRET_KEY = 'dev-only-insecure-key-do-not-use-in-production'
    
    # Base de Datos (OBLIGATORIO vía .env)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        import warnings
        warnings.warn('DATABASE_URL no configurada — usando localhost por defecto', stacklevel=2)
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/control_visitantes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=45)
    
    # Sesiones
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 45))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_TIMEOUT)
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Seguridad
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 10))
    PASSWORD_MIN_LENGTH = 8
    
    # Archivos
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '../uploads/visitantes')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 5 * 1024 * 1024))  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # PDF Storage
    PDF_STORAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'autorizaciones_sst')
    
    # Retención de fotografías
    DIAS_RETENCION_FOTOS = int(os.getenv('DIAS_RETENCION_FOTOS', 90))
    BORRADO_AUTOMATICO_FOTOS = os.getenv('BORRADO_AUTOMATICO_FOTOS', 'false').lower() == 'true'
    
    # CORS — restringido por defecto, configurar en .env para producción
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000').split(',')
    
    # Timezone
    TIMEZONE = 'America/Bogota'
    
    # Configuración de Correo (Gmail)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Validar que secretos estén configurados en producción
    @classmethod
    def init_app(cls, app):
        required = ['SECRET_KEY', 'DATABASE_URL', 'MAIL_PASSWORD']
        missing = [k for k in required if not os.environ.get(k)]
        if missing:
            raise RuntimeError(f'Variables de entorno requeridas no configuradas: {", ".join(missing)}')


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_TEST', 'sqlite:///:memory:')
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
