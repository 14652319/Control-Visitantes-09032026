"""
========================================
MODELO: PLANILLA SS
========================================
"""

from datetime import datetime
from app.extensions import db


class PlanillaSS(db.Model):
    """Planillas de seguridad social cargadas por empresa y periodo"""

    __tablename__ = 'planillas_ss'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas_contratistas.id'), nullable=False)
    periodo = db.Column(db.String(7), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    vigencia_fin = db.Column(db.Date, nullable=False)
    archivo_nombre = db.Column(db.String(200))
    archivo_ruta = db.Column(db.String(500))
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    verificado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    verificado_at = db.Column(db.DateTime)

    empresa = db.relationship('EmpresaContratista', back_populates='planillas')

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_id': self.empresa_id,
            'periodo': self.periodo,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'vigencia_fin': self.vigencia_fin.isoformat() if self.vigencia_fin else None,
            'archivo_nombre': self.archivo_nombre,
            'archivo_ruta': self.archivo_ruta,
            'estado': self.estado,
            'verificado_por': self.verificado_por,
            'verificado_at': self.verificado_at.isoformat() if self.verificado_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<PlanillaSS {self.empresa_id} - {self.periodo}>'