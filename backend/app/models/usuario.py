"""
========================================
MODELO: USUARIO
Sistema de Control de Visitantes
========================================
"""

from datetime import datetime
from app.extensions import db
from flask_login import UserMixin
import bcrypt


class Usuario(UserMixin, db.Model):
    """Modelo de Usuario del sistema"""
    
    __tablename__ = 'usuarios'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    tipo_identificacion = db.Column(db.String(50), nullable=False)
    num_identificacion = db.Column(db.String(50), nullable=False, unique=True, index=True)
    primer_nombre = db.Column(db.String(100), nullable=False)
    segundo_nombre = db.Column(db.String(100))
    primer_apellido = db.Column(db.String(100), nullable=False)
    segundo_apellido = db.Column(db.String(100))
    num_telefono = db.Column(db.String(100), nullable=False)
    dir_correo = db.Column(db.String(100), nullable=False, unique=True, index=True)
    
    # Sede asignada (NULL para usuario_master que tienen acceso global)
    sede_id = db.Column(db.Integer, db.ForeignKey('sedes.id'), nullable=True)
    sede = db.relationship('Sede', backref='usuarios')
    
    # Rol y estado
    rol = db.Column(db.String(100), nullable=False)  # usuario_master o usuario_operador
    estado = db.Column(db.String(100), nullable=False, default='ACTIVO')  # ACTIVO, INACTIVO, BLOQUEADO
    
    # Credenciales
    usuario = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Control de intentos de login
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime)
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hashea la contraseña usando bcrypt"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def incrementar_intentos_fallidos(self):
        """Incrementa los intentos fallidos de login"""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 10:
            self.estado = 'BLOQUEADO'
            self.bloqueado_hasta = datetime.utcnow()
    
    def resetear_intentos_fallidos(self):
        """Resetea los intentos fallidos"""
        self.intentos_fallidos = 0
        if self.estado == 'BLOQUEADO':
            self.estado = 'ACTIVO'
        self.bloqueado_hasta = None
    
    def tiene_acceso_sede(self, sede_id):
        """Verifica si el usuario tiene acceso a una sede"""
        if self.rol == 'usuario_master':
            return True  # Master tiene acceso a todas las sedes
        return self.sede_id == sede_id
    
    def to_dict(self):
        """Convierte el usuario a diccionario"""
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
            'sede_id': self.sede_id,
            'sede': self.sede.descripcion_sede if self.sede else 'N/A (Acceso Global)',
            'rol': self.rol,
            'estado': self.estado,
            'usuario': self.usuario,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.usuario} - {self.rol}>'
