"""
========================================
RUTAS: USUARIOS
Gestión de usuarios del sistema (solo usuario_master)
========================================
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Usuario, LogEvento
from app.routes.auth import role_required

bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')


@bp.route('/', methods=['GET'])
@role_required('usuario_master')
def listar_usuarios():
    """Lista todos los usuarios"""
    try:
        usuarios = Usuario.query.all()
        
        return jsonify({
            'success': True,
            'total': len(usuarios),
            'usuarios': [u.to_dict() for u in usuarios]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<int:usuario_id>', methods=['GET'])
@role_required('usuario_master')
def obtener_usuario(usuario_id):
    """Obtiene un usuario por ID"""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/', methods=['POST'])
@role_required('usuario_master')
def crear_usuario():
    """Crea un nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos base
        campos_requeridos = [
            'tipo_identificacion', 'num_identificacion', 'primer_nombre',
            'primer_apellido', 'num_telefono', 'dir_correo',
            'rol', 'usuario', 'password'
        ]
        
        # sede_id es requerido solo para operadores y funcionarios
        # Los usuarios Master tienen acceso global (sede_id puede ser NULL)
        if data.get('rol') != 'usuario_master':
            campos_requeridos.append('sede_id')
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Verificar que no exista el usuario
        existe_usuario = Usuario.query.filter_by(usuario=data['usuario'].upper()).first()
        if existe_usuario:
            return jsonify({
                'success': False,
                'message': 'El nombre de usuario ya existe'
            }), 409
        
        # Verificar que no exista el correo
        existe_correo = Usuario.query.filter_by(dir_correo=data['dir_correo'].lower()).first()
        if existe_correo:
            return jsonify({
                'success': False,
                'message': 'El correo electrónico ya está registrado'
            }), 409
        
        # Validar contraseña
        password = data['password']
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }), 400
        
        # Crear usuario
        usuario = Usuario(
            tipo_identificacion=data['tipo_identificacion'].upper(),
            num_identificacion=data['num_identificacion'].upper(),
            primer_nombre=data['primer_nombre'].upper(),
            segundo_nombre=data.get('segundo_nombre', '').upper(),
            primer_apellido=data['primer_apellido'].upper(),
            segundo_apellido=data.get('segundo_apellido', '').upper(),
            num_telefono=data['num_telefono'].upper(),
            dir_correo=data['dir_correo'].lower(),
            sede_id=data.get('sede_id') if data.get('sede_id') else None,  # NULL para Master
            rol=data['rol'],
            estado='ACTIVO',
            usuario=data['usuario'].upper()
        )
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='USUARIO_CREADO',
            descripcion=f'Usuario creado: {usuario.usuario} ({usuario.rol})',
            usuario=current_user,
            datos_adicionales={'nuevo_usuario_id': usuario.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'usuario': usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<int:usuario_id>', methods=['PUT'])
@role_required('usuario_master')
def actualizar_usuario(usuario_id):
    """Actualiza un usuario existente"""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        data = request.get_json()
        
        # Validar que solo usuarios Master pueden tener sede_id NULL
        if 'sede_id' in data:
            if data['sede_id'] == '' or data['sede_id'] is None:
                # Solo Master puede tener sede_id NULL
                if usuario.rol != 'usuario_master' and data.get('rol', usuario.rol) != 'usuario_master':
                    return jsonify({
                        'success': False,
                        'message': 'Solo los usuarios Master pueden tener acceso global. Operadores y Funcionarios deben tener una sede asignada.'
                    }), 400
        
        # Actualizar campos permitidos
        if 'primer_nombre' in data:
            usuario.primer_nombre = data['primer_nombre'].upper()
        if 'segundo_nombre' in data:
            usuario.segundo_nombre = data['segundo_nombre'].upper()
        if 'primer_apellido' in data:
            usuario.primer_apellido = data['primer_apellido'].upper()
        if 'segundo_apellido' in data:
            usuario.segundo_apellido = data['segundo_apellido'].upper()
        if 'num_telefono' in data:
            usuario.num_telefono = data['num_telefono'].upper()
        if 'dir_correo' in data:
            usuario.dir_correo = data['dir_correo'].lower()
        if 'sede_id' in data:
            usuario.sede_id = data['sede_id'] if data['sede_id'] else None
        if 'estado' in data:
            usuario.estado = data['estado']
        
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='USUARIO_MODIFICADO',
            descripcion=f'Usuario modificado: {usuario.usuario}',
            usuario=current_user,
            datos_adicionales={'usuario_modificado_id': usuario.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<int:usuario_id>/resetear-password', methods=['POST'])
@role_required('usuario_master')
def resetear_password(usuario_id):
    """Resetea la contraseña de un usuario"""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        data = request.get_json()
        nueva_password = data.get('nueva_password')
        
        if not nueva_password or len(nueva_password) < 8:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }), 400
        
        usuario.set_password(nueva_password)
        usuario.resetear_intentos_fallidos()
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='USUARIO_DESBLOQUEADO',
            descripcion=f'Contraseña reseteada para usuario: {usuario.usuario}',
            usuario=current_user,
            datos_adicionales={'usuario_reseteado_id': usuario.id},
            nivel='WARNING'
        )
        
        return jsonify({
            'success': True,
            'message': 'Contraseña reseteada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<int:usuario_id>/desbloquear', methods=['POST'])
@role_required('usuario_master')
def desbloquear_usuario(usuario_id):
    """Desbloquea un usuario bloqueado por intentos fallidos"""
    try:
        usuario = db.session.get(Usuario, usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        if usuario.estado != 'BLOQUEADO':
            return jsonify({
                'success': False,
                'message': f'El usuario no está bloqueado (estado actual: {usuario.estado})'
            }), 400
        
        # Desbloquear usuario
        usuario.resetear_intentos_fallidos()
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='USUARIO_DESBLOQUEADO',
            descripcion=f'Usuario desbloqueado manualmente: {usuario.usuario}',
            usuario=current_user,
            datos_adicionales={
                'usuario_desbloqueado_id': usuario.id,
                'intentos_fallidos_anteriores': usuario.intentos_fallidos
            },
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': f'Usuario {usuario.usuario} desbloqueado exitosamente',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/activar/<int:usuario_id>', methods=['POST'])
@role_required('usuario_master')
def activar_usuario(usuario_id):
    """
    Activa un usuario PENDIENTE y envía correo de confirmación
    """
    try:
        usuario = db.session.get(Usuario, usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        if usuario.estado != 'PENDIENTE':
            return jsonify({
                'success': False,
                'message': 'Solo se pueden activar usuarios en estado PENDIENTE'
            }), 400
        
        # Cambiar estado a ACTIVO
        usuario.estado = 'ACTIVO'
        usuario.intentos_fallidos = 0
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='USUARIO_ACTIVADO',
            descripcion=f'Usuario activado por administrador: {usuario.usuario}',
            usuario=current_user,
            datos_adicionales={
                'usuario_activado_id': usuario.id,
                'usuario_activado': usuario.usuario
            },
            nivel='INFO'
        )
        
        # Enviar correo de confirmación
        from app.services.email_service import enviar_correo_cuenta_activada
        
        usuario_data = {
            'primer_nombre': usuario.primer_nombre,
            'primer_apellido': usuario.primer_apellido,
            'dir_correo': usuario.dir_correo,
            'usuario': usuario.usuario
        }
        
        enviar_correo_cuenta_activada(usuario_data)
        
        return jsonify({
            'success': True,
            'message': f'Usuario {usuario.usuario} activado exitosamente',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/rechazar/<int:usuario_id>', methods=['POST'])
@role_required('usuario_master')
def rechazar_usuario(usuario_id):
    """
    Rechaza una solicitud de usuario PENDIENTE y envía correo
    """
    try:
        data = request.get_json()
        motivo = data.get('motivo', '') if data else ''
        
        usuario = db.session.get(Usuario, usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        if usuario.estado != 'PENDIENTE':
            return jsonify({
                'success': False,
                'message': 'Solo se pueden rechazar usuarios en estado PENDIENTE'
            }), 400
        
        # Cambiar estado a RECHAZADO
        usuario.estado = 'RECHAZADO'
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='USUARIO_RECHAZADO',
            descripcion=f'Solicitud rechazada por administrador: {usuario.usuario}',
            usuario=current_user,
            datos_adicionales={
                'usuario_rechazado_id': usuario.id,
                'usuario_rechazado': usuario.usuario,
                'motivo': motivo
            },
            nivel='WARNING'
        )
        
        # Enviar correo de rechazo
        from app.services.email_service import enviar_correo_cuenta_rechazada
        
        usuario_data = {
            'primer_nombre': usuario.primer_nombre,
            'primer_apellido': usuario.primer_apellido,
            'dir_correo': usuario.dir_correo,
            'usuario': usuario.usuario
        }
        
        enviar_correo_cuenta_rechazada(usuario_data, motivo)
        
        return jsonify({
            'success': True,
            'message': f'Solicitud de {usuario.usuario} rechazada',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
