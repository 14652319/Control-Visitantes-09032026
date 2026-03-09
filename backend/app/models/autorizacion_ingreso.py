"""
========================================
MODELO: AUTORIZACION_INGRESO
Autorizaciones previas de ingreso creadas por funcionarios
========================================
"""

from datetime import datetime, timedelta
from app.extensions import db


class AutorizacionIngreso(db.Model):
    """Modelo de Autorizaciones Previas de Ingreso"""
    
    __tablename__ = 'autorizaciones_ingreso'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos del visitante autorizado
    tipo_identificacion = db.Column(db.String(50), nullable=False, index=True)
    num_identificacion = db.Column(db.String(50), nullable=False, index=True)
    primer_nombre = db.Column(db.String(100), nullable=False)
    segundo_nombre = db.Column(db.String(100))
    primer_apellido = db.Column(db.String(100), nullable=False)
    segundo_apellido = db.Column(db.String(100))
    num_telefono = db.Column(db.String(100), nullable=True)  # Opcional
    dir_correo = db.Column(db.String(100), nullable=True)  # Opcional
    
    # Datos empresariales
    empresa = db.Column(db.String(100), nullable=False)
    nit_empresa = db.Column(db.String(50), nullable=False)
    
    # Destino en la empresa
    prefijo_dependencia = db.Column(db.String(50), nullable=False)
    descripcion_dependencia = db.Column(db.String(200), nullable=False)
    funcionario_autoriza = db.Column(db.String(200), nullable=False)  # Quién recibirá
    observaciones = db.Column(db.Text)
    
    # Estado de la autorización
    estado = db.Column(db.String(50), nullable=False, default='PENDIENTE', index=True)
    # Estados: PENDIENTE, UTILIZADA, VENCIDA, CANCELADA
    
    # Vigencia
    fecha_vencimiento = db.Column(db.Date, nullable=False, index=True)
    
    # Relaciones
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_creador = db.relationship('Usuario', backref='autorizaciones_creadas')
    
    sede_id = db.Column(db.Integer, db.ForeignKey('sedes.id'), nullable=False)
    sede = db.relationship('Sede', backref='autorizaciones')
    
    # Seguimiento de uso
    fecha_utilizacion = db.Column(db.DateTime)
    utilizada_en_log_id = db.Column(db.Integer, db.ForeignKey('log_visitantes.id'))
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """Constructor que establece fecha_vencimiento automáticamente"""
        super(AutorizacionIngreso, self).__init__(**kwargs)
        if not self.fecha_vencimiento:
            # Importar aquí para evitar import circular
            from app.models.configuracion_sistema import ConfiguracionSistema
            
            # Obtener días de vigencia desde configuración (por defecto 1 día = 24 horas)
            dias_vigencia = int(ConfiguracionSistema.obtener_valor('dias_vigencia_autorizacion', 1))
            fecha_calculo = datetime.now().date() + timedelta(days=dias_vigencia)
            self.fecha_vencimiento = fecha_calculo
    
    def marcar_como_utilizada(self, log_visitante_id):
        """Marca la autorización como utilizada"""
        self.estado = 'UTILIZADA'
        self.fecha_utilizacion = datetime.utcnow()
        self.utilizada_en_log_id = log_visitante_id
    
    def cancelar(self):
        """Cancela la autorización"""
        if self.estado == 'PENDIENTE':
            self.estado = 'CANCELADA'
            return True
        return False
    
    def verificar_vencimiento(self):
        """Verifica si la autorización está vencida"""
        if self.estado == 'PENDIENTE':
            hoy = datetime.now().date()
            fecha_venc = self.fecha_vencimiento if isinstance(self.fecha_vencimiento, type(hoy)) else self.fecha_vencimiento.date() if hasattr(self.fecha_vencimiento, 'date') else self.fecha_vencimiento
            if hoy > fecha_venc:
                self.estado = 'VENCIDA'
                return True
        return False
    
    @property
    def esta_activa(self):
        """Verifica si la autorización está activa (pendiente y no vencida)"""
        if self.estado != 'PENDIENTE':
            return False
        try:
            hoy = datetime.now().date()
            fecha_venc = self.fecha_vencimiento if isinstance(self.fecha_vencimiento, type(hoy)) else self.fecha_vencimiento.date() if hasattr(self.fecha_vencimiento, 'date') else self.fecha_vencimiento
            if hoy > fecha_venc:
                self.verificar_vencimiento()
                return False
        except:
            pass
        return True
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes de validez"""
        if self.estado != 'PENDIENTE':
            return 0
        try:
            hoy = datetime.now().date()
            fecha_venc = self.fecha_vencimiento if isinstance(self.fecha_vencimiento, type(hoy)) else self.fecha_vencimiento.date() if hasattr(self.fecha_vencimiento, 'date') else self.fecha_vencimiento
            delta = fecha_venc - hoy
            return max(0, delta.days)
        except:
            return 0
    
    def to_dict(self, incluir_usuario=False):
        """Convierte la autorización a diccionario"""
        data = {
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
            'prefijo_dependencia': self.prefijo_dependencia,
            'descripcion_dependencia': self.descripcion_dependencia,
            'funcionario_autoriza': self.funcionario_autoriza,
            'observaciones': self.observaciones,
            'estado': self.estado,
            'esta_activa': self.esta_activa,
            'dias_restantes': self.dias_restantes,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_utilizacion': self.fecha_utilizacion.isoformat() if self.fecha_utilizacion else None,
            'utilizada_en_log_id': self.utilizada_en_log_id,
            'sede_id': self.sede_id
        }
        
        if incluir_usuario and self.usuario_creador:
            data['usuario_creador'] = {
                'id': self.usuario_creador.id,
                'usuario': self.usuario_creador.usuario,
                'nombre_completo': f"{self.usuario_creador.primer_nombre} {self.usuario_creador.primer_apellido}"
            }
        
        return data
    
    def __repr__(self):
        return f'<AutorizacionIngreso {self.num_identificacion} - {self.estado}>'
