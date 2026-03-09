"""
========================================
MODELO: SEDE
========================================
"""

from datetime import datetime
from app.extensions import db


class Sede(db.Model):
    """Modelo de Sedes de la empresa"""
    
    __tablename__ = 'sedes'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_sede = db.Column(db.String(50), nullable=False, unique=True, index=True)
    descripcion_sede = db.Column(db.String(200), nullable=False)
    direccion_sede = db.Column(db.String(300), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='ACTIVO')
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convierte la sede a diccionario"""
        return {
            'id': self.id,
            'codigo_sede': self.codigo_sede,
            'descripcion_sede': self.descripcion_sede,
            'direccion_sede': self.direccion_sede,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def __repr__(self):
        return f'<Sede {self.codigo_sede} - {self.descripcion_sede}>'
