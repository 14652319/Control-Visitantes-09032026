"""
========================================
RUTAS: AUTENTICACIÓN
Login, Logout, Verificación de Sesión
========================================
"""

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models import Usuario, LogEvento
from app.models.configuracion_sistema import ConfiguracionSistema
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_client_info():
    """Obtiene información del cliente"""
    return {
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', '')[:500]
    }


@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        usuario_input = data.get('usuario', '').strip().lower()
        password = data.get('password', '')
        
        if not usuario_input or not password:
            return jsonify({
                'success': False,
                'message': 'Usuario y contraseña son requeridos'
            }), 400
        
        # Buscar usuario (case-insensitive)
        usuario = Usuario.query.filter(
            db.func.lower(Usuario.usuario) == usuario_input
        ).first()
        
        if not usuario:
            # Registrar intento fallido
            client_info = get_client_info()
            LogEvento.registrar_evento(
                tipo_evento='LOGIN_FALLIDO',
                descripcion=f'Intento de login con usuario inexistente: {usuario_input}',
                ip_address=client_info['ip'],
                user_agent=client_info['user_agent'],
                nivel='WARNING'
            )
            return jsonify({
                'success': False,
                'message': 'Usuario o contraseña incorrectos'
            }), 401
        
        # Verificar si está bloqueado
        if usuario.estado == 'BLOQUEADO':
            client_info = get_client_info()
            LogEvento.registrar_evento(
                tipo_evento='ACCESO_DENEGADO',
                descripcion=f'Intento de acceso de usuario bloqueado: {usuario_input}',
                usuario=usuario,
                ip_address=client_info['ip'],
                user_agent=client_info['user_agent'],
                nivel='WARNING'
            )
            return jsonify({
                'success': False,
                'message': 'Usuario bloqueado. Contacte al administrador.'
            }), 403
        
        # Verificar contraseña
        if not usuario.check_password(password):
            usuario.incrementar_intentos_fallidos()
            db.session.commit()
            
            client_info = get_client_info()
            LogEvento.registrar_evento(
                tipo_evento='LOGIN_FALLIDO',
                descripcion=f'Contraseña incorrecta para usuario: {usuario_input}',
                usuario=usuario,
                ip_address=client_info['ip'],
                user_agent=client_info['user_agent'],
                nivel='WARNING'
            )
            
            # Obtener máximo de intentos desde configuración
            max_intentos = int(ConfiguracionSistema.obtener_valor('max_intentos_login', 10))
            intentos_restantes = max_intentos - usuario.intentos_fallidos
            mensaje = f'Contraseña incorrecta. Intentos restantes: {intentos_restantes}'
            
            if usuario.estado == 'BLOQUEADO':
                mensaje = 'Usuario bloqueado por exceso de intentos fallidos'
                LogEvento.registrar_evento(
                    tipo_evento='USUARIO_BLOQUEADO',
                    descripcion=f'Usuario bloqueado automáticamente: {usuario_input}',
                    usuario=usuario,
                    ip_address=client_info['ip'],
                    nivel='ERROR'
                )
            
            return jsonify({
                'success': False,
                'message': mensaje,
                'bloqueado': usuario.estado == 'BLOQUEADO'
            }), 401
        
        # Login exitoso
        usuario.resetear_intentos_fallidos()
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        # Configurar tiempo de sesión desde base de datos
        tiempo_sesion = int(ConfiguracionSistema.obtener_valor('tiempo_sesion_minutos', 45))
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=tiempo_sesion)
        
        login_user(usuario, remember=True)
        
        client_info = get_client_info()
        LogEvento.registrar_evento(
            tipo_evento='LOGIN_EXITOSO',
            descripcion=f'Login exitoso: {usuario_input}',
            usuario=usuario,
            ip_address=client_info['ip'],
            user_agent=client_info['user_agent'],
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Endpoint de logout"""
    try:
        client_info = get_client_info()
        LogEvento.registrar_evento(
            tipo_evento='LOGOUT',
            descripcion=f'Cierre de sesión: {current_user.usuario}',
            usuario=current_user,
            ip_address=client_info['ip'],
            user_agent=client_info['user_agent'],
            nivel='INFO'
        )
        
        # Limpiar sesión
        logout_user()
        session.clear()
        
        response = jsonify({
            'success': True,
            'message': 'Sesión cerrada correctamente'
        })
        
        # Eliminar cookies de sesión
        response.set_cookie('session', '', expires=0)
        response.set_cookie('remember_token', '', expires=0)
        
        return response, 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Obtiene la información del usuario actual"""
    try:
        return jsonify({
            'success': True,
            'usuario': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/check-session', methods=['GET'])
def check_session():
    """Verifica si hay una sesión activa"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'usuario': current_user.to_dict()
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200


# Decorador para verificar rol
def role_required(*roles):
    """Decorador para restringir acceso por rol"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.rol not in roles:
                return jsonify({
                    'success': False,
                    'message': 'No tiene permisos para realizar esta acción'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@bp.route('/verificar-identificacion/<num_identificacion>', methods=['GET'])
@limiter.limit("10 per minute")
def verificar_identificacion(num_identificacion):
    """
    Verifica si una identificación ya está registrada
    Endpoint público para registro de funcionarios
    Rate-limited para prevenir enumeración masiva
    """
    try:
        num_id = str(num_identificacion).strip()
        usuario_existe = Usuario.query.filter_by(num_identificacion=num_id).first()
        
        if usuario_existe:
            return jsonify({
                'existe': True,
                'message': 'Esta identificación ya está registrada en el sistema.'
            }), 200
        else:
            return jsonify({
                'existe': False,
                'message': 'Identificación disponible'
            }), 200
            
    except Exception as e:
        logger.error(f"Error verificando identificación: {e}")
        return jsonify({
            'existe': False,
            'message': 'Error al verificar'
        }), 500


@bp.route('/verificar-correo/<correo>', methods=['GET'])
@limiter.limit("10 per minute")
def verificar_correo(correo):
    """
    Verifica si un correo electrónico ya está registrado
    Endpoint público para registro de funcionarios
    Rate-limited para prevenir enumeración masiva
    """
    try:
        email = correo.lower().strip()
        usuario_existe = Usuario.query.filter(
            db.func.lower(Usuario.dir_correo) == email
        ).first()
        
        if usuario_existe:
            return jsonify({
                'existe': True,
                'message': 'Este correo ya está registrado en el sistema.'
            }), 200
        else:
            return jsonify({
                'existe': False,
                'message': 'Correo disponible'
            }), 200
            
    except Exception as e:
        logger.error(f"Error verificando correo: {e}")
        return jsonify({
            'existe': False,
            'message': 'Error al verificar'
        }), 500


@bp.route('/registro-funcionario', methods=['POST'])
@limiter.limit("5 per hour")
def registro_funcionario():
    """
    Registro público de funcionarios
    Crea usuario con estado PENDIENTE y envía correos de notificación
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = [
            'tipo_identificacion', 'num_identificacion', 'primer_nombre', 
            'primer_apellido', 'num_telefono', 'dir_correo', 'sede_id', 
            'usuario', 'password'
        ]
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Validar que el usuario no exista
        usuario_existe = Usuario.query.filter(
            db.func.lower(Usuario.usuario) == data['usuario'].lower()
        ).first()
        
        if usuario_existe:
            return jsonify({
                'success': False,
                'message': 'El nombre de usuario ya existe'
            }), 400
        
        # Validar que el correo no exista
        correo_existe = Usuario.query.filter(
            db.func.lower(Usuario.dir_correo) == data['dir_correo'].lower()
        ).first()
        
        if correo_existe:
            return jsonify({
                'success': False,
                'message': 'El correo electrónico ya está registrado'
            }), 400
        
        # Validar que la identificación no exista
        num_id_input = str(data['num_identificacion']).strip()
        
        identificacion_existe = Usuario.query.filter_by(
            num_identificacion=num_id_input
        ).first()
        
        if identificacion_existe:
            return jsonify({
                'success': False,
                'message': 'Esta identificación ya está registrada en el sistema. Si olvidó su usuario o contraseña, contacte al administrador.'
            }), 400
        
        # Crear nuevo usuario con estado PENDIENTE
        nuevo_usuario = Usuario(
            tipo_identificacion=data['tipo_identificacion'],
            num_identificacion=data['num_identificacion'],
            primer_nombre=data['primer_nombre'].upper(),
            segundo_nombre=data.get('segundo_nombre', '').upper(),
            primer_apellido=data['primer_apellido'].upper(),
            segundo_apellido=data.get('segundo_apellido', '').upper(),
            num_telefono=data['num_telefono'],
            dir_correo=data['dir_correo'].lower(),
            sede_id=data['sede_id'],
            rol='usuario_funcionario',
            estado='PENDIENTE',
            usuario=data['usuario'].lower()
        )
        
        # Establecer contraseña
        nuevo_usuario.set_password(data['password'])
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Registrar evento
        client_info = get_client_info()
        LogEvento.registrar_evento(
            tipo_evento='REGISTRO_FUNCIONARIO',
            descripcion=f'Nuevo registro de funcionario: {nuevo_usuario.usuario}',
            usuario=nuevo_usuario,
            ip_address=client_info['ip'],
            user_agent=client_info['user_agent'],
            nivel='INFO'
        )
        
        # Enviar correos
        from app.services.email_service import (
            enviar_correo_registro_funcionario,
            enviar_correo_notificacion_admin
        )
        
        usuario_data = {
            'primer_nombre': nuevo_usuario.primer_nombre,
            'segundo_nombre': nuevo_usuario.segundo_nombre,
            'primer_apellido': nuevo_usuario.primer_apellido,
            'segundo_apellido': nuevo_usuario.segundo_apellido,
            'tipo_identificacion': nuevo_usuario.tipo_identificacion,
            'num_identificacion': nuevo_usuario.num_identificacion,
            'num_telefono': nuevo_usuario.num_telefono,
            'dir_correo': nuevo_usuario.dir_correo,
            'usuario': nuevo_usuario.usuario
        }
        
        # Correo al funcionario
        enviar_correo_registro_funcionario(usuario_data)
        
        # Correo al administrador master
        admin = Usuario.query.filter_by(rol='usuario_master', estado='ACTIVO').first()
        if admin and admin.dir_correo:
            enviar_correo_notificacion_admin(usuario_data, admin.dir_correo)
        
        return jsonify({
            'success': True,
            'message': 'Registro exitoso. Tu cuenta está pendiente de activación por el administrador.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
