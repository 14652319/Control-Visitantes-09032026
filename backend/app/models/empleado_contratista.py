"""
========================================
MODELO: EMPLEADO CONTRATISTA
========================================
"""

from datetime import datetime
from app.extensions import db


class EmpleadoContratista(db.Model):
    """Empleados asociados a una empresa contratista"""

    __tablename__ = 'empleados_contratistas'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas_contratistas.id'), nullable=False)
    tipo_id = db.Column(db.String(5), nullable=False)
    num_id = db.Column(db.String(20), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))
    eps_id = db.Column(db.Integer, db.ForeignKey('operadores_aportes.id'))
    afp_id = db.Column(db.Integer, db.ForeignKey('operadores_aportes.id'))
    arl_id = db.Column(db.Integer, db.ForeignKey('operadores_aportes.id'))
    estado = db.Column(db.String(20), nullable=False, default='activo')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa = db.relationship('EmpresaContratista', back_populates='empleados')
    eps = db.relationship('OperadorAportes', foreign_keys=[eps_id], back_populates='empleados_eps')
    afp = db.relationship('OperadorAportes', foreign_keys=[afp_id], back_populates='empleados_afp')
    arl = db.relationship('OperadorAportes', foreign_keys=[arl_id], back_populates='empleados_arl')
    certificados = db.relationship('CertificadoTrabajo', back_populates='empleado')
    ingresos = db.relationship('LogIngresoContratista', back_populates='empleado')
    autorizaciones_sst = db.relationship('EmpleadoAutorizacion', back_populates='empleado')

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_id': self.empresa_id,
            'tipo_id': self.tipo_id,
            'num_id': self.num_id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'cargo': self.cargo,
            'eps_id': self.eps_id,
            'afp_id': self.afp_id,
            'arl_id': self.arl_id,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<EmpleadoContratista {self.tipo_id}-{self.num_id}>'