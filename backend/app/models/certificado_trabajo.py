"""
========================================
MODELO: CERTIFICADO TRABAJO
========================================
"""

from datetime import datetime
from app.extensions import db


class CertificadoTrabajo(db.Model):
    """Certificados requeridos para el trabajo del contratista"""

    __tablename__ = 'certificados_trabajo'

    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados_contratistas.id'), nullable=False)
    tipo_certificado = db.Column(db.String(50), nullable=False)
    nombre_certificado = db.Column(db.String(200), nullable=False)
    fecha_expedicion = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    archivo_nombre = db.Column(db.String(200))
    archivo_ruta = db.Column(db.String(500))
    verificado = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    empleado = db.relationship('EmpleadoContratista', back_populates='certificados')

    def to_dict(self):
        return {
            'id': self.id,
            'empleado_id': self.empleado_id,
            'tipo_certificado': self.tipo_certificado,
            'nombre_certificado': self.nombre_certificado,
            'fecha_expedicion': self.fecha_expedicion.isoformat() if self.fecha_expedicion else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'archivo_nombre': self.archivo_nombre,
            'archivo_ruta': self.archivo_ruta,
            'verificado': self.verificado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<CertificadoTrabajo {self.tipo_certificado} - {self.nombre_certificado}>'