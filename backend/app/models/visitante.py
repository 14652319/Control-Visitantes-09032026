"""
========================================
MODELO: VISITANTE
========================================
"""

from datetime import datetime
from app.extensions import db


class Visitante(db.Model):
    """Modelo de Visitantes registrados en el sistema"""
    
    __tablename__ = 'visitantes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos personales
    tipo_identificacion = db.Column(db.String(50), nullable=False)
    num_identificacion = db.Column(db.String(50), nullable=False, index=True)
    primer_nombre = db.Column(db.String(100), nullable=False)
    segundo_nombre = db.Column(db.String(100))
    primer_apellido = db.Column(db.String(100), nullable=False)
    segundo_apellido = db.Column(db.String(100))
    num_telefono = db.Column(db.String(100), nullable=False)
    dir_correo = db.Column(db.String(100), nullable=False)
    
    # Datos empresariales
    empresa = db.Column(db.String(100), nullable=False)
    nit_empresa = db.Column(db.String(50), nullable=False)
    
    # Estado
    estado = db.Column(db.String(50), nullable=False, default='ACTIVO')
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice compuesto para búsqueda rápida
    __table_args__ = (
        db.Index('idx_visitante_identificacion', 'tipo_identificacion', 'num_identificacion'),
    )
    
    def to_dict(self):
        """Convierte el visitante a diccionario"""
        return {
            'id': self.id,
            'tipo_identificacion': self.tipo_identificacion,
            'num_identificacion': self.num_identificacion,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'nombre_completo': f"{self.primer_nombre} {self.segundo_nombre or ''} {self.primer_apellido} {self.segundo_apellido or ''}".strip(),
            'num_telefono': self.num_telefono,
            'dir_correo': self.dir_correo,
            'empresa': self.empresa,
            'nit_empresa': self.nit_empresa,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def __repr__(self):
        return f'<Visitante {self.num_identificacion} - {self.primer_nombre} {self.primer_apellido}>'
