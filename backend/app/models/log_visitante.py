"""
========================================
MODELO: LOG VISITANTES
Registra todas las entradas y salidas de visitantes
========================================
"""

from datetime import datetime
from app.extensions import db


class LogVisitante(db.Model):
    """Modelo de registro de entradas/salidas de visitantes"""
    
    __tablename__ = 'log_visitantes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Fechas y horas
    fecha_ingreso = db.Column(db.Date, nullable=False, index=True)
    hora_ingreso = db.Column(db.Time, nullable=False)
    fecha_salida = db.Column(db.Date)
    hora_salida = db.Column(db.Time)
    
    # Datos del visitante (desnormalizados para histórico)
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
    
    # Destino en la empresa
    prefijo_dependencia = db.Column(db.String(50), nullable=False)
    descripcion_dependencia = db.Column(db.String(200), nullable=False)
    funcionario_recibe = db.Column(db.String(200), nullable=False)
    funcionario_autoriza = db.Column(db.String(200), nullable=False)  # Quién autoriza el ingreso
    observaciones1 = db.Column(db.Text)
    
    # Autorización previa (si se utilizó una)
    autorizacion_previa_id = db.Column(db.Integer, db.ForeignKey('autorizaciones_ingreso.id'))
    
    # Elementos ingresados (checkboxes antiguos - mantener por compatibilidad)
    check1_elemento_tecnologico = db.Column(db.Boolean, default=False)
    check1_descripcion = db.Column(db.String(500))
    
    check2_arma_fuego = db.Column(db.Boolean, default=False)
    check2_descripcion = db.Column(db.String(500))
    
    check3_otro_elemento = db.Column(db.Boolean, default=False)
    check3_descripcion = db.Column(db.String(500))
    
    check4_herramienta = db.Column(db.Boolean, default=False)
    check4_descripcion = db.Column(db.String(500))
    
    check5_adicional = db.Column(db.Boolean, default=False)
    check5_descripcion = db.Column(db.String(500))
    
    # Nuevos campos para elementos que ingresa (estructura simplificada)
    ingresa_elementos = db.Column(db.Boolean, default=False)
    elementos_observacion = db.Column(db.String(500))
    elemento_portatil = db.Column(db.Boolean, default=False)
    elemento_celular = db.Column(db.Boolean, default=False)
    elemento_herramientas = db.Column(db.Boolean, default=False)
    elemento_otros = db.Column(db.Boolean, default=False)
    
    # Número de visitantes
    numero_visitantes = db.Column(db.Integer, default=1)
    visitantes_adicionales = db.Column(db.Text)
    
    # Fotografía
    fotografia_visitante = db.Column(db.String(500))
    
    # Número de carnet
    numero_carnet = db.Column(db.String(50))
    
    # Estado de la visita
    estado_visita = db.Column(db.String(50), nullable=False, default='EN_INSTALACIONES')  # EN_INSTALACIONES, SALIO
    
    # Sede donde se registró
    sede_id = db.Column(db.Integer, db.ForeignKey('sedes.id'), nullable=False)
    sede = db.relationship('Sede', backref='visitas')
    
    # Usuario que registró
    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_registro = db.relationship('Usuario', backref='visitas_registradas')
    
    # Relación con autorización previa (si fue utilizada)
    autorizacion = db.relationship('AutorizacionIngreso', foreign_keys=[autorizacion_previa_id], 
                                   backref=db.backref('registro_uso', uselist=False))
    
    # Timestamps
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del visitante"""
        return f"{self.primer_nombre} {self.segundo_nombre or ''} {self.primer_apellido} {self.segundo_apellido or ''}".strip()
    
    def marcar_salida(self):
        """Marca la salida del visitante"""
        ahora = datetime.now()
        self.fecha_salida = ahora.date()
        self.hora_salida = ahora.time()
        self.estado_visita = 'SALIO'
    
    def get_elementos_ingresados(self):
        """Retorna una lista de elementos ingresados"""
        elementos = []
        if self.check1_elemento_tecnologico:
            elementos.append(f"Elemento tecnológico: {self.check1_descripcion}")
        if self.check2_arma_fuego:
            elementos.append(f"Arma de fuego: {self.check2_descripcion}")
        if self.check3_otro_elemento:
            elementos.append(f"Otro elemento: {self.check3_descripcion}")
        if self.check4_herramienta:
            elementos.append(f"Herramienta: {self.check4_descripcion}")
        if self.check5_adicional:
            elementos.append(f"Adicional: {self.check5_descripcion}")
        return elementos
    
    def to_dict(self):
        """Convierte el log a diccionario"""
        return {
            'id': self.id,
            'fecha_ingreso': self.fecha_ingreso.strftime('%d/%m/%Y') if self.fecha_ingreso else None,
            'hora_ingreso': self.hora_ingreso.strftime('%H:%M:%S') if self.hora_ingreso else None,
            'fecha_salida': self.fecha_salida.strftime('%d/%m/%Y') if self.fecha_salida else None,
            'hora_salida': self.hora_salida.strftime('%H:%M:%S') if self.hora_salida else None,
            'tipo_identificacion': self.tipo_identificacion,
            'num_identificacion': self.num_identificacion,
            'nombre_completo': self.get_nombre_completo(),
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'num_telefono': self.num_telefono,
            'dir_correo': self.dir_correo,
            'empresa': self.empresa,
            'nit_empresa': self.nit_empresa,
            'prefijo_dependencia': self.prefijo_dependencia,
            'descripcion_dependencia': self.descripcion_dependencia,
            'funcionario_recibe': self.funcionario_recibe,
            'funcionario_autoriza': self.funcionario_autoriza,
            'autorizacion_previa_id': self.autorizacion_previa_id,
            'observaciones1': self.observaciones1,
            'elementos': self.get_elementos_ingresados(),
            # Nuevos campos
            'ingresa_elementos': self.ingresa_elementos,
            'elementos_observacion': self.elementos_observacion,
            'elemento_portatil': self.elemento_portatil,
            'elemento_celular': self.elemento_celular,
            'elemento_herramientas': self.elemento_herramientas,
            'elemento_otros': self.elemento_otros,
            'numero_visitantes': self.numero_visitantes,
            'visitantes_adicionales': self.visitantes_adicionales,
            'fotografia_visitante': self.fotografia_visitante,
            'numero_carnet': self.numero_carnet,
            'estado_visita': self.estado_visita,
            'sede_id': self.sede_id,
            'sede': self.sede.descripcion_sede if self.sede else None,
            'codigo_sede': self.sede.codigo_sede if self.sede else None,
            'usuario_registro': self.usuario_registro.usuario if self.usuario_registro else None,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    def __repr__(self):
        return f'<LogVisitante {self.num_identificacion} - {self.fecha_ingreso} - {self.estado_visita}>'
