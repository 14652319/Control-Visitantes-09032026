"""
========================================
MODELO: DEPENDENCIA
========================================
"""

from datetime import datetime
from app.extensions import db


# Tabla intermedia para relación many-to-many entre Sede y Dependencia
sede_dependencia = db.Table(
    'sede_dependencia',
    db.Column('sede_id', db.Integer, db.ForeignKey('sedes.id'), primary_key=True),
    db.Column('dependencia_id', db.Integer, db.ForeignKey('dependencias.id'), primary_key=True),
    db.Column('fecha_asignacion', db.DateTime, default=datetime.utcnow)
)


class Dependencia(db.Model):
    """Modelo de Dependencias - pueden estar asociadas a una o más sedes"""
    
    __tablename__ = 'dependencias'
    
    id = db.Column(db.Integer, primary_key=True)
    prefijo_dependencia = db.Column(db.String(50), nullable=False, unique=True, index=True)
    descripcion_dependencia = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='ACTIVO')
    
    # Relación many-to-many con Sedes
    sedes = db.relationship(
        'Sede',
        secondary=sede_dependencia,
        backref=db.backref('dependencias', lazy='dynamic')
    )
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def tiene_sede(self, sede_id):
        """Verifica si la dependencia está asociada a una sede"""
        return any(sede.id == sede_id for sede in self.sedes)
    
    def to_dict(self, incluir_sedes=False):
        """Convierte la dependencia a diccionario"""
        data = {
            'id': self.id,
            'prefijo_dependencia': self.prefijo_dependencia,
            'descripcion_dependencia': self.descripcion_dependencia,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
        
        if incluir_sedes:
            data['sedes'] = [{'id': sede.id, 'descripcion': sede.descripcion_sede} for sede in self.sedes]
        
        return data
    
    def __repr__(self):
        return f'<Dependencia {self.prefijo_dependencia} - {self.descripcion_dependencia}>'
