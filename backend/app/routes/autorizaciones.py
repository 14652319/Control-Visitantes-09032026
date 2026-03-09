"""
========================================
RUTAS: AUTORIZACIONES DE INGRESO
Gestión de autorizaciones previas de visitantes
========================================
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import AutorizacionIngreso, LogVisitante, LogEvento, Sede, Usuario
from app.routes.auth import role_required
from datetime import datetime, timedelta
from sqlalchemy import or_, and_

bp = Blueprint('autorizaciones', __name__, url_prefix='/api/autorizaciones')


@bp.route('/', methods=['GET'])
@login_required
def listar_autorizaciones():
    """
    Lista autorizaciones según el rol del usuario
    - usuario_master: Ve todas las autorizaciones
    - usuario_funcionario: Ve solo sus autorizaciones
    - usuario_operador: Ve solo las pendientes de su sede
    """
    try:
        # Obtener parámetros de filtro
        estado = request.args.get('estado', None)
        sede_id = request.args.get('sede_id', None)
        incluir_vencidas = request.args.get('incluir_vencidas', 'false').lower() == 'true'
        
        # Query base
        query = AutorizacionIngreso.query
        
        # Filtrar según el rol
        print(f"\n🔍 [AUTORIZACIONES] Usuario: {current_user.usuario} (Rol: {current_user.rol})")
        if current_user.rol == 'usuario_funcionario':
            # Funcionarios solo ven sus propias autorizaciones
            query = query.filter_by(usuario_id=current_user.id)
            print(f"   → Filtrado por usuario_id={current_user.id}")
        elif current_user.rol == 'usuario_operador':
            # Operadores ven solo las pendientes de su sede
            query = query.filter_by(
                sede_id=current_user.sede_id,
                estado='PENDIENTE'
            )
            print(f"   → Filtrado por sede_id={current_user.sede_id}, estado=PENDIENTE")
            # Verificar vencimiento de las pendientes
            autorizaciones = query.all()
            for auth in autorizaciones:
                auth.verificar_vencimiento()
            db.session.commit()
        # usuario_master no tiene filtros adicionales
        else:
            print(f"   → Sin filtros de rol (Master)")
        
        # Aplicar filtros adicionales
        if estado:
            query = query.filter_by(estado=estado)
        
        if sede_id and current_user.rol != 'usuario_operador':
            query = query.filter_by(sede_id=int(sede_id))
        
        # Filtrar vencidas si no se solicitan explícitamente
        if not incluir_vencidas and estado != 'VENCIDA':
            query = query.filter(or_(
                AutorizacionIngreso.estado != 'PENDIENTE',
                AutorizacionIngreso.fecha_vencimiento > datetime.now().date()
            ))
        
        # Ordenar por fecha de creación descendente
        autorizaciones = query.order_by(
            AutorizacionIngreso.fecha_creacion.desc()
        ).all()
        
        print(f"   → Total autorizaciones encontradas: {len(autorizaciones)}")
        
        # Verificar vencimiento de autorizaciones pendientes
        for auth in autorizaciones:
            if auth.estado == 'PENDIENTE':
                print(f"      • {auth.num_identificacion} - Fecha venc: {auth.fecha_vencimiento} - Estado: {auth.estado}")
                auth.verificar_vencimiento()
        
        db.session.commit()
        
        print(f"✅ Retornando {len(autorizaciones)} autorizaciones\n")
        
        return jsonify({
            'success': True,
            'autorizaciones': [auth.to_dict(incluir_usuario=True) for auth in autorizaciones],
            'total': len(autorizaciones)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al listar autorizaciones: {str(e)}'
        }), 500


@bp.route('/buscar', methods=['GET'])
@login_required
def buscar_por_identificacion():
    """
    Busca autorizaciones pendientes por número de identificación
    Usado por operadores al registrar un visitante
    """
    try:
        num_identificacion = request.args.get('identificacion', '').upper()
        
        if not num_identificacion:
            return jsonify({
                'success': False,
                'message': 'Número de identificación requerido'
            }), 400
        
        # Buscar autorizaciones pendientes y no vencidas
        autorizaciones = AutorizacionIngreso.query.filter_by(
            num_identificacion=num_identificacion,
            estado='PENDIENTE'
        ).filter(
            AutorizacionIngreso.fecha_vencimiento > datetime.now().date()
        ).all()
        
        # Si es operador, filtrar por su sede
        if current_user.rol == 'usuario_operador':
            autorizaciones = [
                auth for auth in autorizaciones 
                if auth.sede_id == current_user.sede_id
            ]
        
        # Verificar vencimiento
        for auth in autorizaciones:
            auth.verificar_vencimiento()
        
        db.session.commit()
        
        # Filtrar las que siguen pendientes después de verificar
        autorizaciones = [auth for auth in autorizaciones if auth.estado == 'PENDIENTE']
        
        return jsonify({
            'success': True,
            'encontrado': len(autorizaciones) > 0,
            'autorizaciones': [auth.to_dict(incluir_usuario=True) for auth in autorizaciones],
            'total': len(autorizaciones)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al buscar autorizaciones: {str(e)}'
        }), 500


@bp.route('/', methods=['POST'])
@login_required
@role_required('usuario_funcionario', 'usuario_master')
def crear_autorizacion():
    """
    Crea una nueva autorización de ingreso
    Solo usuario_funcionario y usuario_master
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = [
            'tipo_identificacion', 'num_identificacion', 'primer_nombre',
            'primer_apellido', 'empresa', 'prefijo_dependencia',
            'descripcion_dependencia', 'funcionario_autoriza'
        ]
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Obtener la sede del usuario actual
        sede_id = current_user.sede_id
        
        # Si es master y se especifica una sede diferente, usarla
        if current_user.rol == 'usuario_master' and data.get('sede_id'):
            sede_id = int(data.get('sede_id'))
        
        # Crear la autorización
        nueva_autorizacion = AutorizacionIngreso(
            tipo_identificacion=data['tipo_identificacion'].upper(),
            num_identificacion=data['num_identificacion'].upper(),
            primer_nombre=data['primer_nombre'].upper(),
            segundo_nombre=data.get('segundo_nombre', '').upper() if data.get('segundo_nombre') else None,
            primer_apellido=data['primer_apellido'].upper(),
            segundo_apellido=data.get('segundo_apellido', '').upper() if data.get('segundo_apellido') else None,
            empresa=data['empresa'].upper(),
            nit_empresa=data.get('nit_empresa', '').upper() if data.get('nit_empresa') else None,
            prefijo_dependencia=data['prefijo_dependencia'].upper(),
            descripcion_dependencia=data['descripcion_dependencia'].upper(),
            funcionario_autoriza=data['funcionario_autoriza'].upper(),
            observaciones=data.get('observaciones', ''),
            estado='PENDIENTE',
            usuario_id=current_user.id,
            sede_id=sede_id
        )
        # fecha_vencimiento se establece automáticamente en el __init__
        
        db.session.add(nueva_autorizacion)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='AUTORIZACION_CREADA',
            descripcion=f'Autorización creada para {nueva_autorizacion.num_identificacion}',
            usuario=current_user,
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Autorización creada exitosamente',
            'autorizacion': nueva_autorizacion.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear autorización: {str(e)}'
        }), 500


@bp.route('/<int:id>', methods=['GET'])
@login_required
def obtener_autorizacion(id):
    """Obtiene una autorización específica por ID"""
    try:
        autorizacion = AutorizacionIngreso.query.get(id)
        
        if not autorizacion:
            return jsonify({
                'success': False,
                'message': 'Autorización no encontrada'
            }), 404
        
        # Verificar permisos
        if current_user.rol == 'usuario_funcionario':
            if autorizacion.usuario_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para ver esta autorización'
                }), 403
        elif current_user.rol == 'usuario_operador':
            if autorizacion.sede_id != current_user.sede_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para ver esta autorización'
                }), 403
        
        # Verificar vencimiento si está pendiente
        if autorizacion.estado == 'PENDIENTE':
            autorizacion.verificar_vencimiento()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'autorizacion': autorizacion.to_dict(incluir_usuario=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener autorización: {str(e)}'
        }), 500


@bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('usuario_funcionario', 'usuario_master')
def actualizar_autorizacion(id):
    """
    Actualiza una autorización (solo si está PENDIENTE)
    Solo el creador o un master pueden actualizar
    """
    try:
        autorizacion = AutorizacionIngreso.query.get(id)
        
        if not autorizacion:
            return jsonify({
                'success': False,
                'message': 'Autorización no encontrada'
            }), 404
        
        # Verificar permisos
        if current_user.rol == 'usuario_funcionario':
            if autorizacion.usuario_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para editar esta autorización'
                }), 403
        
        # Verificar que esté pendiente
        if autorizacion.estado != 'PENDIENTE':
            return jsonify({
                'success': False,
                'message': f'No se puede editar una autorización con estado {autorizacion.estado}'
            }), 400
        
        # Verificar vencimiento
        autorizacion.verificar_vencimiento()
        if autorizacion.estado == 'VENCIDA':
            db.session.commit()
            return jsonify({
                'success': False,
                'message': 'No se puede editar una autorización vencida'
            }), 400
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        campos_actualizables = [
            'tipo_identificacion', 'num_identificacion', 'primer_nombre',
            'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'empresa', 'nit_empresa', 'prefijo_dependencia',
            'descripcion_dependencia', 'funcionario_autoriza', 'observaciones'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                valor = data[campo]
                if valor and isinstance(valor, str):
                    valor = valor.upper()
                setattr(autorizacion, campo, valor)
        
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='AUTORIZACION_ACTUALIZADA',
            descripcion=f'Autorización {id} actualizada',
            usuario=current_user,
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Autorización actualizada exitosamente',
            'autorizacion': autorizacion.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar autorización: {str(e)}'
        }), 500


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('usuario_funcionario', 'usuario_master')
def cancelar_autorizacion(id):
    """
    Cancela una autorización (cambia estado a CANCELADA)
    Solo el creador o un master pueden cancelar
    """
    try:
        autorizacion = AutorizacionIngreso.query.get(id)
        
        if not autorizacion:
            return jsonify({
                'success': False,
                'message': 'Autorización no encontrada'
            }), 404
        
        # Verificar permisos
        if current_user.rol == 'usuario_funcionario':
            if autorizacion.usuario_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para cancelar esta autorización'
                }), 403
        
        # Verificar que esté pendiente
        if autorizacion.estado != 'PENDIENTE':
            return jsonify({
                'success': False,
                'message': f'No se puede cancelar una autorización con estado {autorizacion.estado}'
            }), 400
        
        # Cancelar
        autorizacion.cancelar()
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='AUTORIZACION_CANCELADA',
            descripcion=f'Autorización {id} cancelada para {autorizacion.num_identificacion}',
            usuario=current_user,
            nivel='WARNING'
        )
        
        return jsonify({
            'success': True,
            'message': 'Autorización cancelada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al cancelar autorización: {str(e)}'
        }), 500


@bp.route('/<int:id>/eliminar', methods=['DELETE'])
@login_required
@role_required('usuario_funcionario', 'usuario_master')
def eliminar_autorizacion(id):
    """
    Elimina permanentemente una autorización del sistema
    Solo se pueden eliminar autorizaciones VENCIDAS o CANCELADAS (no UTILIZADAS)
    """
    try:
        autorizacion = AutorizacionIngreso.query.get(id)
        
        if not autorizacion:
            return jsonify({
                'success': False,
                'message': 'Autorización no encontrada'
            }), 404
        
        # Verificar permisos
        if current_user.rol == 'usuario_funcionario':
            if autorizacion.usuario_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para eliminar esta autorización'
                }), 403
        
        # Verificar que esté vencida o cancelada (NO utilizada)
        if autorizacion.estado not in ['VENCIDA', 'CANCELADA']:
            return jsonify({
                'success': False,
                'message': f'Solo se pueden eliminar autorizaciones VENCIDAS o CANCELADAS. Estado actual: {autorizacion.estado}'
            }), 400
        
        # Guardar datos para el log
        num_id = autorizacion.num_identificacion
        estado = autorizacion.estado
        
        # Eliminar permanentemente
        db.session.delete(autorizacion)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='AUTORIZACION_ELIMINADA',
            descripcion=f'Autorización {id} eliminada (Estado: {estado}, NumID: {num_id})',
            usuario=current_user,
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Autorización eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar autorización: {str(e)}'
        }), 500


@bp.route('/<int:id>/aplicar', methods=['POST'])
@login_required
@role_required('usuario_operador', 'usuario_master')
def aplicar_autorizacion(id):
    """
    Retorna los datos de la autorización para llenar el formulario
    Al crear el log_visitantes, se debe llamar a marcar_como_utilizada
    Este endpoint solo retorna los datos, no marca como utilizada
    """
    try:
        autorizacion = AutorizacionIngreso.query.get(id)
        
        if not autorizacion:
            return jsonify({
                'success': False,
                'message': 'Autorización no encontrada'
            }), 404
        
        # Verificar que sea de la sede del operador
        if current_user.rol == 'usuario_operador':
            if autorizacion.sede_id != current_user.sede_id:
                return jsonify({
                    'success': False,
                    'message': 'Esta autorización no pertenece a tu sede'
                }), 403
        
        # Verificar estado
        if autorizacion.estado != 'PENDIENTE':
            return jsonify({
                'success': False,
                'message': f'Esta autorización está {autorizacion.estado} y no puede ser aplicada'
            }), 400
        
        # Verificar vencimiento
        autorizacion.verificar_vencimiento()
        db.session.commit()
        
        if autorizacion.estado == 'VENCIDA':
            return jsonify({
                'success': False,
                'message': 'Esta autorización ha vencido'
            }), 400
        
        # Retornar datos de la autorización
        return jsonify({
            'success': True,
            'message': 'Autorización válida',
            'autorizacion': autorizacion.to_dict(incluir_usuario=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al aplicar autorización: {str(e)}'
        }), 500


@bp.route('/estadisticas', methods=['GET'])
@login_required
@role_required('usuario_master')
def obtener_estadisticas():
    """Obtiene estadísticas de autorizaciones (solo master)"""
    try:
        sede_id = request.args.get('sede_id', None)
        
        # Query base
        query = AutorizacionIngreso.query
        
        if sede_id:
            query = query.filter_by(sede_id=int(sede_id))
        
        # Verificar vencimientos
        pendientes = query.filter_by(estado='PENDIENTE').all()
        for auth in pendientes:
            auth.verificar_vencimiento()
        db.session.commit()
        
        # Contar por estado
        total = query.count()
        pendientes = query.filter_by(estado='PENDIENTE').count()
        utilizadas = query.filter_by(estado='UTILIZADA').count()
        vencidas = query.filter_by(estado='VENCIDA').count()
        canceladas = query.filter_by(estado='CANCELADA').count()
        
        # Próximas a vencer (menos de 2 días)
        fecha_limite = (datetime.now() + timedelta(days=2)).date()
        proximas_vencer = query.filter(
            AutorizacionIngreso.estado == 'PENDIENTE',
            AutorizacionIngreso.fecha_vencimiento <= fecha_limite,
            AutorizacionIngreso.fecha_vencimiento > datetime.now().date()
        ).count()
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total': total,
                'pendientes': pendientes,
                'utilizadas': utilizadas,
                'vencidas': vencidas,
                'canceladas': canceladas,
                'proximas_vencer': proximas_vencer
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500
