"""
========================================
MODELO: AUTORIZACION SST
========================================
"""

from datetime import datetime
from app.extensions import db


class AutorizacionSST(db.Model):
    """Autorizaciones SST para ejecución de labores contratistas"""

    __tablename__ = 'autorizaciones_sst'

    id = db.Column(db.Integer, primary_key=True)
    numero_autorizacion = db.Column(db.String(20), unique=True)  # AC-00000001
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas_contratistas.id'), nullable=False)
    sede_id = db.Column(db.Integer, db.ForeignKey('sedes.id'))
    planilla_ss_id = db.Column(db.Integer, db.ForeignKey('planillas_ss.id'))
    labor = db.Column(db.String(300), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    fecha_autorizacion = db.Column(db.Date)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    pdf_ruta = db.Column(db.String(500))
    observaciones = db.Column(db.String(1000))
    carta_presentacion_ruta = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    aprobado_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa = db.relationship('EmpresaContratista', back_populates='autorizaciones')
    planilla = db.relationship('PlanillaSS', foreign_keys=[planilla_ss_id])
    ingresos = db.relationship('LogIngresoContratista', back_populates='autorizacion_sst')
    empleados_autorizacion = db.relationship('EmpleadoAutorizacion', back_populates='autorizacion', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'numero_autorizacion': self.numero_autorizacion,
            'empresa_id': self.empresa_id,
            'sede_id': self.sede_id,
            'planilla_ss_id': self.planilla_ss_id,
            'labor': self.labor,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'fecha_autorizacion': self.fecha_autorizacion.isoformat() if self.fecha_autorizacion else None,
            'estado': self.estado,
            'pdf_ruta': self.pdf_ruta,
            'observaciones': self.observaciones,
            'carta_presentacion_ruta': self.carta_presentacion_ruta,
            'created_by': self.created_by,
            'aprobado_by': self.aprobado_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<AutorizacionSST {self.id} - {self.estado}>'