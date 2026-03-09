"""
========================================
INICIALIZACIÓN DE RUTAS
========================================
"""

from app.routes import auth
from app.routes import usuarios
from app.routes import sedes
from app.routes import dependencias
from app.routes import visitantes
from app.routes import reportes
from app.routes import autorizaciones
from app.routes import configuracion

__all__ = [
    'auth',
    'usuarios',
    'sedes',
    'dependencias',
    'visitantes',
    'reportes',
    'autorizaciones',
    'configuracion'
]
