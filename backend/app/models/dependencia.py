"""
========================================
MODELO: DEPENDENCIA
========================================
"""

from datetime import datetime
from app.extensions import db


class Dependencia(db.Model):
    """Modelo de Dependencias - Departamentos globales disponibles para todas las sedes"""
    
    __tablename__ = 'dependencias'
    
    id = db.Column(db.Integer, primary_key=True)
    prefijo_dependencia = db.Column(db.String(50), nullable=False, unique=True, index=True)
    descripcion_dependencia = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='ACTIVO')
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, incluir_sedes=True):
        """Convierte la dependencia a diccionario
        
        Args:
            incluir_sedes (bool): Si True, incluye datos de sede relacionada
        
        Returns:
            dict: Datos del modelo en formato JSON
        """
        data = {
            'id': self.id,
            'prefijo_dependencia': self.prefijo_dependencia,
            'descripcion_dependencia': self.descripcion_dependencia,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
        
        # Incluir sede solo si se solicita y existe relación
        if incluir_sedes and hasattr(self, 'sede') and self.sede:
            data['sede'] = {
                'id': self.sede.id,
                'nombre': self.sede.nombre
            }
        
        return data
    
    def __repr__(self):
        return f'<Dependencia {self.prefijo_dependencia} - {self.descripcion_dependencia}>'
