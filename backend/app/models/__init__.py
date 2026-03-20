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

# Módulo SST
from app.models.operador_aportes import OperadorAportes
from app.models.empresa_contratista import EmpresaContratista
from app.models.empleado_contratista import EmpleadoContratista
from app.models.certificado_trabajo import CertificadoTrabajo
from app.models.planilla_ss import PlanillaSS
from app.models.autorizacion_sst import AutorizacionSST
from app.models.empleado_autorizacion import EmpleadoAutorizacion
from app.models.log_ingreso_contratista import LogIngresoContratista

__all__ = [
    'Usuario',
    'Sede',
    'Dependencia',
    'Visitante',
    'LogVisitante',
    'LogEvento',
    'AutorizacionIngreso',
    # SST
    'OperadorAportes',
    'EmpresaContratista',
    'EmpleadoContratista',
    'CertificadoTrabajo',
    'PlanillaSS',
    'AutorizacionSST',
    'EmpleadoAutorizacion',
    'LogIngresoContratista',
]
