"""
========================================
RUTAS DE CONFIGURACIÓN
Endpoints para gestión de configuración del sistema
========================================
"""

from flask import Blueprint, jsonify, request, session
from app.models.configuracion_sistema import ConfiguracionSistema
from app.models.usuario import Usuario
from app.extensions import db
from functools import wraps


bp = Blueprint('configuracion', __name__, url_prefix='/api/configuracion')


def login_required(f):
    """Decorador para verificar que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorador para verificar que el usuario sea Master"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        
        usuario = db.session.get(Usuario, session['usuario_id'])
        if not usuario or usuario.rol != 'usuario_master':
            return jsonify({'success': False, 'message': 'Acceso denegado. Solo usuarios Master pueden modificar la configuración.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/', methods=['GET'])
@login_required
def obtener_configuraciones():
    """
    Obtener todas las configuraciones del sistema
    Solo usuarios Master pueden ver configuraciones
    """
    try:
        usuario = db.session.get(Usuario, session['usuario_id'])
        if not usuario or usuario.rol != 'usuario_master':
            return jsonify({
                'success': False, 
                'message': 'Acceso denegado'
            }), 403
        
        configuraciones = ConfiguracionSistema.query.all()
        
        return jsonify({
            'success': True,
            'configuraciones': [conf.to_dict() for conf in configuraciones]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<string:clave>', methods=['GET'])
@login_required
def obtener_configuracion(clave):
    """
    Obtener una configuración específica por clave
    """
    try:
        valor = ConfiguracionSistema.obtener_valor(clave)
        
        if valor is None:
            return jsonify({
                'success': False,
                'message': f'Configuración {clave} no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'clave': clave,
            'valor': valor
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<string:clave>', methods=['PUT'])
@admin_required
def actualizar_configuracion(clave):
    """
    Actualizar una configuración específica
    Solo usuarios Master pueden actualizar
    """
    try:
        data = request.get_json()
        
        if 'valor' not in data:
            return jsonify({
                'success': False,
                'message': 'El campo valor es requerido'
            }), 400
        
        valor = data['valor']
        descripcion = data.get('descripcion', '')
        tipo_dato = data.get('tipo_dato', 'string')
        
        # Validaciones específicas según la clave
        if clave == 'dias_vigencia_autorizacion':
            try:
                valor_int = int(valor)
                if valor_int < 1 or valor_int > 365:
                    return jsonify({
                        'success': False,
                        'message': 'Los días de vigencia deben estar entre 1 y 365'
                    }), 400
                valor = valor_int
                tipo_dato = 'int'
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'El valor debe ser un número entero'
                }), 400
        
        elif clave == 'max_intentos_login':
            try:
                valor_int = int(valor)
                if valor_int < 1 or valor_int > 100:
                    return jsonify({
                        'success': False,
                        'message': 'Los intentos máximos deben estar entre 1 y 100'
                    }), 400
                valor = valor_int
                tipo_dato = 'int'
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'El valor debe ser un número entero'
                }), 400
        
        elif clave == 'tiempo_sesion_minutos':
            try:
                valor_int = int(valor)
                if valor_int < 5 or valor_int > 1440:  # Máximo 24 horas
                    return jsonify({
                        'success': False,
                        'message': 'El tiempo de sesión debe estar entre 5 y 1440 minutos'
                    }), 400
                valor = valor_int
                tipo_dato = 'int'
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'El valor debe ser un número entero'
                }), 400
        
        # Actualizar o crear la configuración
        ConfiguracionSistema.establecer_valor(clave, valor, descripcion, tipo_dato)
        
        return jsonify({
            'success': True,
            'message': f'Configuración {clave} actualizada correctamente',
            'clave': clave,
            'valor': valor
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/batch', methods=['PUT'])
@admin_required
def actualizar_configuraciones_batch():
    """
    Actualizar múltiples configuraciones en una sola petición
    Solo usuarios Master pueden actualizar
    """
    try:
        data = request.get_json()
        
        if 'configuraciones' not in data or not isinstance(data['configuraciones'], list):
            return jsonify({
                'success': False,
                'message': 'Se requiere un array de configuraciones'
            }), 400
        
        resultados = []
        errores = []
        
        for config in data['configuraciones']:
            clave = config.get('clave')
            valor = config.get('valor')
            descripcion = config.get('descripcion', '')
            tipo_dato = config.get('tipo_dato', 'string')
            
            if not clave or valor is None:
                errores.append(f'Configuración inválida: {config}')
                continue
            
            try:
                ConfiguracionSistema.establecer_valor(clave, valor, descripcion, tipo_dato)
                resultados.append({'clave': clave, 'status': 'actualizado'})
            except Exception as e:
                errores.append(f'Error en {clave}: {str(e)}')
        
        if errores:
            return jsonify({
                'success': False,
                'message': 'Algunos cambios fallaron',
                'resultados': resultados,
                'errores': errores
            }), 400
        
        return jsonify({
            'success': True,
            'message': f'{len(resultados)} configuraciones actualizadas',
            'resultados': resultados
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
