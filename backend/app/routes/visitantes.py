"""
========================================
RUTAS: VISITANTES
Gestión completa de visitantes y sus visitas
========================================
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Visitante, LogVisitante, LogEvento, Dependencia, AutorizacionIngreso
from app.routes.auth import role_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('visitantes', __name__, url_prefix='/api/visitantes')


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/buscar', methods=['GET'])
@login_required
def buscar_visitante():
    """Busca un visitante por tipo y número de identificación"""
    try:
        tipo_id = request.args.get('tipo_identificacion', '').upper()
        num_id = request.args.get('num_identificacion', '').upper()
        
        if not tipo_id or not num_id:
            return jsonify({
                'success': False,
                'message': 'Tipo y número de identificación son requeridos'
            }), 400
        
        visitante = Visitante.query.filter_by(
            tipo_identificacion=tipo_id,
            num_identificacion=num_id
        ).first()
        
        if visitante:
            return jsonify({
                'success': True,
                'encontrado': True,
                'visitante': visitante.to_dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'encontrado': False,
                'message': 'Visitante no encontrado'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/buscar-por-nit', methods=['GET'])
@login_required
def buscar_por_nit():
    """Busca el nombre de empresa por NIT en la base de datos de visitantes"""
    try:
        nit = request.args.get('nit', '').upper().strip()
        
        if not nit or len(nit) < 3:
            return jsonify({
                'success': False,
                'message': 'NIT inválido'
            }), 400
        
        # Buscar el visitante más reciente con ese NIT
        visitante = Visitante.query.filter_by(
            nit_empresa=nit
        ).order_by(Visitante.fecha_creacion.desc()).first()
        
        if visitante:
            return jsonify({
                'success': True,
                'empresa': visitante.empresa,
                'nit': visitante.nit_empresa
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'NIT no encontrado'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/registrar', methods=['POST'])
@login_required
def registrar_visitante():
    """Registra un nuevo visitante en la base de datos"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = [
            'tipo_identificacion', 'num_identificacion', 'primer_nombre',
            'primer_apellido', 'num_telefono', 'dir_correo', 'empresa', 'nit_empresa'
        ]
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Verificar si ya existe
        existe = Visitante.query.filter_by(
            tipo_identificacion=data['tipo_identificacion'].upper(),
            num_identificacion=data['num_identificacion'].upper()
        ).first()
        
        if existe:
            return jsonify({
                'success': False,
                'message': 'El visitante ya está registrado'
            }), 409
        
        # Crear visitante
        visitante = Visitante(
            tipo_identificacion=data['tipo_identificacion'].upper(),
            num_identificacion=data['num_identificacion'].upper(),
            primer_nombre=data['primer_nombre'].upper(),
            segundo_nombre=data.get('segundo_nombre', '').upper(),
            primer_apellido=data['primer_apellido'].upper(),
            segundo_apellido=data.get('segundo_apellido', '').upper(),
            num_telefono=data['num_telefono'].upper(),
            dir_correo=data['dir_correo'].lower(),
            empresa=data['empresa'].upper(),
            nit_empresa=data['nit_empresa'].upper(),
            estado='ACTIVO'
        )
        
        db.session.add(visitante)
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='VISITANTE_REGISTRADO',
            descripcion=f'Visitante registrado: {visitante.num_identificacion} - {visitante.primer_nombre} {visitante.primer_apellido}',
            usuario=current_user,
            datos_adicionales={'visitante_id': visitante.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Visitante registrado exitosamente',
            'visitante': visitante.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/ingreso', methods=['POST'])
@login_required
def registrar_ingreso():
    """Registra el ingreso de un visitante"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = [
            'tipo_identificacion', 'num_identificacion', 'prefijo_dependencia',
            'funcionario_recibe', 'funcionario_autoriza'  # NUEVO: funcionario_autoriza es requerido
        ]
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Buscar visitante
        visitante = Visitante.query.filter_by(
            tipo_identificacion=data['tipo_identificacion'].upper(),
            num_identificacion=data['num_identificacion'].upper()
        ).first()
        
        if not visitante:
            return jsonify({
                'success': False,
                'message': 'Visitante no encontrado. Por favor regístrelo primero.'
            }), 404
        
        # Buscar dependencia
        dependencia = Dependencia.query.filter_by(
            prefijo_dependencia=data['prefijo_dependencia'].upper()
        ).first()
        
        if not dependencia:
            return jsonify({
                'success': False,
                'message': 'Dependencia no encontrada'
            }), 404
        
        # Verificar acceso a la sede
        if not current_user.tiene_acceso_sede(current_user.sede_id):
            return jsonify({
                'success': False,
                'message': 'No tiene acceso a esta sede'
            }), 403
        
        # Crear log de ingreso
        ahora = datetime.now()
        log = LogVisitante(
            fecha_ingreso=ahora.date(),
            hora_ingreso=ahora.time(),
            tipo_identificacion=visitante.tipo_identificacion,
            num_identificacion=visitante.num_identificacion,
            primer_nombre=visitante.primer_nombre,
            segundo_nombre=visitante.segundo_nombre,
            primer_apellido=visitante.primer_apellido,
            segundo_apellido=visitante.segundo_apellido,
            num_telefono=visitante.num_telefono,
            dir_correo=visitante.dir_correo,
            empresa=data.get('empresa', visitante.empresa).upper(),
            nit_empresa=data.get('nit_empresa', visitante.nit_empresa).upper(),
            prefijo_dependencia=dependencia.prefijo_dependencia,
            descripcion_dependencia=dependencia.descripcion_dependencia,
            funcionario_recibe=data['funcionario_recibe'].upper(),
            funcionario_autoriza=data['funcionario_autoriza'].upper(),  # NUEVO campo
            observaciones1=data.get('observaciones1', '').upper(),
            # Campos antiguos check (mantener por compatibilidad)
            check1_elemento_tecnologico=data.get('check1_elemento_tecnologico', False),
            check1_descripcion=data.get('check1_descripcion', '').upper(),
            check2_arma_fuego=data.get('check2_arma_fuego', False),
            check2_descripcion=data.get('check2_descripcion', '').upper(),
            check3_otro_elemento=data.get('check3_otro_elemento', False),
            check3_descripcion=data.get('check3_descripcion', '').upper(),
            check4_herramienta=data.get('check4_herramienta', False),
            check4_descripcion=data.get('check4_descripcion', '').upper(),
            check5_adicional=data.get('check5_adicional', False),
            check5_descripcion=data.get('check5_descripcion', '').upper(),
            # Nuevos campos simplificados
            ingresa_elementos=data.get('ingresa_elementos', False),
            elementos_observacion=data.get('elementos_observacion', '').upper(),
            elemento_portatil=data.get('elemento_portatil', False),
            elemento_celular=data.get('elemento_celular', False),
            elemento_herramientas=data.get('elemento_herramientas', False),
            elemento_otros=data.get('elemento_otros', False),
            numero_visitantes=data.get('numero_visitantes', 1),
            visitantes_adicionales=data.get('visitantes_adicionales', '').upper(),
            numero_carnet=data.get('numero_carnet', '').upper(),
            estado_visita='EN_INSTALACIONES',
            sede_id=current_user.sede_id,
            usuario_registro_id=current_user.id,
            autorizacion_previa_id=data.get('autorizacion_previa_id', None)  # NUEVO: ID de autorización si se usó
        )
        
        db.session.add(log)
        db.session.flush()  # Para obtener el ID del log antes de commit
        
        # NUEVO: Si se usó una autorización previa, marcarla como utilizada
        if data.get('autorizacion_previa_id'):
            autorizacion = AutorizacionIngreso.query.get(data['autorizacion_previa_id'])
            if autorizacion:
                autorizacion.marcar_como_utilizada(log.id)
        
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='VISITANTE_INGRESO',
            descripcion=f'Ingreso registrado: {visitante.num_identificacion} - {visitante.primer_nombre} {visitante.primer_apellido}',
            usuario=current_user,
            datos_adicionales={'log_id': log.id, 'visitante_id': visitante.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Ingreso registrado exitosamente',
            'log': log.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/salida/<int:log_id>', methods=['PUT'])
@login_required
def registrar_salida(log_id):
    """Registra la salida de un visitante"""
    try:
        log = LogVisitante.query.get(log_id)
        
        if not log:
            return jsonify({
                'success': False,
                'message': 'Registro no encontrado'
            }), 404
        
        # Validar acceso por sede (operadores solo su sede)
        if current_user.rol == 'usuario_operador' and log.sede_id != current_user.sede_id:
            return jsonify({
                'success': False,
                'message': 'No tiene acceso a este registro (sede diferente)'
            }), 403
        
        if log.estado_visita == 'SALIO':
            return jsonify({
                'success': False,
                'message': 'El visitante ya registró su salida'
            }), 400
        
        # Marcar salida
        log.marcar_salida()
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='VISITANTE_SALIDA',
            descripcion=f'Salida registrada: {log.num_identificacion} - {log.get_nombre_completo()}',
            usuario=current_user,
            datos_adicionales={'log_id': log.id},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Salida registrada exitosamente',
            'log': log.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/listar', methods=['GET'])
@login_required
def listar_visitas():
    """Lista las visitas registradas con filtros y paginación"""
    try:
        sede_id = request.args.get('sede_id', type=int)
        fecha_desde = request.args.get('fecha_desde')  # Formato: YYYY-MM-DD
        fecha_hasta = request.args.get('fecha_hasta')  # Formato: YYYY-MM-DD
        estado = request.args.get('estado')  # EN_INSTALACIONES o SALIO
        busqueda = request.args.get('busqueda')  # Búsqueda por identificación
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 100, type=int)
        
        # Base query
        query = LogVisitante.query
        
        # Filtrar por sede según rol
        if current_user.rol == 'usuario_operador':
            query = query.filter_by(sede_id=current_user.sede_id)
        elif sede_id:
            query = query.filter_by(sede_id=sede_id)
        
        # Filtrar por rango de fechas
        if fecha_desde and fecha_hasta:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            query = query.filter(
                LogVisitante.fecha_ingreso >= fecha_desde_obj,
                LogVisitante.fecha_ingreso <= fecha_hasta_obj
            )
        elif fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            query = query.filter_by(fecha_ingreso=fecha_desde_obj)
        else:
            # Por defecto, visitas del día actual
            query = query.filter_by(fecha_ingreso=datetime.now().date())
        
        # Filtrar por estado
        if estado:
            query = query.filter_by(estado_visita=estado)
        
        # Búsqueda por identificación
        if busqueda:
            query = query.filter(
                db.or_(
                    LogVisitante.num_identificacion.ilike(f'%{busqueda}%'),
                    LogVisitante.primer_nombre.ilike(f'%{busqueda}%'),
                    LogVisitante.primer_apellido.ilike(f'%{busqueda}%')
                )
            )
        
        # Contar total antes de paginar
        total = query.count()
        
        # Ordenar: 1) EN_INSTALACIONES primero, SALIO al final
        #          2) Dentro de cada estado: más antiguos arriba, más recientes abajo
        query = query.order_by(
            LogVisitante.estado_visita.asc(),    # EN_INSTALACIONES primero
            LogVisitante.fecha_ingreso.asc(),    # Más antiguos arriba
            LogVisitante.hora_ingreso.asc()      # Más antiguos arriba
        )
        
        # Paginación
        visitas_paginadas = query.paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'total': total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'total_paginas': visitas_paginadas.pages,
            'visitas': [v.to_dict() for v in visitas_paginadas.items]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@bp.route('/foto/<int:log_id>', methods=['POST'])
@login_required
def guardar_foto(log_id):
    """Guarda la fotografía de un visitante"""
    try:
        # Verificar que se envió un archivo
        if 'foto' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No se envió ninguna foto'
            }), 400
        
        file = request.files['foto']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No se seleccionó ningún archivo'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Formato de archivo no permitido'
            }), 400
        
        # Buscar log
        log = LogVisitante.query.get(log_id)
        
        if not log:
            return jsonify({
                'success': False,
                'message': 'Registro no encontrado'
            }), 404
        
        # Validar acceso por sede (operadores solo su sede)
        if current_user.rol == 'usuario_operador' and log.sede_id != current_user.sede_id:
            return jsonify({
                'success': False,
                'message': 'No tiene acceso a este registro (sede diferente)'
            }), 403
        
        # Crear nombre de archivo según estructura:
        # [TIPO_ID]-[NUM_ID]-[FECHA]_[HORA].jpg
        # Ejemplo: CC-12345678-06032026_143052.jpg
        fecha_str = log.fecha_ingreso.strftime('%d%m%Y')  # DDMMYYYY
        hora_str = log.hora_ingreso.strftime('%H%M%S')    # HHMMSS
        filename = f"{log.tipo_identificacion}-{log.num_identificacion}-{fecha_str}_{hora_str}.jpg"
        filename = secure_filename(filename)
        
        # Obtener ruta de uploads desde configuración
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Guardar archivo
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Actualizar log
        log.fotografia_visitante = filepath
        db.session.commit()
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='FOTO_CAPTURADA',
            descripcion=f'Fotografía capturada: {log.num_identificacion}',
            usuario=current_user,
            datos_adicionales={'log_id': log.id, 'filename': filename},
            nivel='INFO'
        )
        
        return jsonify({
            'success': True,
            'message': 'Foto guardada exitosamente',
            'ruta': filepath
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
