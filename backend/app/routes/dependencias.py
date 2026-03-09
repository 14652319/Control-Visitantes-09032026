"""
========================================
RUTAS: DEPENDENCIAS
Gestión de dependencias asociadas a sedes
========================================
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Dependencia, Sede, LogEvento
from app.routes.auth import role_required

bp = Blueprint('dependencias', __name__, url_prefix='/api/dependencias')


@bp.route('/', methods=['GET'])
@login_required
def listar_dependencias():
    """Lista todas las dependencias o las de una sede específica"""
    try:
        sede_id = request.args.get('sede_id', type=int)
        
        if sede_id:
            # Filtrar por sede (solo activas para el operador)
            sede = Sede.query.get(sede_id)
            if not sede:
                return jsonify({
                    'success': False,
                    'message': 'Sede no encontrada'
                }), 404
            
            dependencias = sede.dependencias.filter_by(estado='ACTIVO').all()
        else:
            # Todas las dependencias (activas e inactivas) para administración
            dependencias = Dependencia.query.order_by(Dependencia.estado.desc(), Dependencia.prefijo_dependencia).all()
        
        return jsonify({
            'success': True,
            'total': len(dependencias),
            'dependencias': [d.to_dict(incluir_sedes=True) for d in dependencias]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/<int:dependencia_id>', methods=['GET'])
@login_required
def obtener_dependencia(dependencia_id):
    """Obtiene una dependencia por ID"""
    try:
        dependencia = Dependencia.query.get(dependencia_id)
        
        if not dependencia:
            return jsonify({
                'success': False,
                'message': 'Dependencia no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'dependencia': dependencia.to_dict(incluir_sedes=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/', methods=['POST'])
@role_required('usuario_master')
def crear_dependencia():
    """Crea una nueva dependencia y la asocia a una o más sedes"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('prefijo_dependencia') or not data.get('descripcion_dependencia'):
            return jsonify({
                'success': False,
                'message': 'Prefijo y descripción son requeridos'
            }), 400
        
        if not data.get('sedes') or len(data['sedes']) == 0:
            return jsonify({
                'success': False,
                'message': 'Debe asociar al menos una sede'
            }), 400
        
        # Verificar que no exista el prefijo
        existe = Dependencia.query.filter_by(
            prefijo_dependencia=data['prefijo_dependencia'].upper()
        ).first()
        
        if existe:
            return jsonify({
                'success': False,
                'message': 'El prefijo de dependencia ya existe'
            }), 409
        
        # Crear dependencia
        dependencia = Dependencia(
            prefijo_dependencia=data['prefijo_dependencia'].upper(),
            descripcion_dependencia=data['descripcion_dependencia'].upper(),
            estado='ACTIVO'
        )
        
        # Asociar sedes
        for sede_id in data['sedes']:
            sede = Sede.query.get(sede_id)
            if sede:
                dependencia.sedes.append(sede)
        
        db.session.add(dependencia)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='DEPENDENCIA_CREADA',
            descripcion=f'Dependencia creada: {dependencia.prefijo_dependencia} - {dependencia.descripcion_dependencia}',
            usuario=current_user,
            datos_adicionales={'dependencia_id': dependencia.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Dependencia creada exitosamente',
            'dependencia': dependencia.to_dict(incluir_sedes=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/<int:dependencia_id>', methods=['PUT'])
@role_required('usuario_master')
def actualizar_dependencia(dependencia_id):
    """Actualiza una dependencia existente"""
    try:
        dependencia = Dependencia.query.get(dependencia_id)
        
        if not dependencia:
            return jsonify({
                'success': False,
                'message': 'Dependencia no encontrada'
            }), 404
        
        data = request.get_json()
        
        if 'descripcion_dependencia' in data:
            dependencia.descripcion_dependencia = data['descripcion_dependencia'].upper()
        
        if 'estado' in data:
            dependencia.estado = data['estado']
        
        if 'sedes' in data:
            # Actualizar asociación de sedes
            dependencia.sedes = []
            for sede_id in data['sedes']:
                sede = Sede.query.get(sede_id)
                if sede:
                    dependencia.sedes.append(sede)
        
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='DEPENDENCIA_MODIFICADA',
            descripcion=f'Dependencia modificada: {dependencia.prefijo_dependencia}',
            usuario=current_user,
            datos_adicionales={'dependencia_id': dependencia.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Dependencia actualizada exitosamente',
            'dependencia': dependencia.to_dict(incluir_sedes=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/<int:dependencia_id>', methods=['DELETE'])
@role_required('usuario_master')
def eliminar_dependencia(dependencia_id):
    """Elimina una dependencia"""
    try:
        dependencia = Dependencia.query.get(dependencia_id)
        
        if not dependencia:
            return jsonify({
                'success': False,
                'message': 'Dependencia no encontrada'
            }), 404
        
        prefijo = dependencia.prefijo_dependencia
        descripcion = dependencia.descripcion_dependencia
        
        db.session.delete(dependencia)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='DEPENDENCIA_ELIMINADA',
            descripcion=f'Dependencia eliminada: {prefijo} - {descripcion}',
            usuario=current_user,
            datos_adicionales={'dependencia_id': dependencia_id},
            nivel='WARNING'
        )
        
        return jsonify({
            'success': True,
            'message': 'Dependencia eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
