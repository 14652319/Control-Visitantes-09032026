"""
========================================
RUTAS: MÓDULO SST (Seguridad y Salud en el Trabajo)
Gestión completa de contratistas, planillas y autorizaciones SST
========================================
"""
from flask import Blueprint, request, jsonify
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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
        return jsonify({'success': False, 'message': str(e)}), 500


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
            'direccion', 'ciudad', 'estado', 'observaciones'
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
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/empresas/buscar', methods=['GET'])
@login_required
@role_required(*ROLES_SST)
def buscar_empresa():
    """
    Búsqueda inteligente de empresa por NIT (Jurídica) o num_identificacion (Natural).
    Útil para auto-completado en formularios.
    
    Query params:
        q (str): NIT o número de documento a buscar
    
    Returns:
        {'encontrado': bool, 'data': empresa.to_dict() | None}
    """
    try:
        from app.models.empresa_contratista import EmpresaContratista
        
        consulta = request.args.get('q', '').strip()
        if not consulta:
            return jsonify({
                'success': False,
                'message': 'Parámetro "q" requerido'
            }), 400
        
        # Buscar por NIT (Jurídica) O por num_identificacion (Natural)
        empresa = EmpresaContratista.query.filter(
            db.or_(
                EmpresaContratista.nit == consulta,
                EmpresaContratista.num_identificacion == consulta
            )
        ).first()
        
        if empresa:
            return jsonify({
                'success': True,
                'encontrado': True,
                'data': empresa.to_dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'encontrado': False,
                'data': None
            }), 200
        
    except Exception as e:
        logger.error(f"Error buscando empresa: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

