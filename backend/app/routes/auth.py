"""
========================================
RUTAS: AUTENTICACIÓN
Login, Logout, Verificación de Sesión
========================================
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models import Usuario, LogEvento
from datetime import datetime
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
            
            intentos_restantes = 10 - usuario.intentos_fallidos
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
            'message': f'Error en el servidor: {str(e)}'
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
            'message': f'Error al cerrar sesión: {str(e)}'
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
            'message': f'Error: {str(e)}'
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
