"""
========================================
RUTAS: REPORTES
Generación de reportes y exportación a Excel
========================================
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from app.models import LogVisitante, LogEvento
from app.routes.auth import role_required
from datetime import datetime, timedelta
import pandas as pd
import io

bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


@bp.route('/visitas', methods=['GET'])
@login_required
def reporte_visitas():
    """Genera un reporte de visitas en un rango de fechas con filtros avanzados"""
    try:
        # Obtener parámetros
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        sede_id = request.args.get('sede_id', type=int)
        dependencia = request.args.get('dependencia')  # Nuevo filtro
        estado = request.args.get('estado')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'message': 'Fechas de inicio y fin son requeridas'
            }), 400
        
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        # Base query
        query = LogVisitante.query.filter(
            LogVisitante.fecha_ingreso >= fecha_inicio_obj,
            LogVisitante.fecha_ingreso <= fecha_fin_obj
        )
        
        # Filtrar por sede según rol
        if current_user.rol == 'usuario_operador':
            query = query.filter_by(sede_id=current_user.sede_id)
        elif sede_id and sede_id > 0:  # 0 o None significa "todas las sedes"
            query = query.filter_by(sede_id=sede_id)
        
        # Filtrar por dependencia
        if dependencia:
            query = query.filter_by(prefijo_dependencia=dependencia)
        
        # Filtrar por estado
        if estado:
            query = query.filter_by(estado_visita=estado)
        
        # Obtener visitas
        visitas = query.order_by(
            LogVisitante.fecha_ingreso.desc(),
            LogVisitante.hora_ingreso.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'total': len(visitas),
            'visitas': [v.to_dict() for v in visitas],
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/visitas/excel', methods=['GET'])
@login_required
def exportar_visitas_excel():
    """Exporta visitas filtradas a un archivo Excel con todos los campos"""
    try:
        # Obtener los mismos parámetros de filtro que /visitas
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        sede_id = request.args.get('sede_id', type=int)
        dependencia = request.args.get('dependencia')
        estado = request.args.get('estado')
        
        # Validar fechas
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'message': 'Fechas de inicio y fin son requeridas'
            }), 400
        
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido'
            }), 400
        
        # Aplicar los mismos filtros que en /visitas
        query = LogVisitante.query.filter(
            LogVisitante.fecha_ingreso >= fecha_inicio_obj,
            LogVisitante.fecha_ingreso <= fecha_fin_obj
        )
        
        if current_user.rol == 'usuario_operador':
            query = query.filter_by(sede_id=current_user.sede_id)
        elif sede_id and sede_id > 0:
            query = query.filter_by(sede_id=sede_id)
        
        if dependencia:
            query = query.filter_by(prefijo_dependencia=dependencia)
        
        if estado:
            query = query.filter_by(estado_visita=estado)
        
        visitas = query.order_by(
            LogVisitante.fecha_ingreso.desc(),
            LogVisitante.hora_ingreso.desc()
        ).all()
        
        if not visitas:
            return jsonify({
                'success': False,
                'message': 'No se encontraron visitas con los filtros aplicados'
            }), 404
        
        # Crear DataFrame con TODOS los campos
        data_excel = []
        for v in visitas:
            data_excel.append({
                'ID': v.id,
                'Fecha Ingreso': v.fecha_ingreso.strftime('%d/%m/%Y'),
                'Hora Ingreso': v.hora_ingreso.strftime('%H:%M:%S'),
                'Fecha Salida': v.fecha_salida.strftime('%d/%m/%Y') if v.fecha_salida else '',
                'Hora Salida': v.hora_salida.strftime('%H:%M:%S') if v.hora_salida else '',
                'Estado': v.estado_visita,
                'Tipo ID': v.tipo_identificacion,
                'Num ID': v.num_identificacion,
                'Primer Nombre': v.primer_nombre,
                'Segundo Nombre': v.segundo_nombre or '',
                'Primer Apellido': v.primer_apellido,
                'Segundo Apellido': v.segundo_apellido or '',
                'Teléfono': v.num_telefono,
                'Correo': v.dir_correo,
                'Empresa': v.empresa,
                'NIT Empresa': v.nit_empresa,
                'Prefijo Dependencia': v.prefijo_dependencia,
                'Dependencia': v.descripcion_dependencia,
                'Funcionario Recibe': v.funcionario_recibe,
                'Funcionario Autoriza': v.funcionario_autoriza,
                'Observaciones': v.observaciones1 or '',
                # Nuevos campos de elementos
                '¿Ingresa Elementos?': 'SÍ' if v.ingresa_elementos else 'NO',
                'Descripción Elementos': v.elementos_observacion or '',
                'Portátil': 'SÍ' if v.elemento_portatil else 'NO',
                'Celular': 'SÍ' if v.elemento_celular else 'NO',
                'Herramientas': 'SÍ' if v.elemento_herramientas else 'NO',
                'Otros Elementos': 'SÍ' if v.elemento_otros else 'NO',
                # Número de visitantes
                'Núm. Visitantes': v.numero_visitantes or 1,
                'Visitantes Adicionales': v.visitantes_adicionales or '',
                # Otros campos
                'Carnet': v.numero_carnet or '',
                'Tiene Foto': 'SÍ' if v.fotografia_visitante else 'NO',
                'Autorización Previa': 'SÍ' if v.autorizacion_previa_id else 'NO',
                'Sede': v.sede.descripcion_sede if v.sede else '',
                'Código Sede': v.sede.codigo_sede if v.sede else '',
                'Operador': v.usuario_registro.usuario if v.usuario_registro else ''
            })
        
        df = pd.DataFrame(data_excel)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Visitas', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Visitas']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                # Limitar ancho máximo y usar índice de columna correcto
                col_letter = chr(65 + idx) if idx < 26 else f"{chr(65 + idx // 26 - 1)}{chr(65 + idx % 26)}"
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)
        
        output.seek(0)
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='REPORTE_EXCEL',
            descripcion=f'Reporte Excel generado: {len(visitas)} visitas ({fecha_inicio} a {fecha_fin})',
            usuario=current_user,
            datos_adicionales={
                'cantidad_visitas': len(visitas),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            nivel='INFO'
        )
        
        # Nombre del archivo
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reporte_visitas_{fecha_actual}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/estadisticas', methods=['GET'])
@role_required('usuario_master')
def estadisticas():
    """Obtiene estadísticas generales del sistema"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Si no se proporcionan fechas, usar últimos 30 días
        if not fecha_inicio or not fecha_fin:
            fecha_fin_obj = datetime.now().date()
            fecha_inicio_obj = fecha_fin_obj - timedelta(days=30)
        else:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Total de visitas en el período
        total_visitas = LogVisitante.query.filter(
            LogVisitante.fecha_ingreso >= fecha_inicio_obj,
            LogVisitante.fecha_ingreso <= fecha_fin_obj
        ).count()
        
        # Visitas por estado
        en_instalaciones = LogVisitante.query.filter(
            LogVisitante.fecha_ingreso >= fecha_inicio_obj,
            LogVisitante.fecha_ingreso <= fecha_fin_obj,
            LogVisitante.estado_visita == 'EN_INSTALACIONES'
        ).count()
        
        salieron = LogVisitante.query.filter(
            LogVisitante.fecha_ingreso >= fecha_inicio_obj,
            LogVisitante.fecha_ingreso <= fecha_fin_obj,
            LogVisitante.estado_visita == 'SALIO'
        ).count()
        
        # Visitas de hoy
        hoy = datetime.now().date()
        visitas_hoy = LogVisitante.query.filter_by(fecha_ingreso=hoy).count()
        en_instalaciones_hoy = LogVisitante.query.filter_by(
            fecha_ingreso=hoy,
            estado_visita='EN_INSTALACIONES'
        ).count()
        
        return jsonify({
            'success': True,
            'periodo': {
                'fecha_inicio': fecha_inicio_obj.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin_obj.strftime('%Y-%m-%d')
            },
            'estadisticas': {
                'total_visitas': total_visitas,
                'en_instalaciones': en_instalaciones,
                'salieron': salieron,
                'hoy': {
                    'total': visitas_hoy,
                    'en_instalaciones': en_instalaciones_hoy
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
