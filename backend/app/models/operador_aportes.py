"""
========================================
MODELO: OPERADOR APORTES (EPS / AFP / ARL)
========================================
Módulo SST — CHECKPOINT 3.1.5
"""

from datetime import datetime
from app.extensions import db


class OperadorAportes(db.Model):
    """Entidades de seguridad social: EPS, AFP y ARL registradas en Colombia"""

    __tablename__ = 'operadores_aportes'

    id         = db.Column(db.Integer,     primary_key=True)
    nombre     = db.Column(db.String(100), nullable=False)
    tipo       = db.Column(db.String(10),  nullable=False)   # 'EPS' | 'AFP' | 'ARL'
    nit        = db.Column(db.String(20),  nullable=False)
    activo     = db.Column(db.Boolean,     nullable=False, default=True)
    created_at = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    empleados_eps = db.relationship(
        'EmpleadoContratista',
        foreign_keys='EmpleadoContratista.eps_id',
        back_populates='eps'
    )
    empleados_afp = db.relationship(
        'EmpleadoContratista',
        foreign_keys='EmpleadoContratista.afp_id',
        back_populates='afp'
    )
    empleados_arl = db.relationship(
        'EmpleadoContratista',
        foreign_keys='EmpleadoContratista.arl_id',
        back_populates='arl'
    )

    # Restricciones a nivel DB se definen en migración (check_tipo_operador, unique_nit_tipo)

    def to_dict(self):
        return {
            'id':         self.id,
            'nombre':     self.nombre,
            'tipo':       self.tipo,
            'nit':        self.nit,
            'activo':     self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<OperadorAportes {self.tipo} - {self.nombre}>'
