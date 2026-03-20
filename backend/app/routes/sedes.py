"""
========================================
RUTAS: SEDES
Gestión de sedes de la empresa
========================================
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Sede, LogEvento, Usuario, LogVisitante
from app.routes.auth import role_required

bp = Blueprint('sedes', __name__, url_prefix='/api/sedes')


@bp.route('/publico', methods=['GET'])
def listar_sedes_publico():
    """Lista sedes activas sin autenticación (para registro público)"""
    try:
        sedes = Sede.query.filter_by(estado='ACTIVO').order_by(Sede.codigo_sede).all()
        
        return jsonify({
            'success': True,
            'sedes': [s.to_dict() for s in sedes]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/', methods=['GET'])
@login_required
def listar_sedes():
    """Lista todas las sedes"""
    try:
        # Listar todas las sedes (activas e inactivas) ordenadas por estado y código
        sedes = Sede.query.order_by(Sede.estado.desc(), Sede.codigo_sede).all()
        
        return jsonify({
            'success': True,
            'total': len(sedes),
            'sedes': [s.to_dict() for s in sedes]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'No se pudieron listar las sedes. Inténtelo nuevamente.'
        }), 500


@bp.route('/<int:sede_id>', methods=['GET'])
@login_required
def obtener_sede(sede_id):
    """Obtiene una sede por ID"""
    try:
        sede = Sede.query.get(sede_id)
        
        if not sede:
            return jsonify({
                'success': False,
                'message': 'Sede no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'sede': sede.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'No se pudo obtener la información de la sede. Inténtelo nuevamente.'
        }), 500


@bp.route('/', methods=['POST'])
@role_required('usuario_master')
def crear_sede():
    """Crea una nueva sede"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('codigo_sede') or not data.get('descripcion_sede') or not data.get('direccion_sede'):
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        # Verificar que no exista el código
        existe = Sede.query.filter_by(codigo_sede=data['codigo_sede'].upper()).first()
        if existe:
            return jsonify({
                'success': False,
                'message': 'El código de sede ya existe'
            }), 409
        
        # Crear sede
        sede = Sede(
            codigo_sede=data['codigo_sede'].upper(),
            descripcion_sede=data['descripcion_sede'].upper(),
            direccion_sede=data['direccion_sede'].upper(),
            estado='ACTIVO'
        )
        
        db.session.add(sede)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='SEDE_CREADA',
            descripcion=f'Sede creada: {sede.codigo_sede} - {sede.descripcion_sede}',
            usuario=current_user,
            datos_adicionales={'sede_id': sede.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Sede creada exitosamente',
            'sede': sede.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<int:sede_id>', methods=['PUT'])
@role_required('usuario_master')
def actualizar_sede(sede_id):
    """Actualiza una sede existente"""
    try:
        sede = Sede.query.get(sede_id)
        
        if not sede:
            return jsonify({
                'success': False,
                'message': 'Sede no encontrada'
            }), 404
        
        data = request.get_json()
        
        if 'descripcion_sede' in data:
            sede.descripcion_sede = data['descripcion_sede'].upper()
        if 'direccion_sede' in data:
            sede.direccion_sede = data['direccion_sede'].upper()
        if 'estado' in data:
            sede.estado = data['estado']
        
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='SEDE_MODIFICADA',
            descripcion=f'Sede modificada: {sede.codigo_sede}',
            usuario=current_user,
            datos_adicionales={'sede_id': sede.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Sede actualizada exitosamente',
            'sede': sede.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/<int:sede_id>', methods=['DELETE'])
@role_required('usuario_master')
def eliminar_sede(sede_id):
    """Elimina una sede"""
    try:
        sede = Sede.query.get(sede_id)
        
        if not sede:
            return jsonify({
                'success': False,
                'message': 'Sede no encontrada'
            }), 404
        
        # Verificar si hay usuarios asociados a esta sede
        usuarios_asociados = Usuario.query.filter_by(sede_id=sede_id).count()
        
        if usuarios_asociados > 0:
            return jsonify({
                'success': False,
                'message': f'No se puede eliminar la sede. Hay {usuarios_asociados} usuario(s) asociado(s). Primero reasigne o elimine los usuarios de esta sede.'
            }), 400
        
        # Verificar si hay registros de visitantes asociados a esta sede
        visitantes_registrados = LogVisitante.query.filter_by(sede_id=sede_id).count()
        
        if visitantes_registrados > 0:
            return jsonify({
                'success': False,
                'message': f'No se puede eliminar la sede. Hay {visitantes_registrados} registro(s) de visitas asociado(s). Esta sede tiene historial de visitantes y no puede ser eliminada por integridad de datos.'
            }), 400
        
        codigo_sede = sede.codigo_sede
        descripcion_sede = sede.descripcion_sede
        
        db.session.delete(sede)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='SEDE_ELIMINADA',
            descripcion=f'Sede eliminada: {codigo_sede} - {descripcion_sede}',
            usuario=current_user,
            datos_adicionales={'sede_id': sede_id},
            nivel='WARNING'
        )
        
        return jsonify({
            'success': True,
            'message': 'Sede eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
