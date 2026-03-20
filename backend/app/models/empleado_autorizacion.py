"""
========================================
MODELO: EMPLEADO POR AUTORIZACIÓN SST
========================================
Relaciona empleados específicos con una autorización SST.
Almacena los permisos de trabajo especial por empleado y las rutas
de los documentos soporte subidos (altura, espacios confinados, etc.)
"""

from datetime import datetime
from app.extensions import db


class EmpleadoAutorizacion(db.Model):
    """Tabla M2M con datos extra: empleados asignados a una autorización SST"""

    __tablename__ = 'empleados_por_autorizacion'

    id                          = db.Column(db.Integer, primary_key=True)
    autorizacion_id             = db.Column(db.Integer, db.ForeignKey('autorizaciones_sst.id'), nullable=False)
    empleado_id                 = db.Column(db.Integer, db.ForeignKey('empleados_contratistas.id'), nullable=False)

    # ── Tipos de trabajo autorizado ────────────────────────────────────────────
    trabajo_altura              = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_energias_peligrosas = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_espacios_confinados = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_caliente            = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_izaje_cargas        = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_excavacion          = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_sustancias_quimicas = db.Column(db.Boolean, nullable=False, default=False)
    trabajo_otro                = db.Column(db.String(100))   # descripción libre si aplica

    # ── Documentos soporte subidos (JSON: [{tipo, nombre, ruta}, ...]) ─────────
    # Ejemplo:  [{"tipo": "trabajo_altura", "nombre": "AC-0000001_900123_12345_001.pdf", "ruta": "Documentos_SST/AC-0000001/...pdf"}]
    documentos_json             = db.Column(db.Text)          # almacenado como JSON string

    created_at                  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # ── Relaciones ─────────────────────────────────────────────────────────────
    autorizacion = db.relationship('AutorizacionSST', back_populates='empleados_autorizacion')
    empleado     = db.relationship('EmpleadoContratista', back_populates='autorizaciones_sst')

    def get_documentos(self):
        """Devuelve la lista de documentos parseada desde JSON"""
        import json
        if self.documentos_json:
            try:
                return json.loads(self.documentos_json)
            except Exception:
                return []
        return []

    def set_documentos(self, lista):
        """Serializa la lista de documentos a JSON"""
        import json
        self.documentos_json = json.dumps(lista, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'autorizacion_id': self.autorizacion_id,
            'empleado_id': self.empleado_id,
            'trabajo_altura': self.trabajo_altura,
            'trabajo_energias_peligrosas': self.trabajo_energias_peligrosas,
            'trabajo_espacios_confinados': self.trabajo_espacios_confinados,
            'trabajo_caliente': self.trabajo_caliente,
            'trabajo_izaje_cargas': self.trabajo_izaje_cargas,
            'trabajo_excavacion': self.trabajo_excavacion,
            'trabajo_sustancias_quimicas': self.trabajo_sustancias_quimicas,
            'trabajo_otro': self.trabajo_otro,
            'documentos': self.get_documentos(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<EmpleadoAutorizacion aut={self.autorizacion_id} emp={self.empleado_id}>'
