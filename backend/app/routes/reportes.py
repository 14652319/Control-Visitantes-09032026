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
    """Genera un reporte de visitas en un rango de fechas"""
    try:
        # Obtener parámetros
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        sede_id = request.args.get('sede_id', type=int)
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
        elif sede_id:
            query = query.filter_by(sede_id=sede_id)
        
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


@bp.route('/visitas/excel', methods=['POST'])
@role_required('usuario_master', 'usuario_operador')
def exportar_visitas_excel():
    """Exporta visitas seleccionadas a un archivo Excel"""
    try:
        data = request.get_json()
        visitas_ids = data.get('visitas_ids', [])
        
        if not visitas_ids:
            return jsonify({
                'success': False,
                'message': 'Debe seleccionar al menos una visita'
            }), 400
        
        # Obtener visitas
        visitas = LogVisitante.query.filter(LogVisitante.id.in_(visitas_ids)).all()
        
        if not visitas:
            return jsonify({
                'success': False,
                'message': 'No se encontraron visitas'
            }), 404
        
        # Verificar acceso por sede
        if current_user.rol == 'usuario_operador':
            for visita in visitas:
                if visita.sede_id != current_user.sede_id:
                    return jsonify({
                        'success': False,
                        'message': 'No tiene acceso a algunas de las visitas seleccionadas'
                    }), 403
        
        # Crear DataFrame
        data_excel = []
        for v in visitas:
            data_excel.append({
                'ID': v.id,
                'Fecha Ingreso': v.fecha_ingreso.strftime('%d/%m/%Y'),
                'Hora Ingreso': v.hora_ingreso.strftime('%H:%M:%S'),
                'Fecha Salida': v.fecha_salida.strftime('%d/%m/%Y') if v.fecha_salida else '',
                'Hora Salida': v.hora_salida.strftime('%H:%M:%S') if v.hora_salida else '',
                'Tipo ID': v.tipo_identificacion,
                'Num ID': v.num_identificacion,
                'Nombres': f"{v.primer_nombre} {v.segundo_nombre or ''}".strip(),
                'Apellidos': f"{v.primer_apellido} {v.segundo_apellido or ''}".strip(),
                'Teléfono': v.num_telefono,
                'Correo': v.dir_correo,
                'Empresa': v.empresa,
                'NIT Empresa': v.nit_empresa,
                'Dependencia': v.descripcion_dependencia,
                'Funcionario Recibe': v.funcionario_recibe,
                'Observaciones': v.observaciones1 or '',
                'Carnet': v.numero_carnet or '',
                'Estado': v.estado_visita,
                'Sede': v.sede.descripcion_sede if v.sede else ''
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
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        
        # Registrar evento
        LogEvento.registrar_evento(
            tipo_evento='REPORTE_GENERADO',
            descripcion=f'Reporte Excel generado con {len(visitas)} visitas',
            usuario=current_user,
            datos_adicionales={'cantidad_visitas': len(visitas)},
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
