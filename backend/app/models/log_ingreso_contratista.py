"""
========================================
MODELO: LOG INGRESO CONTRATISTA
========================================
"""

from datetime import datetime
from app.extensions import db


class LogIngresoContratista(db.Model):
    """Registro de ingresos y salidas de contratistas"""

    __tablename__ = 'log_ingresos_contratistas'

    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados_contratistas.id'), nullable=False)
    autorizacion_sst_id = db.Column(db.Integer, db.ForeignKey('autorizaciones_sst.id'), nullable=False)
    sede_id = db.Column(db.Integer, db.ForeignKey('sedes.id'))
    tipo_evento = db.Column(db.String(10), nullable=False)
    timestamp_evento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    registrado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    observaciones = db.Column(db.String(500))

    empleado = db.relationship('EmpleadoContratista', back_populates='ingresos')
    autorizacion_sst = db.relationship('AutorizacionSST', back_populates='ingresos')

    def to_dict(self):
        return {
            'id': self.id,
            'empleado_id': self.empleado_id,
            'autorizacion_sst_id': self.autorizacion_sst_id,
            'sede_id': self.sede_id,
            'tipo_evento': self.tipo_evento,
            'timestamp_evento': self.timestamp_evento.isoformat() if self.timestamp_evento else None,
            'registrado_por': self.registrado_por,
            'observaciones': self.observaciones,
        }

    def __repr__(self):
        return f'<LogIngresoContratista {self.id} - {self.tipo_evento}>'