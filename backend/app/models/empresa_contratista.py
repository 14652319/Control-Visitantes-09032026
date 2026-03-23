"""
========================================
MODELO: EMPRESA CONTRATISTA
========================================
"""

from datetime import datetime
from app.extensions import db


class EmpresaContratista(db.Model):
    """Empresas o personas naturales registradas como contratistas"""

    __tablename__ = 'empresas_contratistas'

    id = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(200), nullable=False)
    nit = db.Column(db.String(20), nullable=False, unique=True)
    digito_verificacion = db.Column(db.String(1))
    representante_legal = db.Column(db.String(150))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(100))
    estado = db.Column(db.String(20), nullable=False, default='activa')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo_persona = db.Column(db.String(10), nullable=False, default='JURIDICA')
    tipo_identificacion = db.Column(db.String(5))
    num_identificacion = db.Column(db.String(20))
    primer_nombre = db.Column(db.String(100))
    segundo_nombre = db.Column(db.String(100))
    primer_apellido = db.Column(db.String(100))
    segundo_apellido = db.Column(db.String(100))
    tipo_tercero = db.Column(db.String(30), nullable=False, default='CONTRATISTA')
    # Valores: CONTRATISTA | EMPLEADO_CONTRATISTA | MERCADERISTA | VISITANTE_REGISTRO
    nit_empresa = db.Column(db.String(20))   # campo legacy — usar empleador_id
    observacion = db.Column(db.Text)         # Motivo de inactivación u otras observaciones
    empleador_id = db.Column(db.Integer, db.ForeignKey('empresas_contratistas.id'), nullable=True)  # FK al contratista empleador

    empleados = db.relationship('EmpleadoContratista', back_populates='empresa')
    planillas = db.relationship('PlanillaSS', back_populates='empresa')
    autorizaciones = db.relationship('AutorizacionSST', back_populates='empresa')

    @property
    def nombre_completo_persona_natural(self):
        partes = [
            self.primer_nombre,
            self.segundo_nombre,
            self.primer_apellido,
            self.segundo_apellido,
        ]
        return ' '.join(parte for parte in partes if parte)

    def _get_empleador_dict(self):
        """Retorna datos básicos del empleador sin llamar to_dict() para evitar recursion."""
        if not self.empleador_id:
            return None
        try:
            emp = db.session.get(EmpresaContratista, self.empleador_id)
            if not emp:
                return None
            return {
                'id': emp.id,
                'nit': emp.nit,
                'tipo_persona': emp.tipo_persona,
                'tipo_identificacion': emp.tipo_identificacion,
                'num_identificacion': emp.num_identificacion,
                'razon_social': emp.razon_social,
                'nombre_completo_persona_natural': emp.nombre_completo_persona_natural,
            }
        except Exception:
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'razon_social': self.razon_social,
            'nit': self.nit,
            'digito_verificacion': self.digito_verificacion,
            'representante_legal': self.representante_legal,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'estado': self.estado,
            'tipo_persona': self.tipo_persona,
            'tipo_identificacion': self.tipo_identificacion,
            'num_identificacion': self.num_identificacion,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'tipo_tercero': self.tipo_tercero or 'CONTRATISTA',
            'nit_empresa': self.nit_empresa,
            'observacion': self.observacion,
            'empleador_id': self.empleador_id,
            'empleador': self._get_empleador_dict(),
            'nombre_completo_persona_natural': self.nombre_completo_persona_natural,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<EmpresaContratista {self.id} - {self.razon_social}>'