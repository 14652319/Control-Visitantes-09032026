"""
========================================
SERVICIO DE GENERACIÓN PDF
Formato SC-SST-FOR-015 — Autorización SST
========================================
"""

import os
from html import escape
from io import BytesIO
from datetime import datetime
from xhtml2pdf import pisa
from flask import current_app
from app.extensions import db
from app.utils.logger import logger


def generar_pdf_autorizacion(autorizacion, empresa, empleados, planilla_vigente=None, sede=None):
    """
    Genera PDF del formato SC-SST-FOR-015

    Args:
        autorizacion: AutorizacionSST instance
        empresa: EmpresaContratista instance
        empleados: list[EmpleadoContratista] — empleados de la empresa
        planilla_vigente: PlanillaSS instance (opcional)
        sede: Sede instance (opcional)

    Returns:
        dict: {'success': bool, 'ruta': str, 'nombre': str}
    """
    try:
        # 1. Generar número consecutivo
        consecutivo = f"SST-{datetime.now().year}-{autorizacion.id:04d}"

        # 2. Datos empresa
        if empresa.tipo_persona == 'JURIDICA':
            nombre_empresa = empresa.razon_social
            doc_empresa = f"NIT: {empresa.nit}-{empresa.digito_verificacion}"
        else:
            nombre_empresa = empresa.nombre_completo_persona_natural
            doc_empresa = f"{empresa.tipo_identificacion}: {empresa.num_identificacion}"

        # 3. Filas de empleados
        filas_empleados = ""
        for i, emp in enumerate(empleados, 1):
            # Obtener certificados vigentes
            certs = []
            for cert in emp.certificados:
                if cert.fecha_vencimiento is None or cert.fecha_vencimiento >= datetime.now().date():
                    abrev = {
                        'ALTURAS': 'Alt',
                        'ELECTRICO': 'Elec',
                        'ESPACIOS_CONFINADOS': 'Esp.C',
                        'OTRO': 'Otro'
                    }.get(cert.tipo_certificado, cert.tipo_certificado[:4])
                    certs.append(abrev)

            filas_empleados += f"""
            <tr>
                <td style="padding: 6px; border: 1px solid #ccc; text-align: center;">{i}</td>
                <td style="padding: 6px; border: 1px solid #ccc;">{escape(emp.nombre_completo)}</td>
                <td style="padding: 6px; border: 1px solid #ccc;">{escape(emp.tipo_id)} {escape(emp.num_id)}</td>
                <td style="padding: 6px; border: 1px solid #ccc;">{escape(emp.cargo) if emp.cargo else '-'}</td>
                <td style="padding: 6px; border: 1px solid #ccc;">{', '.join(certs) if certs else '-'}</td>
            </tr>"""

        # 4. Datos planilla
        info_planilla = "Sin planilla vigente registrada"
        if planilla_vigente:
            info_planilla = f"""
            <p><strong>Periodo:</strong> {planilla_vigente.periodo}</p>
            <p><strong>Fecha pago:</strong> {planilla_vigente.fecha_pago.strftime('%d/%m/%Y') if planilla_vigente.fecha_pago else '-'}</p>
            <p><strong>Vigencia hasta:</strong> {planilla_vigente.vigencia_fin.strftime('%d/%m/%Y') if planilla_vigente.vigencia_fin else '-'}</p>
            """

        # 5. Nombre sede
        nombre_sede = sede.descripcion_sede if sede else 'TODAS LAS SEDES'

        # 6. Template HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; color: #333; margin: 30px; }}
                .header {{ text-align: center; border-bottom: 3px solid #2d7a3e; padding-bottom: 15px; margin-bottom: 20px; }}
                .header h1 {{ color: #2d7a3e; margin: 0; font-size: 16px; }}
                .header h2 {{ color: #555; margin: 5px 0; font-size: 13px; }}
                .header .formato {{ color: #888; font-size: 10px; }}
                .consecutivo {{ text-align: right; font-size: 14px; font-weight: bold; color: #2d7a3e; }}
                .seccion {{ margin: 15px 0; }}
                .seccion h3 {{ background: #2d7a3e; color: white; padding: 6px 12px; font-size: 12px; margin: 0 0 8px 0; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
                th {{ background: #f0f0f0; padding: 6px; border: 1px solid #ccc; text-align: left; font-weight: bold; }}
                .dato {{ margin: 4px 0; }}
                .dato strong {{ color: #555; }}
                .firma {{ margin-top: 40px; text-align: center; }}
                .firma .linea {{ border-top: 1px solid #333; width: 250px; margin: 0 auto; padding-top: 5px; }}
                .footer {{ margin-top: 30px; text-align: center; font-size: 9px; color: #999; border-top: 1px solid #ddd; padding-top: 10px; }}
                .validez {{ background: #fff8e1; border: 2px solid #f9a825; padding: 10px; text-align: center; margin: 15px 0; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SUPERTIENDAS CAÑAVERAL SAS</h1>
                <h2>AUTORIZACIÓN DE INGRESO — CONTRATISTAS</h2>
                <p class="formato">Formato: SC-SST-FOR-015</p>
            </div>

            <p class="consecutivo">No. {consecutivo}</p>
            <p class="dato"><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y')} &nbsp;&nbsp; <strong>Hora:</strong> {datetime.now().strftime('%H:%M')}</p>

            <div class="seccion">
                <h3>EMPRESA CONTRATISTA</h3>
                <p class="dato"><strong>{doc_empresa}</strong></p>
                <p class="dato"><strong>Nombre:</strong> {nombre_empresa}</p>
                <p class="dato"><strong>Teléfono:</strong> {empresa.telefono or '-'} &nbsp;&nbsp; <strong>Email:</strong> {empresa.email or '-'}</p>
            </div>

            <div class="seccion">
                <h3>PLANILLA DE SEGURIDAD SOCIAL</h3>
                {info_planilla}
            </div>

            <div class="seccion">
                <h3>LABOR AUTORIZADA</h3>
                <p>{escape(autorizacion.labor)}</p>
            </div>

            <div class="seccion">
                <h3>EMPLEADOS AUTORIZADOS</h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 30px;">#</th>
                            <th>Nombre Completo</th>
                            <th>Documento</th>
                            <th>Cargo</th>
                            <th>Certificaciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_empleados if filas_empleados else '<tr><td colspan="5" style="text-align:center; padding:10px;">Sin empleados registrados</td></tr>'}
                    </tbody>
                </table>
            </div>

            <div class="seccion">
                <h3>SEDE AUTORIZADA</h3>
                <p>{escape(nombre_sede)}</p>
            </div>

            <div class="validez">
                Válido desde {autorizacion.fecha_inicio.strftime('%d/%m/%Y')} hasta {autorizacion.fecha_fin.strftime('%d/%m/%Y')}
            </div>

            <div class="firma">
                <p><strong>Aprobado por:</strong></p>
                <br><br>
                <div class="linea"></div>
                <p>Administrador SST</p>
            </div>

            <div class="footer">
                <p>SUPERTIENDAS CAÑAVERAL SAS — Sistema de Gestión SST</p>
                <p>Documento generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </body>
        </html>
        """

        # 7. Crear directorio si no existe
        year_folder = str(datetime.now().year)
        storage_path = os.path.join(
            current_app.config.get('PDF_STORAGE_FOLDER', 'uploads/autorizaciones_sst'),
            year_folder
        )
        os.makedirs(storage_path, exist_ok=True)

        # 8. Generar PDF
        nombre_archivo = f"{consecutivo}.pdf"
        ruta_completa = os.path.join(storage_path, nombre_archivo)

        result = BytesIO()
        pdf = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result)

        if pdf.err:
            logger.error(f"Error generando PDF: {pdf.err}")
            return {'success': False, 'error': 'Error al generar PDF'}

        # 9. Guardar archivo
        with open(ruta_completa, 'wb') as f:
            f.write(result.getvalue())

        # 10. Ruta relativa para guardar en DB
        ruta_relativa = os.path.join('autorizaciones_sst', year_folder, nombre_archivo)

        logger.info(f"PDF generado: {consecutivo} para autorización #{autorizacion.id}")

        return {
            'success': True,
            'ruta': ruta_relativa,
            'nombre': nombre_archivo,
            'consecutivo': consecutivo
        }

    except Exception as e:
        logger.error(f"Error generando PDF autorización #{autorizacion.id}: {e}")
        return {'success': False, 'error': str(e)}
