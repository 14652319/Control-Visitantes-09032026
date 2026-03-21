"""
========================================
RUTAS: MÓDULO SST (Seguridad y Salud en el Trabajo)
Gestión completa de contratistas, planillas y autorizaciones SST
========================================
"""
import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.routes.auth import role_required
from app.utils.logger import logger

bp = Blueprint('sst', __name__, url_prefix='/api/sst')

# Roles con acceso al módulo SST
ROLES_SST = ['usuario_master', 'admin_sst', 'operador_seguridad']
ROLES_ADMIN_SST = ['usuario_master', 'admin_sst']


# ============================================================
# ENDPOINT: GET /api/sst/operadores
# Catálogo de operadores de aportes (EPS/AFP/ARL)
# Acceso: Cualquier usuario autenticado con rol SST
# ============================================================
@bp.route('/operadores', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_operadores():
    """Lista operadores de aportes (EPS, AFP, ARL) — catálogo de referencia"""
    try:
        from app.models.operador_aportes import OperadorAportes
        
        tipo = request.args.get('tipo')  # EPS | AFP | ARL
        
        query = OperadorAportes.query.filter_by(activo=True)
        if tipo and tipo.upper() in ('EPS', 'AFP', 'ARL'):
            query = query.filter_by(tipo=tipo.upper())
        
        operadores = query.order_by(OperadorAportes.tipo, OperadorAportes.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [op.to_dict() for op in operadores],
            'total': len(operadores)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando operadores SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# ENDPOINT: GET /api/sst/health
# Health check del módulo SST
# ============================================================
@bp.route('/health', methods=['GET'])
@login_required
def health():
    """Verifica que el módulo SST está activo"""
    return jsonify({'success': True, 'message': 'Módulo SST activo', 'version': '3.2'}), 200


# ============================================================
# HELPERS: Validaciones de negocio
# ============================================================
def validar_empresa(data, es_actualizacion=False):
    """
    Valida datos de empresa según tipo_persona.
    
    Args:
        data (dict): Datos de la empresa
        es_actualizacion (bool): True si es PUT, False si es POST
    
    Returns:
        tuple: (es_valido: bool, mensaje_error: str|None)
    """
    tipo = data.get('tipo_persona', '').upper()
    
    if tipo == 'JURIDICA':
        if not data.get('nit'):
            return False, "Persona Jurídica requiere NIT"
        if not data.get('razon_social'):
            return False, "Persona Jurídica requiere razón social"
        if not es_actualizacion:
            if not data.get('digito_verificacion'):
                return False, "Persona Jurídica requiere dígito de verificación"
            if not data.get('representante_legal'):
                return False, "Persona Jurídica requiere representante legal"
    elif tipo == 'NATURAL':
        if not data.get('tipo_identificacion'):
            return False, "Persona Natural requiere tipo de identificación"
        if not data.get('num_identificacion'):
            return False, "Persona Natural requiere número de identificación"
        if not data.get('primer_nombre'):
            return False, "Persona Natural requiere primer nombre"
        if not data.get('primer_apellido'):
            return False, "Persona Natural requiere primer apellido"
    else:
        return False, "tipo_persona debe ser 'JURIDICA' o 'NATURAL'"
    
    return True, None


# ============================================================
# ENDPOINTS: CRUD EMPRESAS CONTRATISTAS
# ============================================================

@bp.route('/empresas', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_empresas():
    """Lista empresas contratistas con filtros opcionales"""
    try:
        from app.models.empresa_contratista import EmpresaContratista
        
        # Filtros opcionales
        tipo_persona = request.args.get('tipo_persona')  # JURIDICA | NATURAL
        estado = request.args.get('estado')  # activa | inactiva
        busqueda = request.args.get('busqueda')  # Búsqueda por nombre, razón social, NIT, o documento
        
        query = EmpresaContratista.query
        
        if tipo_persona and tipo_persona.upper() in ('JURIDICA', 'NATURAL'):
            query = query.filter_by(tipo_persona=tipo_persona.upper())
        
        if estado and estado.lower() in ('activa', 'inactiva'):
            query = query.filter_by(estado=estado.lower())
        
        if busqueda:
            # Búsqueda flexible por múltiples campos
            busqueda_patron = f'%{busqueda}%'
            query = query.filter(
                db.or_(
                    EmpresaContratista.razon_social.ilike(busqueda_patron),
                    EmpresaContratista.nit.ilike(busqueda_patron),
                    EmpresaContratista.num_identificacion.ilike(busqueda_patron),
                    EmpresaContratista.primer_nombre.ilike(busqueda_patron),
                    EmpresaContratista.primer_apellido.ilike(busqueda_patron)
                )
            )
        
        empresas = query.order_by(
            EmpresaContratista.tipo_persona,
            db.func.coalesce(EmpresaContratista.razon_social, EmpresaContratista.primer_nombre)
        ).all()
        
        return jsonify({
            'success': True,
            'data': [emp.to_dict() for emp in empresas],
            'total': len(empresas)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando empresas SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empresas', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def crear_empresa():
    """Crea una nueva empresa contratista (Jurídica o Natural)"""
    try:
        from app.models.empresa_contratista import EmpresaContratista
        
        data = request.get_json()
        
        # Validación de negocio
        es_valido, error = validar_empresa(data)
        if not es_valido:
            return jsonify({'success': False, 'message': error}), 400
        
        # Normalizar tipo_persona
        data['tipo_persona'] = data['tipo_persona'].upper()
        
        # Verificar duplicados
        tipo = data['tipo_persona']
        if tipo == 'JURIDICA' and data.get('nit'):
            existe = EmpresaContratista.query.filter_by(nit=data['nit']).first()
            if existe:
                return jsonify({
                    'success': False,
                    'message': f'Ya existe una empresa con NIT {data["nit"]}'
                }), 409
        elif tipo == 'NATURAL' and data.get('num_identificacion'):
            existe = EmpresaContratista.query.filter_by(
                tipo_identificacion=data.get('tipo_identificacion'),
                num_identificacion=data['num_identificacion']
            ).first()
            if existe:
                return jsonify({
                    'success': False,
                    'message': f'Ya existe una persona con ese documento'
                }), 409
        
        # Crear empresa
        empresa = EmpresaContratista(**data)
        db.session.add(empresa)
        db.session.commit()
        
        logger.info(f"Empresa creada: {empresa.id} por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': empresa.to_dict(),
            'message': 'Empresa registrada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando empresa SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empresas/<int:id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_empresa(id):
    """Obtiene detalle de una empresa contratista"""
    try:
        from app.models.empresa_contratista import EmpresaContratista
        
        empresa = EmpresaContratista.query.get(id)
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': empresa.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo empresa {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empresas/<int:id>', methods=['PUT'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def actualizar_empresa(id):
    """Actualiza una empresa contratista existente"""
    try:
        from app.models.empresa_contratista import EmpresaContratista
        
        empresa = EmpresaContratista.query.get(id)
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404
        
        data = request.get_json()
        
        # Validación de negocio
        es_valido, error = validar_empresa(data, es_actualizacion=True)
        if not es_valido:
            return jsonify({'success': False, 'message': error}), 400
        
        # Normalizar tipo_persona
        if 'tipo_persona' in data:
            data['tipo_persona'] = data['tipo_persona'].upper()
        
        # Actualizar campos permitidos
        campos_actualizables = [
            'tipo_persona', 'nit', 'razon_social', 'tipo_identificacion',
            'num_identificacion', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'telefono', 'email',
            'direccion', 'ciudad', 'estado', 'digito_verificacion', 'representante_legal'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                setattr(empresa, campo, data[campo])
        
        db.session.commit()
        
        logger.info(f"Empresa {id} actualizada por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': empresa.to_dict(),
            'message': 'Empresa actualizada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando empresa {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empresas/buscar', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def buscar_empresa():
    """
    Búsqueda inteligente por tipo + número de documento en todas las tablas.
    Busca en: EmpresaContratista → Visitante → AutorizacionIngreso.

    Query params:
        q       (str): NIT o número de documento
        tipo_id (str): Tipo de documento (CC, CE, NIT, etc.) — mejora la precisión

    Returns:
        {'encontrado': bool, 'fuente': 'contratista'|'visitante'|'autorizacion_ingreso'|None, 'data': {...}|None}
    """
    try:
        from app.models.empresa_contratista import EmpresaContratista
        from app.models.visitante import Visitante
        from app.models.autorizacion_ingreso import AutorizacionIngreso

        consulta = request.args.get('q', '').strip()
        tipo_id = request.args.get('tipo_id', '').strip()

        logger.info(f"[buscar_empresa] q='{consulta}' tipo_id='{tipo_id}'")

        if not consulta:
            return jsonify({'success': False, 'message': 'Parámetro "q" requerido'}), 400

        # Filtra por (tipo == tipo_id AND num == consulta) si hay tipo_id, o solo por num
        def con_tipo(col_tipo, col_num):
            if tipo_id:
                return db.and_(col_tipo == tipo_id, col_num == consulta)
            return col_num == consulta

        # 1) Buscar en EmpresaContratista por NIT o tipo+num_identificacion
        empresa = EmpresaContratista.query.filter(
            db.or_(
                EmpresaContratista.nit == consulta,
                con_tipo(EmpresaContratista.tipo_identificacion, EmpresaContratista.num_identificacion)
            )
        ).first()

        if empresa:
            logger.info(f"[buscar_empresa] ENCONTRADO en EmpresaContratista id={empresa.id}")
            return jsonify({
                'success': True,
                'encontrado': True,
                'fuente': 'contratista',
                'data': empresa.to_dict()
            }), 200

        # 2) Buscar en Visitantes por tipo+num_identificacion
        #    NUNCA para búsquedas por NIT: el NIT es un identificador empresarial
        #    y podría coincidir con el num_identificacion de un visitante registrado
        #    con tipo='NIT', devolviendo erróneamente datos de persona natural.
        if tipo_id != 'NIT':
            visitante = Visitante.query.filter(
                con_tipo(Visitante.tipo_identificacion, Visitante.num_identificacion)
            ).first()

            if visitante:
                data = visitante.to_dict()
                data['tipo_persona'] = 'NATURAL'
                data['nombre_completo_persona_natural'] = data.get('nombre_completo', '')
                data['id'] = None
                return jsonify({
                    'success': True,
                    'encontrado': True,
                    'fuente': 'visitante',
                    'data': data
                }), 200

        # 3) Buscar en AutorizacionIngreso (sistema anterior) — SOLO para personas naturales
        #    Para NIT (JURIDICA) NO se usa esta tabla: el campo 'empresa' en autorizaciones
        #    es texto libre histórico donde operators ponían nombres de personas en lugar del
        #    nombre real de la empresa, causando datos erróneos. Si el NIT no está en
        #    empresas_contratistas, se debe crear la empresa desde cero.
        if tipo_id != 'NIT':
            auth = AutorizacionIngreso.query.filter(
                db.or_(
                    AutorizacionIngreso.nit_empresa == consulta,
                    con_tipo(AutorizacionIngreso.tipo_identificacion, AutorizacionIngreso.num_identificacion)
                )
            ).order_by(AutorizacionIngreso.id.desc()).first()

            if auth:
                logger.info(f"[buscar_empresa] ENCONTRADO en AutorizacionIngreso id={auth.id}")
                data = {
                    'id': None,
                    'tipo_persona': 'NATURAL',
                    'tipo_identificacion': auth.tipo_identificacion,
                    'num_identificacion': auth.num_identificacion,
                    'primer_nombre': auth.primer_nombre or '',
                    'segundo_nombre': auth.segundo_nombre or '',
                    'primer_apellido': auth.primer_apellido or '',
                    'segundo_apellido': auth.segundo_apellido or '',
                    'nombre_completo_persona_natural': ' '.join(filter(None, [
                        auth.primer_nombre, auth.segundo_nombre,
                        auth.primer_apellido, auth.segundo_apellido
                    ])),
                    'empresa': auth.empresa or '',
                    'nit': auth.nit_empresa or '',
                    'telefono': auth.num_telefono or '',
                    'email': auth.dir_correo or '',
                }
                return jsonify({
                    'success': True,
                    'encontrado': True,
                    'fuente': 'autorizacion_ingreso',
                    'data': data
                }), 200

        logger.info(f"[buscar_empresa] NO ENCONTRADO para q='{consulta}'")
        return jsonify({'success': True, 'encontrado': False, 'fuente': None, 'data': None}), 200

    except Exception as e:
        logger.error(f"Error buscando empresa: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# HELPERS: Certificados
# ============================================================
def estado_vigencia(fecha_vencimiento):
    """
    Retorna estado de vigencia del certificado.
    
    Args:
        fecha_vencimiento (date): Fecha de vencimiento del certificado
    
    Returns:
        str: 'VENCIDO' | 'PROXIMO_VENCER' | 'VIGENTE'
    """
    from datetime import date, timedelta
    
    hoy = date.today()
    if fecha_vencimiento < hoy:
        return 'VENCIDO'
    elif fecha_vencimiento <= hoy + timedelta(days=30):
        return 'PROXIMO_VENCER'  # Alerta visual en frontend (próximos 30 días)
    return 'VIGENTE'


# ============================================================
# ENDPOINTS: CRUD EMPLEADOS CONTRATISTAS
# ============================================================

@bp.route('/empleados', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_empleados():
    """Lista empleados contratistas con filtros opcionales"""
    try:
        from app.models.empleado_contratista import EmpleadoContratista
        
        empresa_id = request.args.get('empresa_id', type=int)
        estado = request.args.get('estado')  # activo | inactivo
        
        query = EmpleadoContratista.query
        
        if empresa_id:
            query = query.filter_by(empresa_id=empresa_id)
        
        if estado and estado.lower() in ('activo', 'inactivo'):
            query = query.filter_by(estado=estado.lower())
        
        empleados = query.order_by(
            EmpleadoContratista.apellidos,
            EmpleadoContratista.nombres
        ).all()
        
        return jsonify({
            'success': True,
            'data': [emp.to_dict() for emp in empleados],
            'total': len(empleados)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando empleados SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empleados', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def crear_empleado():
    """Crea un nuevo empleado contratista"""
    try:
        from app.models.empleado_contratista import EmpleadoContratista
        from app.models.empresa_contratista import EmpresaContratista
        
        data = request.get_json()
        
        # Validaciones
        if not data.get('empresa_id'):
            return jsonify({'success': False, 'message': 'empresa_id requerido'}), 400
        
        if not data.get('tipo_id') or not data.get('num_id'):
            return jsonify({'success': False, 'message': 'Documento de identificación requerido'}), 400
        
        if not data.get('nombres') or not data.get('apellidos'):
            return jsonify({'success': False, 'message': 'Nombre y apellido requeridos'}), 400
        
        # Verificar que empresa existe
        empresa = EmpresaContratista.query.get(data['empresa_id'])
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404
        
        # Verificar duplicado
        existe = EmpleadoContratista.query.filter_by(
            tipo_id=data['tipo_id'],
            num_id=data['num_id']
        ).first()
        
        if existe:
            return jsonify({
                'success': False,
                'message': f'Ya existe un empleado con ese documento en empresa {existe.empresa_id}'
            }), 409
        
        # Crear empleado
        empleado = EmpleadoContratista(**data)
        db.session.add(empleado)
        db.session.commit()
        
        logger.info(f"Empleado contratista creado: {empleado.id} por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': empleado.to_dict(),
            'message': 'Empleado registrado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando empleado SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empleados/<int:id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_empleado(id):
    """Obtiene detalle de un empleado + certificados vigentes"""
    try:
        from app.models.empleado_contratista import EmpleadoContratista
        from app.models.certificado_trabajo import CertificadoTrabajo
        from datetime import date
        
        empleado = EmpleadoContratista.query.get(id)
        if not empleado:
            return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
        
        # Obtener certificados vigentes
        certificados_vigentes = CertificadoTrabajo.query.filter(
            CertificadoTrabajo.empleado_id == id,
            CertificadoTrabajo.fecha_vencimiento >= date.today()
        ).all()
        
        data = empleado.to_dict()
        data['certificados_vigentes'] = [cert.to_dict() for cert in certificados_vigentes]
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo empleado {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empleados/<int:id>', methods=['PUT'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def actualizar_empleado(id):
    """Actualiza un empleado contratista"""
    try:
        from app.models.empleado_contratista import EmpleadoContratista
        
        empleado = EmpleadoContratista.query.get(id)
        if not empleado:
            return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
        
        data = request.get_json()
        
        # Campos actualizables
        campos_actualizables = [
            'empresa_id', 'tipo_id', 'num_id',
            'nombres', 'apellidos', 'cargo',
            'eps_id', 'afp_id', 'arl_id', 'estado'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                setattr(empleado, campo, data[campo])
        
        db.session.commit()
        
        logger.info(f"Empleado {id} actualizado por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': empleado.to_dict(),
            'message': 'Empleado actualizado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando empleado {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/empleados/buscar', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def buscar_empleado():
    """
    Búsqueda inteligente de empleado por tipo + número de documento.
    Si no se encuentra en EmpleadoContratista, busca en la tabla de Visitantes.

    Query params:
        tipo (str): Tipo de documento (CC, TI, CE, etc)
        num (str): Número de documento

    Returns:
        {'encontrado': bool, 'fuente': 'empleado'|'visitante'|None, 'data': {...}|None}
    """
    try:
        from app.models.empleado_contratista import EmpleadoContratista
        from app.models.certificado_trabajo import CertificadoTrabajo
        from app.models.visitante import Visitante
        from datetime import date

        tipo_doc = request.args.get('tipo', '').strip().upper()
        num_doc = request.args.get('num', '').strip()

        if not tipo_doc or not num_doc:
            return jsonify({'success': False, 'message': 'Parámetros "tipo" y "num" requeridos'}), 400

        # 1) Buscar en EmpleadoContratista
        empleado = EmpleadoContratista.query.filter_by(
            tipo_id=tipo_doc,
            num_id=num_doc
        ).first()

        if empleado:
            certificados_vigentes = CertificadoTrabajo.query.filter(
                CertificadoTrabajo.empleado_id == empleado.id,
                CertificadoTrabajo.fecha_vencimiento >= date.today()
            ).all()

            data = empleado.to_dict()
            data['certificados_vigentes'] = [cert.to_dict() for cert in certificados_vigentes]
            if empleado.empresa:
                data['empresa'] = empleado.empresa.to_dict()

            return jsonify({'success': True, 'encontrado': True, 'fuente': 'empleado', 'data': data}), 200

        # 2) Si no está en SST, buscar en la tabla de visitantes
        visitante = Visitante.query.filter_by(
            num_identificacion=num_doc
        ).first()

        if visitante:
            data = visitante.to_dict()
            # Adaptar campos al formato de EmpleadoContratista para el frontend
            data['id'] = None
            data['tipo_id'] = visitante.tipo_identificacion
            data['num_id'] = visitante.num_identificacion
            nombres = (visitante.primer_nombre or '').strip()
            if visitante.segundo_nombre:
                nombres += ' ' + visitante.segundo_nombre.strip()
            data['nombres'] = nombres
            apellidos = (visitante.primer_apellido or '').strip()
            if visitante.segundo_apellido:
                apellidos += ' ' + visitante.segundo_apellido.strip()
            data['apellidos'] = apellidos
            data['certificados_vigentes'] = []
            return jsonify({'success': True, 'encontrado': True, 'fuente': 'visitante', 'data': data}), 200

        return jsonify({'success': True, 'encontrado': False, 'fuente': None, 'data': None}), 200

    except Exception as e:
        logger.error(f"Error buscando empleado: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# ENDPOINTS: CRUD CERTIFICADOS DE TRABAJO
# ============================================================

@bp.route('/certificados', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_certificados():
    """Lista certificados de trabajo con filtros opcionales"""
    try:
        from app.models.certificado_trabajo import CertificadoTrabajo
        from datetime import date
        
        empleado_id = request.args.get('empleado_id', type=int)
        tipo = request.args.get('tipo')  # ALTURAS | ELECTRICO | etc
        vigente = request.args.get('vigente')  # true | false
        
        query = CertificadoTrabajo.query
        
        if empleado_id:
            query = query.filter_by(empleado_id=empleado_id)
        
        if tipo and tipo.upper() in ('ALTURAS', 'ELECTRICO', 'ESPACIOS_CONFINADOS', 'MANEJO_QUIMICOS', 'PRIMEROS_AUXILIOS', 'OTRO'):
            query = query.filter_by(tipo_certificado=tipo.upper())
        
        if vigente and vigente.lower() == 'true':
            query = query.filter(CertificadoTrabajo.fecha_vencimiento >= date.today())
        elif vigente and vigente.lower() == 'false':
            query = query.filter(CertificadoTrabajo.fecha_vencimiento < date.today())
        
        certificados = query.order_by(CertificadoTrabajo.fecha_vencimiento.desc()).all()
        
        # Agregar estado de vigencia a cada certificado
        data = []
        for cert in certificados:
            cert_dict = cert.to_dict()
            cert_dict['estado_vigencia'] = estado_vigencia(cert.fecha_vencimiento)
            data.append(cert_dict)
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando certificados SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/certificados', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def crear_certificado():
    """Registra un nuevo certificado de trabajo para un empleado"""
    try:
        from app.models.certificado_trabajo import CertificadoTrabajo
        from app.models.empleado_contratista import EmpleadoContratista
        
        data = request.get_json()
        
        # Validaciones
        if not data.get('empleado_id'):
            return jsonify({'success': False, 'message': 'empleado_id requerido'}), 400
        
        if not data.get('tipo_certificado'):
            return jsonify({'success': False, 'message': 'tipo_certificado requerido'}), 400
        
        if not data.get('fecha_expedicion') or not data.get('fecha_vencimiento'):
            return jsonify({'success': False, 'message': 'Fechas de expedición y vencimiento requeridas'}), 400
        
        # Verificar que empleado existe
        empleado = EmpleadoContratista.query.get(data['empleado_id'])
        if not empleado:
            return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
        
        # Crear certificado
        certificado = CertificadoTrabajo(**data)
        db.session.add(certificado)
        db.session.commit()
        
        logger.info(f"Certificado creado: {certificado.id} para empleado {empleado.id} por usuario {current_user.id}")
        
        cert_dict = certificado.to_dict()
        cert_dict['estado_vigencia'] = estado_vigencia(certificado.fecha_vencimiento)
        
        return jsonify({
            'success': True,
            'data': cert_dict,
            'message': 'Certificado registrado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando certificado SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/certificados/empleado/<int:empleado_id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_certificados_empleado(empleado_id):
    """Obtiene todos los certificados de un empleado"""
    try:
        from app.models.certificado_trabajo import CertificadoTrabajo
        from app.models.empleado_contratista import EmpleadoContratista
        
        empleado = EmpleadoContratista.query.get(empleado_id)
        if not empleado:
            return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
        
        certificados = CertificadoTrabajo.query.filter_by(empleado_id=empleado_id).order_by(
            CertificadoTrabajo.fecha_vencimiento.desc()
        ).all()
        
        # Agregar estado de vigencia
        data = []
        for cert in certificados:
            cert_dict = cert.to_dict()
            cert_dict['estado_vigencia'] = estado_vigencia(cert.fecha_vencimiento)
            data.append(cert_dict)
        
        return jsonify({
            'success': True,
            'data': data,
            'empleado': empleado.to_dict(),
            'total': len(data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo certificados de empleado {empleado_id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/certificados/<int:id>', methods=['PUT'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def actualizar_certificado(id):
    """Actualiza un certificado de trabajo"""
    try:
        from app.models.certificado_trabajo import CertificadoTrabajo
        
        certificado = CertificadoTrabajo.query.get(id)
        if not certificado:
            return jsonify({'success': False, 'message': 'Certificado no encontrado'}), 404
        
        data = request.get_json()
        
        # Campos actualizables
        campos_actualizables = [
            'tipo_certificado', 'nombre_certificado',
            'fecha_expedicion', 'fecha_vencimiento',
            'archivo_nombre', 'archivo_ruta', 'verificado'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                setattr(certificado, campo, data[campo])
        
        db.session.commit()
        
        logger.info(f"Certificado {id} actualizado por usuario {current_user.id}")
        
        cert_dict = certificado.to_dict()
        cert_dict['estado_vigencia'] = estado_vigencia(certificado.fecha_vencimiento)
        
        return jsonify({
            'success': True,
            'data': cert_dict,
            'message': 'Certificado actualizado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando certificado {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# HELPERS: Planillas
# ============================================================
def validar_planilla(data):
    """Valida campos obligatorios de una planilla SS."""
    if not data.get('periodo'):
        return False, 'periodo requerido (formato YYYY-MM)'
    return True, None


# ============================================================
# ENDPOINTS: CRUD PLANILLAS DE SEGURIDAD SOCIAL
# ============================================================

@bp.route('/planillas', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_planillas():
    """Lista planillas de seguridad social con filtros opcionales"""
    try:
        from app.models.planilla_ss import PlanillaSS
        from datetime import date
        
        empresa_id = request.args.get('empresa_id', type=int)
        vigente = request.args.get('vigente')  # true | false
        
        query = PlanillaSS.query
        
        if empresa_id:
            query = query.filter_by(empresa_id=empresa_id)
        
        if vigente and vigente.lower() == 'true':
            query = query.filter(PlanillaSS.vigencia_fin >= date.today())
        elif vigente and vigente.lower() == 'false':
            query = query.filter(PlanillaSS.vigencia_fin < date.today())
        
        planillas = query.order_by(PlanillaSS.fecha_pago.desc()).all()
        
        # Agregar campo vigente calculado
        data = []
        for planilla in planillas:
            plan_dict = planilla.to_dict()
            plan_dict['vigente'] = planilla.vigencia_fin >= date.today()
            data.append(plan_dict)
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando planillas SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/planillas', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def crear_planilla():
    """Registra una nueva planilla de seguridad social con cálculo automático de vigencia"""
    try:
        from app.models.planilla_ss import PlanillaSS
        from app.models.empresa_contratista import EmpresaContratista
        from datetime import date, timedelta
        
        data = request.get_json()
        
        # Validaciones
        if not data.get('empresa_id'):
            return jsonify({'success': False, 'message': 'empresa_id requerido'}), 400
        
        if not data.get('fecha_pago'):
            return jsonify({'success': False, 'message': 'fecha_pago requerido'}), 400
        
        # Validar empresa existe
        empresa = EmpresaContratista.query.get(data['empresa_id'])
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404
        
        # Validar campos obligatorios
        es_valido, error = validar_planilla(data)
        if not es_valido:
            return jsonify({'success': False, 'message': error}), 400
        
        # LÓGICA CRÍTICA: Calcular vigencia_fin automáticamente (30 días desde pago)
        fecha_pago = date.fromisoformat(data['fecha_pago'])
        vigencia_fin = fecha_pago + timedelta(days=30)
        
        # Construir planilla solo con campos válidos del modelo
        planilla = PlanillaSS(
            empresa_id=data['empresa_id'],
            periodo=data['periodo'],
            fecha_pago=data['fecha_pago'],
            vigencia_fin=vigencia_fin.isoformat(),
            archivo_nombre=data.get('archivo_nombre'),
            archivo_ruta=data.get('archivo_ruta'),
        )
        db.session.add(planilla)
        db.session.commit()
        
        logger.info(f"Planilla creada: {planilla.id} para empresa {empresa.id} por usuario {current_user.id}")
        
        plan_dict = planilla.to_dict()
        plan_dict['vigente'] = planilla.vigencia_fin >= date.today()
        
        return jsonify({
            'success': True,
            'data': plan_dict,
            'message': 'Planilla registrada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando planilla SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/planillas/<int:id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_planilla(id):
    """Obtiene detalle de una planilla de seguridad social"""
    try:
        from app.models.planilla_ss import PlanillaSS
        from datetime import date
        
        planilla = PlanillaSS.query.get(id)
        if not planilla:
            return jsonify({'success': False, 'message': 'Planilla no encontrada'}), 404
        
        plan_dict = planilla.to_dict()
        plan_dict['vigente'] = planilla.vigencia_fin >= date.today()
        
        return jsonify({
            'success': True,
            'data': plan_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo planilla {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/planillas/empresa/<int:empresa_id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_planillas_empresa(empresa_id):
    """Obtiene todas las planillas de una empresa"""
    try:
        from app.models.planilla_ss import PlanillaSS
        from app.models.empresa_contratista import EmpresaContratista
        from datetime import date
        
        empresa = EmpresaContratista.query.get(empresa_id)
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404
        
        planillas = PlanillaSS.query.filter_by(empresa_id=empresa_id).order_by(
            PlanillaSS.fecha_pago.desc()
        ).all()
        
        # Agregar campo vigente
        data = []
        for planilla in planillas:
            plan_dict = planilla.to_dict()
            plan_dict['vigente'] = planilla.vigencia_fin >= date.today()
            data.append(plan_dict)
        
        return jsonify({
            'success': True,
            'data': data,
            'empresa': empresa.to_dict(),
            'total': len(data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo planillas de empresa {empresa_id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/planillas/vigentes/<int:empresa_id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_planillas_vigentes_empresa(empresa_id):
    """Obtiene solo las planillas vigentes (hoy) de una empresa"""
    try:
        from app.models.planilla_ss import PlanillaSS
        from app.models.empresa_contratista import EmpresaContratista
        from datetime import date
        
        empresa = EmpresaContratista.query.get(empresa_id)
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404
        
        hoy = date.today()
        planillas = PlanillaSS.query.filter(
            PlanillaSS.empresa_id == empresa_id,
            PlanillaSS.vigencia_fin >= hoy
        ).order_by(PlanillaSS.fecha_pago.desc()).all()
        
        # Todas son vigentes por definición del filtro
        data = []
        for planilla in planillas:
            plan_dict = planilla.to_dict()
            plan_dict['vigente'] = True
            data.append(plan_dict)
        
        return jsonify({
            'success': True,
            'data': data,
            'empresa': empresa.to_dict(),
            'total': len(data),
            'fecha_consulta': hoy.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo planillas vigentes de empresa {empresa_id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# HELPERS: Autorizaciones SST
# ============================================================

def generar_consecutivo_sst():
    """
    Eliminado: la columna numero_autorizacion no existe en el modelo AutorizacionSST.
    Se usa el ID de la tabla como identificador (único por definición).
    """
    raise NotImplementedError("generar_consecutivo_sst eliminado — no hay columna numero_autorizacion en el modelo")


# Transiciones de estado válidas (estados en minúsculas, igual que el modelo y la BD)
TRANSICIONES_VALIDAS = {
    'borrador':  ['revision'],
    'revision':  ['aprobada', 'rechazada'],
    'aprobada':  ['vencida', 'anulada'],
    'rechazada': [],  # Estado final
    'vencida':   [],  # Estado final
    'anulada':   [],  # Estado final
}


def puede_transitar(estado_actual, estado_nuevo, rol_usuario):
    """
    Valida si la transición de estado es permitida para el rol dado.
    
    Args:
        estado_actual (str): Estado actual de la autorización
        estado_nuevo (str): Estado al que se quiere transitar
        rol_usuario (str): Rol del usuario que intenta la transición
    
    Returns:
        tuple: (puede: bool, mensaje_error: str|None)
    """
    if estado_nuevo not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        return False, f"No se puede pasar de {estado_actual} a {estado_nuevo}"
    
    # Solo master puede anular
    if estado_nuevo == 'anulada' and rol_usuario != 'usuario_master':
        return False, "Solo el master puede anular una autorización"
    
    # Solo admin_sst o master pueden aprobar/rechazar
    if estado_nuevo in ('aprobada', 'rechazada') and rol_usuario not in ('admin_sst', 'usuario_master'):
        return False, "Solo admin_sst o master pueden aprobar/rechazar"
    
    return True, None


def marcar_vencidas():
    """
    Marca como VENCIDAS las autorizaciones cuya vigencia_fin ya pasó.
    Ejecutar al listar autorizaciones para mantener estados actualizados.
    
    Returns:
        int: Cantidad de autorizaciones marcadas como vencidas
    """
    from app.models.autorizacion_sst import AutorizacionSST
    from datetime import date
    
    vencidas = AutorizacionSST.query.filter(
        AutorizacionSST.estado == 'aprobada',
        AutorizacionSST.fecha_fin < date.today()
    ).all()
    
    for auth in vencidas:
        auth.estado = 'vencida'
    
    if vencidas:
        db.session.commit()
        logger.info(f"Marcadas {len(vencidas)} autorizaciones como VENCIDAS")
    
    return len(vencidas)


# ============================================================
# ENDPOINTS: CRUD AUTORIZACIONES SST
# ============================================================

# ── Helpers de archivos ───────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _documentos_sst_base():
    """Devuelve la ruta absoluta de la carpeta Documentos_SST dentro del proyecto"""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, 'Documentos_SST')

def _carpeta_autorizacion(numero_autorizacion):
    """Crea (si no existe) y devuelve la ruta de la subcarpeta de la autorización"""
    carpeta = os.path.join(_documentos_sst_base(), numero_autorizacion)
    os.makedirs(carpeta, exist_ok=True)
    return carpeta

def _nombre_documento(numero_autorizacion, nit_empresa, num_id_empleado, numero_planilla, seq):
    """
    Devuelve nombre de archivo: AC-0000001_900123_12345678_PLAN001_001.pdf
    Sanitiza componentes para evitar chars inválidos en nombres de archivo.
    """
    def s(v):
        return str(v or 'X').replace('/', '-').replace('\\', '-').replace(' ', '_')[:40]
    return f"{s(numero_autorizacion)}_{s(nit_empresa)}_{s(num_id_empleado)}_{s(numero_planilla)}_{seq:03d}.pdf"

def _siguiente_seq(carpeta, nombre_base_sin_seq):
    """Calcula el siguiente número de secuencia para evitar colisiones de nombre"""
    import glob
    patron = os.path.join(carpeta, nombre_base_sin_seq + '_*.pdf')
    existentes = glob.glob(patron)
    return len(existentes) + 1


@bp.route('/autorizaciones/consecutivo', methods=['GET'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def obtener_consecutivo():
    """Devuelve el próximo número de autorización AC-XXXXXXXX"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        from sqlalchemy import func
        ultimo = db.session.query(func.max(AutorizacionSST.id)).scalar() or 0
        siguiente = ultimo + 1
        return jsonify({
            'success': True,
            'consecutivo': f'AC-{siguiente:08d}'
        }), 200
    except Exception as e:
        logger.error(f"Error generando consecutivo: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500


@bp.route('/autorizaciones/verificar-planilla', methods=['GET'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def verificar_numero_planilla():
    """
    GET /api/sst/autorizaciones/verificar-planilla?numero=XXX&operador_id=Y
    Verifica si un número de planilla ya fue registrado con ese operador.
    """
    try:
        from app.models.planilla_ss import PlanillaSS
        from app.models.empresa_contratista import EmpresaContratista
        numero = request.args.get('numero', '').strip()
        operador_id = request.args.get('operador_id', type=int)
        if not numero:
            return jsonify({'success': False, 'message': 'numero requerido'}), 400
        q = PlanillaSS.query.filter_by(numero_planilla=numero)
        if operador_id:
            q = q.filter_by(operador_id=operador_id)
        planilla = q.first()
        if planilla:
            empresa = EmpresaContratista.query.get(planilla.empresa_id)
            nombre_empresa = ''
            if empresa:
                nombre_empresa = empresa.razon_social if empresa.tipo_persona == 'JURIDICA' \
                    else empresa.nombre_completo_persona_natural
            return jsonify({
                'success': True,
                'existe': True,
                'planilla': {
                    'id': planilla.id,
                    'periodo': planilla.periodo,
                    'fecha_pago': planilla.fecha_pago.isoformat() if planilla.fecha_pago else None,
                    'empresa_nombre': nombre_empresa,
                    'created_at': planilla.created_at.isoformat() if planilla.created_at else None,
                }
            }), 200
        return jsonify({'success': True, 'existe': False}), 200
    except Exception as e:
        logger.error(f"Error verificando planilla: {e}")
        return jsonify({'success': False, 'message': 'Error interno'}), 500


@bp.route('/autorizaciones/upload-documento', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def upload_documento_autorizacion():
    """
    Sube un archivo PDF a Documentos_SST/{numero_autorizacion}/
    Form-data: numero_autorizacion, nit_empresa, num_id_empleado, numero_planilla, tipo_doc, archivo
    Devuelve: { ruta_relativa, nombre_archivo }
    """
    try:
        numero_autorizacion = request.form.get('numero_autorizacion', '').strip()
        nit_empresa         = request.form.get('nit_empresa', '').strip()
        num_id_empleado     = request.form.get('num_id_empleado', 'X').strip()
        numero_planilla     = request.form.get('numero_planilla', 'SIN').strip()

        if not numero_autorizacion:
            return jsonify({'success': False, 'message': 'numero_autorizacion requerido'}), 400

        if 'archivo' not in request.files:
            return jsonify({'success': False, 'message': 'archivo requerido'}), 400

        archivo = request.files['archivo']
        if archivo.filename == '' or not _allowed_file(archivo.filename):
            return jsonify({'success': False, 'message': 'Tipo de archivo no permitido (solo PDF/PNG/JPG)'}), 400

        carpeta = _carpeta_autorizacion(numero_autorizacion)

        # Base del nombre sin secuencia para calcular siguiente seq
        base = f"{numero_autorizacion}_{nit_empresa}_{num_id_empleado}_{numero_planilla}"
        seq = _siguiente_seq(carpeta, base)
        nombre_final = _nombre_documento(numero_autorizacion, nit_empresa, num_id_empleado, numero_planilla, seq)

        ruta_completa = os.path.join(carpeta, nombre_final)
        archivo.save(ruta_completa)

        # Ruta relativa para guardar en BD
        ruta_relativa = os.path.join('Documentos_SST', numero_autorizacion, nombre_final)

        logger.info(f"Documento SST subido: {ruta_relativa} por usuario {current_user.id}")

        return jsonify({
            'success': True,
            'nombre_archivo': nombre_final,
            'ruta_relativa': ruta_relativa
        }), 200

    except Exception as e:
        logger.error(f"Error subiendo documento SST: {e}")
        return jsonify({'success': False, 'message': 'Error al guardar el archivo'}), 500


@bp.route('/autorizaciones', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_autorizaciones():
    """Lista autorizaciones SST con filtros opcionales. Actualiza estados vencidos."""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        
        # Marcar vencidas antes de listar
        marcar_vencidas()
        
        estado = request.args.get('estado')  # BORRADOR | REVISION | APROBADA | RECHAZADA | VENCIDA | ANULADA
        sede_id = request.args.get('sede_id', type=int)
        empresa_id = request.args.get('empresa_id', type=int)
        
        query = AutorizacionSST.query
        
        if estado and estado.lower() in ('borrador', 'revision', 'aprobada', 'rechazada', 'vencida', 'anulada'):
            query = query.filter_by(estado=estado.lower())
        
        if sede_id:
            query = query.filter_by(sede_id=sede_id)
        
        if empresa_id:
            query = query.filter_by(empresa_id=empresa_id)
        
        autorizaciones = query.order_by(AutorizacionSST.created_at.desc()).all()

        resultado = []
        for aut in autorizaciones:
            d = aut.to_dict()
            if aut.empresa:
                d['empresa_nombre'] = aut.empresa.razon_social if aut.empresa.tipo_persona == 'JURIDICA' \
                    else aut.empresa.nombre_completo_persona_natural
            else:
                d['empresa_nombre'] = 'N/A'
            resultado.append(d)

        return jsonify({
            'success': True,
            'data': resultado,
            'total': len(resultado)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando autorizaciones SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def crear_autorizacion():
    """
    Crea una nueva autorización SST en estado BORRADOR.
    Acepta JSON con la siguiente estructura:
    {
        "empresa_id": int,
        "sede_id": int,
        "labor": str,
        "fecha_inicio": "YYYY-MM-DD",
        "fecha_fin":    "YYYY-MM-DD",
        "fecha_autorizacion": "YYYY-MM-DD",   (opcional, default hoy)
        "observaciones": str,                 (opcional)
        "planilla": {                         (opcional)
            "operador_id": int,
            "numero_planilla": str,
            "tipo_planilla": "I"|"E"|"N",
            "periodo": "YYYY-MM",
            "fecha_pago": "YYYY-MM-DD",
            "vigencia_fin": "YYYY-MM-DD",
            "archivo_ruta": str,              (ruta devuelta por upload-documento)
            "archivo_nombre": str
        },
        "empleados": [                        (opcional)
            {
                "empleado_id": int,
                "trabajo_altura": bool,
                "trabajo_energias_peligrosas": bool,
                "trabajo_espacios_confinados": bool,
                "trabajo_caliente": bool,
                "trabajo_izaje_cargas": bool,
                "trabajo_excavacion": bool,
                "trabajo_sustancias_quimicas": bool,
                "trabajo_otro": str,
                "documentos": [{ "tipo": str, "nombre": str, "ruta": str }]
            }
        ],
        "carta_presentacion_ruta": str        (opcional)
    }
    """
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        from app.models.empresa_contratista import EmpresaContratista
        from app.models.planilla_ss import PlanillaSS
        from app.models.empleado_autorizacion import EmpleadoAutorizacion
        from datetime import date

        data = request.get_json()

        # ── validaciones obligatorias ───────────────────────────────────────────
        if not data.get('empresa_id'):
            return jsonify({'success': False, 'message': 'empresa_id requerido'}), 400
        if not data.get('sede_id'):
            return jsonify({'success': False, 'message': 'sede_id requerido'}), 400
        if not data.get('fecha_inicio') or not data.get('fecha_fin'):
            return jsonify({'success': False, 'message': 'Fechas de vigencia requeridas'}), 400
        if not data.get('labor'):
            return jsonify({'success': False, 'message': 'labor requerido'}), 400

        empresa = EmpresaContratista.query.get(data['empresa_id'])
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404

        # ── Generar consecutivo ─────────────────────────────────────────────────
        from sqlalchemy import func
        ultimo_id = db.session.query(func.max(AutorizacionSST.id)).scalar() or 0
        numero_autorizacion = f'AC-{(ultimo_id + 1):08d}'

        # ── Crear planilla SS si viene en el payload ────────────────────────────
        planilla_id = None
        if data.get('planilla'):
            pdata = data['planilla']
            planilla = PlanillaSS(
                empresa_id=data['empresa_id'],
                operador_id=pdata.get('operador_id'),
                numero_planilla=pdata.get('numero_planilla'),
                tipo_planilla=pdata.get('tipo_planilla'),
                periodo=pdata.get('periodo', ''),
                fecha_pago=pdata.get('fecha_pago'),
                vigencia_fin=pdata.get('vigencia_fin', pdata.get('fecha_pago')),
                archivo_nombre=pdata.get('archivo_nombre'),
                archivo_ruta=pdata.get('archivo_ruta'),
                estado='pendiente',
            )
            db.session.add(planilla)
            db.session.flush()   # obtener planilla.id antes del commit
            planilla_id = planilla.id

        # ── Crear autorización ──────────────────────────────────────────────────
        autorizacion = AutorizacionSST(
            numero_autorizacion=numero_autorizacion,
            empresa_id=data['empresa_id'],
            sede_id=data.get('sede_id'),
            planilla_ss_id=planilla_id,
            labor=data['labor'],
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            fecha_autorizacion=data.get('fecha_autorizacion', date.today().isoformat()),
            estado='borrador',
            observaciones=data.get('observaciones'),
            carta_presentacion_ruta=data.get('carta_presentacion_ruta'),
            created_by=current_user.id,
        )
        db.session.add(autorizacion)
        db.session.flush()   # obtener autorizacion.id

        # ── Crear relaciones con empleados ──────────────────────────────────────
        for emp_data in (data.get('empleados') or []):
            if not emp_data.get('empleado_id'):
                continue
            ea = EmpleadoAutorizacion(
                autorizacion_id=autorizacion.id,
                empleado_id=emp_data['empleado_id'],
                trabajo_altura=emp_data.get('trabajo_altura', False),
                trabajo_energias_peligrosas=emp_data.get('trabajo_energias_peligrosas', False),
                trabajo_espacios_confinados=emp_data.get('trabajo_espacios_confinados', False),
                trabajo_caliente=emp_data.get('trabajo_caliente', False),
                trabajo_izaje_cargas=emp_data.get('trabajo_izaje_cargas', False),
                trabajo_excavacion=emp_data.get('trabajo_excavacion', False),
                trabajo_sustancias_quimicas=emp_data.get('trabajo_sustancias_quimicas', False),
                trabajo_otro=emp_data.get('trabajo_otro'),
            )
            ea.set_documentos(emp_data.get('documentos') or [])
            db.session.add(ea)

        db.session.commit()

        logger.info(f"Autorización SST {numero_autorizacion} creada por usuario {current_user.id}")

        return jsonify({
            'success': True,
            'data': autorizacion.to_dict(),
            'message': f'Autorización {numero_autorizacion} creada exitosamente'
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando autorización SST: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones/<int:id>', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def obtener_autorizacion(id):
    """Obtiene detalle completo de una autorización con empleados asociados"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        
        autorizacion = AutorizacionSST.query.get(id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        data = autorizacion.to_dict()
        data['empleados'] = []  # Relación empleados-autorización no implementada en esta versión
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo autorización {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones/<int:id>', methods=['PUT'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def actualizar_autorizacion(id):
    """Actualiza una autorización SST (solo si está en estado BORRADOR)"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        
        autorizacion = AutorizacionSST.query.get(id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        if autorizacion.estado != 'borrador':
            return jsonify({
                'success': False,
                'message': f'Solo se pueden actualizar autorizaciones en estado borrador (actual: {autorizacion.estado})'
            }), 400
        
        data = request.get_json()
        
        # Campos actualizables
        campos_actualizables = [
            'empresa_id', 'sede_id', 'fecha_inicio', 'fecha_fin', 'labor',
            'observaciones', 'carta_presentacion_ruta', 'fecha_autorizacion'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                setattr(autorizacion, campo, data[campo])
        
        db.session.commit()
        
        logger.info(f"Autorización {id} actualizada por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': autorizacion.to_dict(),
            'message': 'Autorización actualizada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando autorización {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones/<int:id>/enviar-revision', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def enviar_revision_autorizacion(id):
    """Cambia estado de borrador a revision"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        
        autorizacion = AutorizacionSST.query.get(id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        # Validar transición
        puede, error = puede_transitar(autorizacion.estado, 'revision', current_user.rol)
        if not puede:
            return jsonify({'success': False, 'message': error}), 400
        
        autorizacion.estado = 'revision'
        db.session.commit()
        
        logger.info(f"Autorización {id} enviada a revision por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': autorizacion.to_dict(),
            'message': 'Autorización enviada a revisión'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enviando autorización {id} a revisión: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones/<int:id>/aprobar', methods=['POST'])
@login_required
@role_required('admin_sst', 'usuario_master')
def aprobar_autorizacion(id):
    """Cambia estado de revision a aprobada (solo admin_sst o master)"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        from app.models.empresa_contratista import EmpresaContratista
        
        autorizacion = AutorizacionSST.query.get(id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        # Validar transición
        puede, error = puede_transitar(autorizacion.estado, 'aprobada', current_user.rol)
        if not puede:
            return jsonify({'success': False, 'message': error}), 400
        
        autorizacion.estado = 'aprobada'
        autorizacion.aprobado_by = current_user.id
        
        db.session.commit()
        
        logger.info(f"Autorización {id} aprobada por usuario {current_user.id}")
        
        # Enviar notificación email a la empresa
        try:
            from app.services.email_service import enviar_notificacion_autorizacion_aprobada
            empresa = EmpresaContratista.query.get(autorizacion.empresa_id)
            if empresa and empresa.email:
                enviar_notificacion_autorizacion_aprobada(
                    autorizacion.to_dict(),
                    empresa.to_dict(),
                    empresa.email,
                    pdf_ruta=autorizacion.pdf_ruta
                )
        except Exception as email_error:
            logger.error(f"Error enviando email aprobación: {email_error}")
        
        return jsonify({
            'success': True,
            'data': autorizacion.to_dict(),
            'message': 'Autorización aprobada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error aprobando autorización {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones/<int:id>/rechazar', methods=['POST'])
@login_required
@role_required('admin_sst', 'usuario_master')
def rechazar_autorizacion(id):
    """Cambia estado de revision a rechazada (solo admin_sst o master)."""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        from app.models.empresa_contratista import EmpresaContratista
        
        autorizacion = AutorizacionSST.query.get(id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        # Validar transición
        puede, error = puede_transitar(autorizacion.estado, 'rechazada', current_user.rol)
        if not puede:
            return jsonify({'success': False, 'message': error}), 400
        
        autorizacion.estado = 'rechazada'
        
        db.session.commit()
        
        logger.info(f"Autorización {id} rechazada por usuario {current_user.id}")
        
        # Enviar notificación email
        try:
            from app.services.email_service import enviar_notificacion_autorizacion_rechazada
            empresa = EmpresaContratista.query.get(autorizacion.empresa_id)
            if empresa and empresa.email:
                enviar_notificacion_autorizacion_rechazada(
                    autorizacion.to_dict(),
                    empresa.to_dict(),
                    empresa.email
                )
        except Exception as email_error:
            logger.error(f"Error enviando email rechazo: {email_error}")
        
        return jsonify({
            'success': True,
            'data': autorizacion.to_dict(),
            'message': 'Autorización rechazada'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rechazando autorización {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/autorizaciones/<int:id>/anular', methods=['POST'])
@login_required
@role_required('usuario_master')
def anular_autorizacion(id):
    """Cambia estado de aprobada a anulada (solo master)."""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        
        autorizacion = AutorizacionSST.query.get(id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        # Validar transición
        puede, error = puede_transitar(autorizacion.estado, 'anulada', current_user.rol)
        if not puede:
            return jsonify({'success': False, 'message': error}), 400
        
        autorizacion.estado = 'anulada'
        
        db.session.commit()
        
        logger.info(f"Autorización {id} anulada por usuario {current_user.id} (master)")
        
        return jsonify({
            'success': True,
            'data': autorizacion.to_dict(),
            'message': 'Autorización anulada'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error anulando autorización {id}: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# SECCIÓN 6: INGRESOS Y SALIDAS DE CONTRATISTAS
# ============================================================

@bp.route('/ingresos', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_ingresos():
    """Lista logs de ingresos/salidas de contratistas con filtros.
    Query params:
    - sede_id: Filtrar por sede
    - fecha: Filtrar por fecha (formato YYYY-MM-DD, default=hoy)
    - tipo_evento: ingreso o salida
    - empleado_id: Filtrar por empleado específico
    """
    try:
        from app.models.log_ingreso_contratista import LogIngresoContratista
        from app.models.empleado_contratista import EmpleadoContratista
        from app.models.empresa_contratista import EmpresaContratista
        from datetime import date, datetime
        from sqlalchemy.orm import joinedload
        
        # Filtros
        sede_id = request.args.get('sede_id', type=int)
        fecha_str = request.args.get('fecha')  # YYYY-MM-DD
        tipo_evento = request.args.get('tipo_evento')  # ingreso | salida
        empleado_id = request.args.get('empleado_id', type=int)
        
        # Determinar fecha a consultar
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Formato de fecha inválido (use YYYY-MM-DD)'}), 400
        else:
            fecha = date.today()
        
        # Query base con eager loading (previene N+1)
        query = LogIngresoContratista.query.options(
            joinedload(LogIngresoContratista.empleado)
            .joinedload(EmpleadoContratista.empresa)
        )
        
        # Filtrar por fecha (timestamp_evento en el día especificado)
        fecha_inicio = datetime.combine(fecha, datetime.min.time())
        fecha_fin = datetime.combine(fecha, datetime.max.time())
        query = query.filter(
            LogIngresoContratista.timestamp_evento >= fecha_inicio,
            LogIngresoContratista.timestamp_evento <= fecha_fin
        )
        
        if sede_id:
            query = query.filter_by(sede_id=sede_id)
        
        if tipo_evento and tipo_evento.lower() in ('ingreso', 'salida'):
            query = query.filter_by(tipo_evento=tipo_evento.lower())
        
        if empleado_id:
            query = query.filter_by(empleado_id=empleado_id)
        
        logs = query.order_by(LogIngresoContratista.timestamp_evento.desc()).all()
        
        # Enriquecer con datos del empleado y empresa (ya cargados por joinedload)
        resultado = []
        for log in logs:
            empleado = log.empleado
            empresa = empleado.empresa if empleado else None
            
            item = log.to_dict()
            item['empleado'] = {
                'id': empleado.id,
                'nombre_completo': empleado.nombre_completo,
                'tipo_id': empleado.tipo_id,
                'num_id': empleado.num_id,
            } if empleado else None
            
            item['empresa'] = {
                'id': empresa.id,
                'nombre': empresa.razon_social if empresa.tipo_persona == 'JURIDICA' else empresa.nombre_completo_persona_natural,
            } if empresa else None
            
            resultado.append(item)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total': len(resultado),
            'fecha': fecha.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando ingresos: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/ingresos', methods=['POST'])
@login_required
@role_required(*ROLES_SST)
def registrar_ingreso():
    """Registra ingreso de empleado contratista.
    Body JSON:
    {
        "empleado_id": int,
        "autorizacion_sst_id": int,
        "sede_id": int,
        "observaciones": str (opcional)
    }
    
    Validaciones:
    - Autorización existe y está APROBADA
    - Autorización no vencida
    - Empleado incluido en la autorización
    - Empleado no tiene ingreso activo (último evento debe ser 'salida')
    """
    try:
        from app.models.log_ingreso_contratista import LogIngresoContratista
        from app.models.autorizacion_sst import AutorizacionSST
        from app.models.empleado_contratista import EmpleadoContratista
        from datetime import date
        
        data = request.json
        
        # Validación de campos requeridos
        if not all(k in data for k in ['empleado_id', 'autorizacion_sst_id', 'sede_id']):
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
        
        # Validación de acceso por sede (operadores solo su sede)
        if not current_user.tiene_acceso_sede(data['sede_id']):
            return jsonify({'success': False, 'message': 'No tiene acceso a esta sede'}), 403
        
        empleado_id = data['empleado_id']
        autorizacion_sst_id = data['autorizacion_sst_id']
        
        # VALIDACIÓN 1: Autorización existe y está APROBADA
        autorizacion = AutorizacionSST.query.get(autorizacion_sst_id)
        if not autorizacion:
            return jsonify({'success': False, 'message': 'Autorización no encontrada'}), 404
        
        if autorizacion.estado.lower() != 'aprobada':
            return jsonify({'success': False, 'message': f'Autorización no está aprobada (estado actual: {autorizacion.estado})'}), 400
        
        # VALIDACIÓN 2: Autorización no vencida
        if autorizacion.fecha_fin < date.today():
            # Marcar como vencida
            autorizacion.estado = 'vencida'
            db.session.commit()
            return jsonify({'success': False, 'message': 'Autorización SST vencida'}), 400
        
        # VALIDACIÓN 3: Empleado existe y pertenece a la misma empresa de la autorización
        empleado = EmpleadoContratista.query.get(empleado_id)
        if not empleado:
            return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
        
        if empleado.empresa_id != autorizacion.empresa_id:
            return jsonify({'success': False, 'message': 'El empleado no pertenece a la empresa de esta autorización'}), 400
        
        # VALIDACIÓN 4: Empleado no tiene ingreso activo
        # Buscar el último log de este empleado
        ultimo_log = LogIngresoContratista.query.filter_by(
            empleado_id=empleado_id
        ).order_by(LogIngresoContratista.timestamp_evento.desc()).first()
        
        if ultimo_log and ultimo_log.tipo_evento == 'ingreso':
            return jsonify({
                'success': False,
                'message': 'Empleado ya se encuentra en instalaciones (debe registrar salida primero)'
            }), 400
        
        # Crear log de ingreso
        nuevo_log = LogIngresoContratista(
            empleado_id=empleado_id,
            autorizacion_sst_id=autorizacion_sst_id,
            sede_id=data['sede_id'],
            tipo_evento='ingreso',
            registrado_por=current_user.id,
            observaciones=data.get('observaciones')
        )
        
        db.session.add(nuevo_log)
        db.session.commit()
        
        logger.info(f"Ingreso registrado para empleado {empleado_id} por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': nuevo_log.to_dict(),
            'message': 'Ingreso registrado correctamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registrando ingreso: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/ingresos/<int:id>/salida', methods=['PUT'])
@login_required
@role_required(*ROLES_SST)
def registrar_salida(id):
    """Registra salida de empleado contratista.
    El ID corresponde al log de ingreso.
    Body JSON (opcional):
    {
        "observaciones": str
    }
    
    Crea un nuevo log con tipo_evento='salida'.
    """
    try:
        from app.models.log_ingreso_contratista import LogIngresoContratista
        
        # Buscar log de ingreso
        log_ingreso = LogIngresoContratista.query.get(id)
        if not log_ingreso:
            return jsonify({'success': False, 'message': 'Log de ingreso no encontrado'}), 404
        
        # Validación de acceso por sede
        if not current_user.tiene_acceso_sede(log_ingreso.sede_id):
            return jsonify({'success': False, 'message': 'No tiene acceso a esta sede'}), 403
        
        if log_ingreso.tipo_evento != 'ingreso':
            return jsonify({'success': False, 'message': 'El log especificado no es un ingreso'}), 400
        
        # Verificar que no haya ya una salida posterior
        salida_existente = LogIngresoContratista.query.filter(
            LogIngresoContratista.empleado_id == log_ingreso.empleado_id,
            LogIngresoContratista.timestamp_evento > log_ingreso.timestamp_evento,
            LogIngresoContratista.tipo_evento == 'salida'
        ).first()
        
        if salida_existente:
            return jsonify({'success': False, 'message': 'Ya existe una salida registrada para este ingreso'}), 400
        
        data = request.json or {}
        
        # Crear log de salida
        log_salida = LogIngresoContratista(
            empleado_id=log_ingreso.empleado_id,
            autorizacion_sst_id=log_ingreso.autorizacion_sst_id,
            sede_id=log_ingreso.sede_id,
            tipo_evento='salida',
            registrado_por=current_user.id,
            observaciones=data.get('observaciones')
        )
        
        db.session.add(log_salida)
        db.session.commit()
        
        logger.info(f"Salida registrada para empleado {log_ingreso.empleado_id} por usuario {current_user.id}")
        
        return jsonify({
            'success': True,
            'data': log_salida.to_dict(),
            'message': 'Salida registrada correctamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registrando salida: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


@bp.route('/ingresos/activos', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def listar_empleados_activos():
    """Lista empleados contratistas actualmente en instalaciones.
    Un empleado está activo si su último log es de tipo='ingreso'.
    
    Query params:
    - sede_id: Filtrar por sede
    """
    try:
        from app.models.log_ingreso_contratista import LogIngresoContratista
        from app.models.empleado_contratista import EmpleadoContratista
        from app.models.empresa_contratista import EmpresaContratista
        from sqlalchemy import func
        from sqlalchemy.orm import joinedload
        
        sede_id = request.args.get('sede_id', type=int)
        
        # Query para obtener el último log de cada empleado
        # Subconsulta: obtener el ID del último log por empleado
        subquery = db.session.query(
            LogIngresoContratista.empleado_id,
            func.max(LogIngresoContratista.id).label('max_id')
        ).group_by(LogIngresoContratista.empleado_id).subquery()
        
        # Query principal con eager loading (previene N+1)
        query = db.session.query(LogIngresoContratista).options(
            joinedload(LogIngresoContratista.empleado)
            .joinedload(EmpleadoContratista.empresa),
            joinedload(LogIngresoContratista.sede)
        ).join(
            subquery,
            (LogIngresoContratista.id == subquery.c.max_id) &
            (LogIngresoContratista.empleado_id == subquery.c.empleado_id)
        ).filter(
            LogIngresoContratista.tipo_evento == 'ingreso'
        )
        
        if sede_id:
            query = query.filter(LogIngresoContratista.sede_id == sede_id)
        
        logs_activos = query.all()
        
        # Enriquecer con datos del empleado y empresa (ya cargados por joinedload)
        resultado = []
        for log in logs_activos:
            empleado = log.empleado
            empresa = empleado.empresa if empleado else None
            
            item = log.to_dict()
            item['empleado'] = {
                'id': empleado.id,
                'nombre_completo': empleado.nombre_completo,
                'tipo_id': empleado.tipo_id,
                'num_id': empleado.num_id,
                'empresa_id': empleado.empresa_id,
            } if empleado else None
            
            item['empresa'] = {
                'id': empresa.id,
                'nombre': empresa.razon_social if empresa.tipo_persona == 'JURIDICA' else empresa.nombre_completo_persona_natural,
            } if empresa else None
            
            item['sede'] = {
                'id': log.sede_id,
                'nombre': log.sede.descripcion_sede if log.sede else None
            } if log.sede_id else None
            
            resultado.append(item)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total': len(resultado)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando empleados activos: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500


# ============================================================
# ENDPOINT: POST /api/sst/autorizaciones/<id>/generar-pdf
# Genera el PDF SC-SST-FOR-015 para una autorización aprobada
# Acceso: admin_sst, usuario_master
# ============================================================
@bp.route('/autorizaciones/<int:id>/generar-pdf', methods=['POST'])
@login_required
@role_required(*ROLES_ADMIN_SST)
def generar_pdf_autorizacion(id):
    """Genera PDF de autorización SST (formato SC-SST-FOR-015)"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST
        from app.models.empresa_contratista import EmpresaContratista
        from app.models.empleado_contratista import EmpleadoContratista
        from app.models.planilla_ss import PlanillaSS
        from app.models.sede import Sede
        from app.services.pdf_service import generar_pdf_autorizacion as generar_pdf
        from datetime import date

        autorizacion = AutorizacionSST.query.get_or_404(id)

        # Solo generar PDF para autorizaciones aprobadas
        if autorizacion.estado != 'aprobada':
            return jsonify({
                'success': False,
                'message': f'Solo se puede generar PDF de autorizaciones aprobadas. Estado actual: {autorizacion.estado}'
            }), 400

        empresa = EmpresaContratista.query.get(autorizacion.empresa_id)
        if not empresa:
            return jsonify({'success': False, 'message': 'Empresa no encontrada'}), 404

        # Empleados de la empresa (activos)
        empleados = EmpleadoContratista.query.filter_by(
            empresa_id=empresa.id, estado='activo'
        ).all()

        # Planilla vigente más reciente
        planilla = PlanillaSS.query.filter(
            PlanillaSS.empresa_id == empresa.id,
            PlanillaSS.vigencia_fin >= date.today()
        ).order_by(PlanillaSS.vigencia_fin.desc()).first()

        # Sede (puede ser None)
        sede = Sede.query.get(autorizacion.sede_id) if autorizacion.sede_id else None

        # Generar PDF
        resultado = generar_pdf(autorizacion, empresa, empleados, planilla, sede)

        if not resultado['success']:
            return jsonify({'success': False, 'message': resultado.get('error', 'Error generando PDF')}), 500

        # Guardar ruta en autorización
        autorizacion.pdf_ruta = resultado['ruta']
        db.session.commit()

        logger.info(f"PDF generado para autorización #{id} por usuario {current_user.id}")

        return jsonify({
            'success': True,
            'data': {
                'pdf_ruta': resultado['ruta'],
                'nombre_archivo': resultado['nombre'],
                'consecutivo': resultado['consecutivo']
            },
            'message': f"PDF {resultado['consecutivo']} generado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error generando PDF autorización #{id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ENDPOINT: GET /api/sst/autorizaciones/<id>/descargar-pdf
# Descarga el PDF generado de una autorización
# Acceso: cualquier rol SST
# ============================================================
@bp.route('/autorizaciones/<int:id>/descargar-pdf', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def descargar_pdf_autorizacion(id):
    """Descarga PDF de autorización SST"""
    try:
        from app.models.autorizacion_sst import AutorizacionSST

        autorizacion = AutorizacionSST.query.get_or_404(id)

        if not autorizacion.pdf_ruta:
            return jsonify({'success': False, 'message': 'Esta autorización no tiene PDF generado'}), 404

        # Construir ruta completa con validación de sandbox
        base_storage = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'uploads')
        )
        ruta_completa = os.path.normpath(os.path.join(base_storage, autorizacion.pdf_ruta))
        if not ruta_completa.startswith(base_storage + os.sep) and ruta_completa != base_storage:
            return jsonify({'success': False, 'message': 'Ruta de archivo inválida'}), 403

        if not os.path.exists(ruta_completa):
            return jsonify({'success': False, 'message': 'Archivo PDF no encontrado en disco'}), 404

        nombre_descarga = os.path.basename(autorizacion.pdf_ruta)

        return send_file(
            ruta_completa,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nombre_descarga
        )

    except Exception as e:
        logger.error(f"Error descargando PDF autorización #{id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

