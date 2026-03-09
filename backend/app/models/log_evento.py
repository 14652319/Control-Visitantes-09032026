"""
========================================
MODELO: LOG EVENTOS
Registra todos los eventos del sistema para auditoría
========================================
"""

from datetime import datetime
from app.extensions import db


class LogEvento(db.Model):
    """Modelo para registrar eventos del sistema (auditoría)"""
    
    __tablename__ = 'log_eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Fecha y hora del evento
    fecha = db.Column(db.Date, nullable=False, index=True)
    hora = db.Column(db.Time, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Usuario que ejecutó la acción
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', backref='eventos')
    usuario_nombre = db.Column(db.String(200))  # Desnormalizado para histórico
    
    # Tipo de evento
    tipo_evento = db.Column(db.String(100), nullable=False, index=True)
    """
    Tipos de eventos:
    - LOGIN_EXITOSO
    - LOGIN_FALLIDO
    - LOGOUT
    - USUARIO_BLOQUEADO
    - USUARIO_DESBLOQUEADO
    - USUARIO_CREADO
    - USUARIO_MODIFICADO
    - USUARIO_ELIMINADO
    - VISITANTE_REGISTRADO
    - VISITANTE_MODIFICADO
    - VISITANTE_INGRESO
    - VISITANTE_SALIDA
    - VISITANTE_REINGRESO
    - SEDE_CREADA
    - SEDE_MODIFICADA
    - DEPENDENCIA_CREADA
    - DEPENDENCIA_MODIFICADA
    - REPORTE_GENERADO
    - FOTO_CAPTURADA
    - FOTO_ELIMINADA
    - SESION_EXPIRADA
    - ERROR_SISTEMA
    - ACCESO_DENEGADO
    """
    
    # Descripción del evento
    descripcion = db.Column(db.Text, nullable=False)
    
    # Datos adicionales (JSON)
    datos_adicionales = db.Column(db.JSON)
    
    # Información de contexto
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    # Nivel de severidad
    nivel = db.Column(db.String(20), default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    def to_dict(self):
        """Convierte el log a diccionario"""
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%d/%m/%Y') if self.fecha else None,
            'hora': self.hora.strftime('%H:%M:%S') if self.hora else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'usuario_id': self.usuario_id,
            'usuario_nombre': self.usuario_nombre,
            'tipo_evento': self.tipo_evento,
            'descripcion': self.descripcion,
            'datos_adicionales': self.datos_adicionales,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'nivel': self.nivel
        }
    
    @staticmethod
    def registrar_evento(tipo_evento, descripcion, usuario=None, datos_adicionales=None, 
                        ip_address=None, user_agent=None, nivel='INFO'):
        """Método helper para registrar un evento"""
        ahora = datetime.now()
        evento = LogEvento(
            fecha=ahora.date(),
            hora=ahora.time(),
            timestamp=ahora,
            usuario_id=usuario.id if usuario else None,
            usuario_nombre=f"{usuario.primer_nombre} {usuario.primer_apellido}" if usuario else "Sistema",
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            datos_adicionales=datos_adicionales,
            ip_address=ip_address,
            user_agent=user_agent,
            nivel=nivel
        )
        db.session.add(evento)
        db.session.commit()
        return evento
    
    def __repr__(self):
        return f'<LogEvento {self.tipo_evento} - {self.timestamp}>'
