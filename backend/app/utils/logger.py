"""
========================================
SISTEMA DE LOGGING ESTRUCTURADO
Sistema de Control de Visitantes
========================================
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formateador con colores para consola"""
    
    # Colores ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agregar color al nivel
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(app):
    """
    Configura el sistema de logging para la aplicación
    
    Crea 3 logs:
    - app.log: Log general de la aplicación (INFO+)
    - error.log: Solo errores (ERROR+)
    - debug.log: Todo incluyendo DEBUG (para desarrollo)
    
    Rotación:
    - Tamaño máximo: 10MB
    - Backups: 10 archivos
    """
    
    # Crear carpeta de logs si no existe
    log_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_folder, exist_ok=True)
    
    # Formato de log
    log_format = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar logger principal de Flask
    app.logger.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    
    # Limpiar handlers existentes
    app.logger.handlers = []
    
    # ==========================================
    # 1. HANDLER DE CONSOLA (con colores)
    # ==========================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    
    # ==========================================
    # 2. HANDLER DE ARCHIVO GENERAL (app.log)
    # ==========================================
    app_log_file = os.path.join(log_folder, 'app.log')
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)
    
    # ==========================================
    # 3. HANDLER DE ERRORES (error.log)
    # ==========================================
    error_log_file = os.path.join(log_folder, 'error.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    app.logger.addHandler(error_handler)
    
    # ==========================================
    # 4. HANDLER DE DEBUG (solo en desarrollo)
    # ==========================================
    if app.config['DEBUG']:
        debug_log_file = os.path.join(log_folder, 'debug.log')
        debug_handler = TimedRotatingFileHandler(
            debug_log_file,
            when='midnight',
            interval=1,
            backupCount=7,  # 7 días de historia
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        app.logger.addHandler(debug_handler)
    
    # ==========================================
    # 5. CONFIGURAR LOGGERS DE WERKZEUG/SQLAlchemy
    # ==========================================
    
    # Werkzeug (servidor Flask)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)  # Solo warnings y errores
    werkzeug_logger.handlers = []
    werkzeug_logger.addHandler(file_handler)
    
    # SQLAlchemy (solo errores)
    sqlalchemy_logger = logging.getLogger('sqlalchemy')
    sqlalchemy_logger.setLevel(logging.WARNING)
    sqlalchemy_logger.handlers = []
    sqlalchemy_logger.addHandler(error_handler)
    
    # Log de inicio
    app.logger.info("="*60)
    app.logger.info("Sistema de Control de Visitantes - INICIADO")
    app.logger.info(f"Entorno: {app.config.get('FLASK_ENV', 'development')}")
    app.logger.info(f"Debug: {app.config['DEBUG']}")
    app.logger.info(f"Logs guardados en: {log_folder}")
    app.logger.info("="*60)
    
    return app.logger


def log_request(logger, request, response_status=None):
    """Helper para loguear peticiones HTTP"""
    logger.info(
        f"{request.method} {request.path} - "
        f"IP: {request.remote_addr} - "
        f"Status: {response_status or 'N/A'}"
    )


def log_user_action(logger, user, action, details=None):
    """Helper para loguear acciones de usuario"""
    message = f"Usuario: {user.usuario if hasattr(user, 'usuario') else 'Unknown'} - Acción: {action}"
    if details:
        message += f" - Detalles: {details}"
    logger.info(message)


def log_error(logger, error, context=None):
    """Helper para loguear errores con contexto"""
    message = f"ERROR: {str(error)}"
    if context:
        message += f" - Contexto: {context}"
    logger.error(message, exc_info=True)


# ==========================================
# LOGGER GLOBAL PARA IMPORTAR EN ROUTES
# ==========================================
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
