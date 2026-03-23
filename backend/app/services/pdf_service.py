"""
========================================
SERVICIO DE GENERACIÓN PDF
Formato SC-SST-FOR-015 — Autorización SST
========================================
"""

import os
import base64
from html import escape
from io import BytesIO
from datetime import datetime
from xhtml2pdf import pisa
from flask import current_app
from app.utils.logger import logger


MESES_ES = [
    '', 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE',
]

DIAS_ES = [
    '', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE',
    'OCHO', 'NUEVE', 'DIEZ', 'ONCE', 'DOCE', 'TRECE', 'CATORCE',
    'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO', 'DIECINUEVE',
    'VEINTE', 'VEINTIUNO', 'VEINTIDÓS', 'VEINTITRÉS', 'VEINTICUATRO',
    'VEINTICINCO', 'VEINTISÉIS', 'VEINTISIETE', 'VEINTIOCHO', 'VEINTINUEVE',
    'TREINTA', 'TREINTA Y UNO',
]

TRABAJOS_LABELS = {
    'trabajo_altura':               'trabajo en alturas',
    'trabajo_energias_peligrosas':  'trabajo con energías peligrosas',
    'trabajo_espacios_confinados':  'trabajo en espacios confinados',
    'trabajo_caliente':             'trabajo en caliente',
    'trabajo_izaje_cargas':         'izaje de cargas',
    'trabajo_excavacion':           'excavación',
    'trabajo_sustancias_quimicas':  'manejo de sustancias químicas',
}


def _logo_base64():
    """Devuelve el logo como data URI base64, o cadena vacía si no existe."""
    try:
        # current_app.root_path = backend/app — subir dos niveles al raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(current_app.root_path))
        logo_path = os.path.join(project_root, 'frontend', 'assets', 'img', 'logo-canaveral.png')
        if not os.path.isfile(logo_path):
            # fallback: subir solo un nivel (si root_path ya es backend/)
            logo_path = os.path.join(os.path.dirname(current_app.root_path), 'frontend', 'assets', 'img', 'logo-canaveral.png')
        if os.path.isfile(logo_path):
            with open(logo_path, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            return f'data:image/png;base64,{data}'
    except Exception:
        pass
    return ''


def _ciudad():
    """Ciudad de la empresa desde configuración, o valor genérico."""
    try:
        from app.models.configuracion_sistema import ConfiguracionSistema
        return ConfiguracionSistema.obtener_valor('ciudad_empresa', 'la ciudad')
    except Exception:
        return 'la ciudad'


def generar_pdf_autorizacion(autorizacion, empresa, empleados, planilla_vigente=None, sede=None):
    """
    Genera PDF del formato SC-SST-FOR-015.

    Args:
        autorizacion: AutorizacionSST instance
        empresa:      EmpresaContratista instance
        empleados:    list[EmpleadoContratista] (fallback si no hay EmpleadoAutorizacion)
        planilla_vigente: PlanillaSS instance (opcional)
        sede:         Sede instance (opcional)
    Returns:
        dict: {'success': bool, 'ruta': str, 'nombre': str, 'consecutivo': str}
    """
    try:
        consecutivo = f"SST-{datetime.now().year}-{autorizacion.id:04d}"

        # ── Empresa ──────────────────────────────────────────────────────────
        if empresa.tipo_persona == 'JURIDICA':
            nombre_empresa = escape(empresa.razon_social or '')
            doc_empresa    = f"NIT: {empresa.nit}-{empresa.digito_verificacion or ''}"
        else:
            nombre_empresa = escape(empresa.nombre_completo_persona_natural or '')
            doc_empresa    = f"{empresa.tipo_identificacion}: {empresa.num_identificacion}"

        # ── Sede ─────────────────────────────────────────────────────────────
        nombre_sede = escape(sede.descripcion_sede if sede else 'SUPERTIENDAS CAÑAVERAL EN GENERAL')

        # ── Cobertura SS ─────────────────────────────────────────────────────
        if planilla_vigente and planilla_vigente.vigencia_fin:
            vf = planilla_vigente.vigencia_fin
            fi = planilla_vigente.fecha_pago or autorizacion.fecha_inicio
            fi_str = fi.strftime('%d/%m/%Y') if fi else '—'
            vf_str = vf.strftime('%d/%m/%Y')
            cobertura_html = (
                f"<strong>{fi_str} – {vf_str}</strong>"
                f"&nbsp;<span style='color:#c0392b;font-weight:bold;'>(Vence)</span>"
            )
        else:
            fi_str = autorizacion.fecha_inicio.strftime('%d/%m/%Y') if autorizacion.fecha_inicio else '—'
            vf_str = autorizacion.fecha_fin.strftime('%d/%m/%Y') if autorizacion.fecha_fin else '—'
            cobertura_html = f"<strong>{fi_str} – {vf_str}</strong>"

        # ── Logo ─────────────────────────────────────────────────────────────
        logo_uri  = _logo_base64()
        logo_img  = f'<img src="{logo_uri}" style="height:55px;" />' if logo_uri else ''
        logo_small = f'<img src="{logo_uri}" style="height:40px;" />' if logo_uri else ''

        # ── Empleados + permisos ─────────────────────────────────────────────
        # Usar EmpleadoAutorizacion (que tiene los permisos) en lugar del listado general
        ea_list = list(autorizacion.empleados_autorizacion)
        ea_map  = {ea.empleado_id: ea for ea in ea_list if ea.empleado_id}

        # Lista de empleados a mostrar (preferir los de la autorización)
        emp_lista = [ea.empleado for ea in ea_list if ea.empleado] or empleados

        filas_empleados = ''
        bloques_notas   = []

        for i, emp in enumerate(emp_lista, 1):
            filas_empleados += f"""
            <tr>
                <td style="padding:4px 7px;border:1px solid #888;text-align:center;">{i}</td>
                <td style="padding:4px 7px;border:1px solid #888;">{escape(emp.nombre_completo)}</td>
                <td style="padding:4px 7px;border:1px solid #888;">{escape(emp.tipo_id)} {escape(emp.num_id)}</td>
            </tr>"""

            ea = ea_map.get(emp.id)
            if ea:
                autorizados   = [lbl for key, lbl in TRABAJOS_LABELS.items() if getattr(ea, key, False)]
                no_autorizados = [lbl for key, lbl in TRABAJOS_LABELS.items() if not getattr(ea, key, False)]
                if ea.trabajo_otro:
                    autorizados.append(ea.trabajo_otro.lower())

                nombre_emp = escape(emp.nombre_completo)
                if autorizados:
                    bloques_notas.append(
                        f"<p style='margin:3px 0;'>"
                        f"<strong>NOTA:</strong> {nombre_emp} está autorizado para realizar: "
                        f"<span style='color:#1a7a3e;'>{', '.join(autorizados)}</span>.</p>"
                    )
                if no_autorizados:
                    bloques_notas.append(
                        f"<p style='margin:3px 0;'>"
                        f"<strong>NOTA:</strong> {nombre_emp} "
                        f"<span style='color:#c0392b;'>NO está autorizado para realizar: "
                        f"{', '.join(no_autorizados)}</span>.</p>"
                    )

        notas_html = '\n'.join(bloques_notas)

        # ── Fecha de cierre en texto ──────────────────────────────────────────
        hoy = autorizacion.fecha_autorizacion or datetime.now().date()
        dia_txt = DIAS_ES[hoy.day] if 1 <= hoy.day <= 31 else str(hoy.day)
        mes_txt = MESES_ES[hoy.month]
        anno    = hoy.year

        # ── Aprobador ─────────────────────────────────────────────────────────
        aprobador_nombre = 'Administrador SST'
        aprobador_cargo  = 'Seguridad y Salud en el Trabajo'
        if autorizacion.aprobado_by:
            try:
                from app.models.usuario import Usuario
                u = Usuario.query.get(autorizacion.aprobado_by)
                if u:
                    aprobador_nombre = escape(
                        (u.primer_nombre or '') + ' ' + (u.primer_apellido or '') or u.usuario
                    ).strip()
            except Exception:
                pass

        ciudad = _ciudad()

        # ═══════════════════════════════════════════════════════════════════
        # HTML → PDF
        # ═══════════════════════════════════════════════════════════════════
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 11px; color: #1a1a1a; margin: 22px 28px; }}
  table.hdr {{ width:100%; border-collapse:collapse; border:1.5px solid #333; margin-bottom:6px; }}
  table.hdr td {{ border:1px solid #555; padding:4px 8px; vertical-align:middle; }}
  .titulo {{ text-align:center; font-size:13px; font-weight:bold; text-transform:uppercase;
             text-decoration:underline; margin:10px 0 12px 0; letter-spacing:0.5px; }}
  .campo {{ margin:5px 0; display:table; width:100%; }}
  .campo .lbl {{ font-weight:bold; display:table-cell; width:220px; vertical-align:top; padding-right:6px; }}
  .campo .val {{ display:table-cell; vertical-align:top; }}
  table.emps {{ width:100%; border-collapse:collapse; margin:8px 0; font-size:10.5px; }}
  table.emps th {{ background:#2d7a3e; color:#fff; padding:5px 8px; text-align:left; border:1px solid #2d7a3e; }}
  table.emps td {{ border:1px solid #888; padding:5px 8px; }}
  .notas {{ margin:6px 0; font-size:10.5px; line-height:1.5; }}
  .recuerden {{ margin:10px 0; font-size:10px; text-align:justify; line-height:1.5; }}
  .recuerden strong {{ font-size:10.5px; }}
  .cierre {{ margin-top:10px; font-size:10.5px; line-height:1.8; }}
  .firmas {{ width:100%; margin-top:45px; border-collapse:collapse; }}
  .firmas td {{ vertical-align:bottom; text-align:center; padding:0 20px; width:50%; }}
  .firma-linea {{ border-top:1px solid #333; margin-top:30px; padding-top:5px; font-size:10px; line-height:1.7; }}
  .consecutivo-box {{ text-align:right; font-size:13px; font-weight:bold; color:#2d7a3e; margin-bottom:2px; }}
</style>
</head>
<body>

<!-- ENCABEZADO SC-SST-FOR-015 -->
<table class="hdr">
  <tr>
    <td rowspan="3" style="width:150px; text-align:center; padding:6px;">
      {logo_img}
      <div style="font-size:8.5px; font-weight:bold; color:#2d7a3e; margin-top:3px;">SUPERTIENDAS CAÑAVERAL SAS</div>
    </td>
    <td colspan="2" style="text-align:center; font-weight:bold; font-size:11px;">
      FORMATO AUTORIZACION DE INGRESO CONTRATISTAS
    </td>
  </tr>
  <tr>
    <td style="font-size:10px;"><strong>Código:</strong> SC-SST-FOR-015</td>
    <td style="font-size:10px;"><strong>Versión:</strong> 01</td>
  </tr>
  <tr>
    <td colspan="2" style="font-size:10px;"><strong>Página:</strong> 1 de 1</td>
  </tr>
</table>

<div class="consecutivo-box">No. {consecutivo}</div>

<div class="titulo">Autorizacion Ingreso Contratista</div>

<div class="campo"><span class="lbl">ENTIDAD:</span><span class="val">{nombre_empresa}</span></div>
<div class="campo"><span class="lbl">NIT:</span><span class="val">{doc_empresa}</span></div>
<div class="campo"><span class="lbl">OBRA AUTORIZADA:</span><span class="val">{escape(autorizacion.labor)}</span></div>
<div class="campo"><span class="lbl">SEDE:</span><span class="val">{nombre_sede}</span></div>
<div class="campo">
  <span class="lbl">COBERTURA<br>SEGURIDAD SOCIAL:</span>
  <span class="val">{cobertura_html}</span>
</div>

<p style="margin:12px 0 6px 0; font-size:10.5px; text-align:justify; line-height:1.5;">
Una vez validada la documentación entregada por la entidad en mención, se notifica
<strong>AUTORIZACION</strong> de los siguientes trabajadores para que realicen actividades
a nivel del piso o suelo.
</p>

<table class="emps">
  <thead>
    <tr>
      <th style="width:30px;">#</th>
      <th>NOMBRE COMPLETO</th>
      <th>No Identificación</th>
    </tr>
  </thead>
  <tbody>
    {filas_empleados if filas_empleados else
      '<tr><td colspan="3" style="text-align:center;padding:8px;color:#888;">Sin empleados registrados</td></tr>'}
  </tbody>
</table>

{'<div class="notas">' + notas_html + '</div>' if notas_html else ''}

<div class="recuerden">
<strong>RECUERDEN</strong> Es Obligación del contratista dotar a cada uno de sus trabajadores de las
herramientas y de todos los elementos de protección personal necesarios para realizar sus actividades
laborales entendiéndose, así como los equipos de protección contra caídas según lo dispuesto en la
resolución 4272 de 2021.
</div>

<div class="cierre">
  <p>Para constancia se firma en {ciudad}, a los <strong>{dia_txt}</strong> días del mes de
  <strong>{mes_txt}</strong> de <strong>{anno}</strong></p>
  <p>Cordialmente;</p>
</div>

<table class="firmas">
  <tr>
    <td>
      <div class="firma-linea">
        <strong>{aprobador_nombre}</strong><br>
        {aprobador_cargo}
      </div>
    </td>
    <td>
      <div class="firma-linea">
        {logo_small}
        <br><strong>SUPERTIENDAS CAÑAVERAL S.A.S.</strong><br>
        NIT. 805.028.041-4<br>
        <strong>SEGURIDAD Y SALUD EN EL TRABAJO</strong>
      </div>
    </td>
  </tr>
</table>

<div style="margin-top:25px; text-align:center; font-size:8px; color:#aaa;
            border-top:1px solid #ddd; padding-top:5px;">
  SUPERTIENDAS CAÑAVERAL SAS — Sistema de Gestión SST &nbsp;|&nbsp;
  Formato SC-SST-FOR-015 &nbsp;|&nbsp;
  Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>

</body>
</html>"""

        # ── Guardar archivo ───────────────────────────────────────────────────
        year_folder = str(datetime.now().year)
        storage_path = os.path.join(
            current_app.config.get('PDF_STORAGE_FOLDER', 'uploads/autorizaciones_sst'),
            year_folder
        )
        os.makedirs(storage_path, exist_ok=True)

        nombre_archivo = f"{consecutivo}.pdf"
        ruta_completa  = os.path.join(storage_path, nombre_archivo)

        result = BytesIO()
        pdf    = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result)

        if pdf.err:
            logger.error(f"Error xhtml2pdf: {pdf.err}")
            return {'success': False, 'error': 'Error al generar PDF'}

        with open(ruta_completa, 'wb') as f:
            f.write(result.getvalue())

        ruta_relativa = os.path.join('autorizaciones_sst', year_folder, nombre_archivo)
        logger.info(f"PDF generado: {consecutivo} para autorización #{autorizacion.id}")

        return {
            'success': True,
            'ruta': ruta_relativa,
            'nombre': nombre_archivo,
            'consecutivo': consecutivo,
        }

    except Exception as e:
        logger.error(f"Error generando PDF autorización #{autorizacion.id}: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


