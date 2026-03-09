"""
========================================
MODELO: CONFIGURACION_SISTEMA
Configuración global del sistema
========================================
"""

from datetime import datetime
from app.extensions import db


class ConfiguracionSistema(db.Model):
    """Modelo de Configuración del Sistema"""
    
    __tablename__ = 'configuracion_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), nullable=False, unique=True, index=True)
    valor = db.Column(db.String(500), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_dato = db.Column(db.String(50), nullable=False, default='string')  # string, int, bool, float
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def obtener_valor(cls, clave, valor_defecto=None):
        """Obtiene un valor de configuración"""
        config = cls.query.filter_by(clave=clave).first()
        if not config:
            return valor_defecto
        
        # Convertir según el tipo
        if config.tipo_dato == 'int':
            return int(config.valor)
        elif config.tipo_dato == 'float':
            return float(config.valor)
        elif config.tipo_dato == 'bool':
            return config.valor.lower() in ('true', '1', 'yes', 'si')
        else:
            return config.valor
    
    @classmethod
    def establecer_valor(cls, clave, valor, descripcion=None, tipo_dato='string'):
        """Establece o actualiza un valor de configuración"""
        config = cls.query.filter_by(clave=clave).first()
        if config:
            config.valor = str(valor)
            config.fecha_modificacion = datetime.utcnow()
            if descripcion:
                config.descripcion = descripcion
        else:
            config = cls(
                clave=clave,
                valor=str(valor),
                descripcion=descripcion,
                tipo_dato=tipo_dato
            )
            db.session.add(config)
        return config
    
    def to_dict(self):
        """Convierte la configuración a diccionario"""
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion,
            'tipo_dato': self.tipo_dato,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }
    
    def __repr__(self):
        return f'<ConfiguracionSistema {self.clave}={self.valor}>'
