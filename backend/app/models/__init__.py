"""
========================================
INICIALIZACIÓN DE MODELOS
========================================
"""

from app.models.usuario import Usuario
from app.models.sede import Sede
from app.models.dependencia import Dependencia
from app.models.visitante import Visitante
from app.models.log_visitante import LogVisitante
from app.models.log_evento import LogEvento
from app.models.autorizacion_ingreso import AutorizacionIngreso

__all__ = [
    'Usuario',
    'Sede',
    'Dependencia',
    'Visitante',
    'LogVisitante',
    'LogEvento',
    'AutorizacionIngreso'
]
