"""
========================================
SERVICIO DE CORREO ELECTRÓNICO
Sistema de Control de Visitantes
========================================
"""

from flask_mail import Message
from app.extensions import mail
from flask import current_app, render_template_string
from datetime import datetime


def enviar_correo(destinatario, asunto, cuerpo_html):
    """
    Envía un correo electrónico
    
    Args:
        destinatario (str): Email del destinatario
        asunto (str): Asunto del correo
        cuerpo_html (str): Contenido HTML del correo
    """
    try:
        msg = Message(
            asunto,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario]
        )
        msg.html = cuerpo_html
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo: {str(e)}")
        return False


def enviar_correo_registro_funcionario(usuario_data):
    """
    Envía correo al funcionario confirmando su registro pendiente
    
    Args:
        usuario_data (dict): Datos del usuario registrado
    """
    asunto = "Registro Recibido - Sistema de Control de Visitantes"
    
    cuerpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2d7a3e 0%, #1e5a2d 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; 
                      border-radius: 0 0 10px 10px; font-size: 12px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #2d7a3e; 
                      color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .info-box {{ background: #fff; border-left: 4px solid #2d7a3e; padding: 15px; 
                        margin: 20px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; 
                       margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Registro Recibido</h1>
                <p>Sistema de Control de Visitantes</p>
            </div>
            
            <div class="content">
                <h2>Hola, {usuario_data['primer_nombre']} {usuario_data['primer_apellido']}</h2>
                
                <p>Tu solicitud de registro como funcionario ha sido recibida exitosamente.</p>
                
                <div class="info-box">
                    <h3>📋 Datos de Registro:</h3>
                    <p><strong>Usuario:</strong> {usuario_data['usuario']}</p>
                    <p><strong>Correo:</strong> {usuario_data['dir_correo']}</p>
                    <p><strong>Rol:</strong> Usuario Funcionario</p>
                    <p><strong>Fecha de registro:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <div class="warning">
                    <h3>⏳ Esperando Aprobación</h3>
                    <p>Tu cuenta está pendiente de activación por parte del administrador del sistema.</p>
                    <p>Recibirás un correo de confirmación una vez que tu cuenta sea activada.</p>
                </div>
                
                <p>Si tienes alguna pregunta, por favor contacta al administrador del sistema.</p>
            </div>
            
            <div class="footer">
                <p>Supertiendas Cañaveral SAS</p>
                <p>© {datetime.now().year} - Sistema de Control de Visitantes</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return enviar_correo(usuario_data['dir_correo'], asunto, cuerpo)


def enviar_correo_notificacion_admin(usuario_data, admin_email):
    """
    Envía correo al administrador notificando nueva solicitud de registro
    
    Args:
        usuario_data (dict): Datos del usuario que se registró
        admin_email (str): Email del administrador
    """
    asunto = "Nueva Solicitud de Registro - Funcionario"
    
    cuerpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e5a2d 0%, #2d7a3e 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; 
                      border-radius: 0 0 10px 10px; font-size: 12px; }}
            .info-box {{ background: #fff; border-left: 4px solid #007bff; padding: 15px; 
                        margin: 20px 0; }}
            .urgent {{ background: #fff3cd; border-left: 4px solid #ff6b6b; padding: 15px; 
                      margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            td:first-child {{ font-weight: bold; width: 40%; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Nueva Solicitud de Registro</h1>
                <p>Se requiere tu aprobación</p>
            </div>
            
            <div class="content">
                <div class="urgent">
                    <h3>⚠️ Acción Requerida</h3>
                    <p>Un nuevo funcionario se ha registrado y está esperando tu aprobación para acceder al sistema.</p>
                </div>
                
                <div class="info-box">
                    <h3>👤 Datos del Solicitante:</h3>
                    <table>
                        <tr>
                            <td>Nombre Completo:</td>
                            <td>{usuario_data['primer_nombre']} {usuario_data.get('segundo_nombre', '')} 
                                {usuario_data['primer_apellido']} {usuario_data.get('segundo_apellido', '')}</td>
                        </tr>
                        <tr>
                            <td>Identificación:</td>
                            <td>{usuario_data['tipo_identificacion']}: {usuario_data['num_identificacion']}</td>
                        </tr>
                        <tr>
                            <td>Correo:</td>
                            <td>{usuario_data['dir_correo']}</td>
                        </tr>
                        <tr>
                            <td>Teléfono:</td>
                            <td>{usuario_data['num_telefono']}</td>
                        </tr>
                        <tr>
                            <td>Usuario (login):</td>
                            <td>{usuario_data['usuario']}</td>
                        </tr>
                        <tr>
                            <td>Rol:</td>
                            <td>Usuario Funcionario</td>
                        </tr>
                        <tr>
                            <td>Fecha de solicitud:</td>
                            <td>{datetime.now().strftime('%d/%m/%Y %H:%M')}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="text-align: center; margin-top: 30px;">
                    <strong>Ingresa al panel de administración para aprobar o rechazar esta solicitud.</strong>
                </p>
            </div>
            
            <div class="footer">
                <p>Supertiendas Cañaveral SAS</p>
                <p>© {datetime.now().year} - Sistema de Control de Visitantes</p>
                <p>Este es un correo automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return enviar_correo(admin_email, asunto, cuerpo)


def enviar_correo_cuenta_activada(usuario_data):
    """
    Envía correo al funcionario notificando que su cuenta fue activada
    
    Args:
        usuario_data (dict): Datos del usuario activado
    """
    asunto = "✅ Cuenta Activada - Sistema de Control de Visitantes"
    
    cuerpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #218838 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; 
                      border-radius: 0 0 10px 10px; font-size: 12px; }}
            .success-box {{ background: #d4edda; border-left: 4px solid #28a745; padding: 20px; 
                           margin: 20px 0; border-radius: 5px; }}
            .info-box {{ background: #fff; border-left: 4px solid #007bff; padding: 15px; 
                        margin: 20px 0; }}
            .button {{ display: inline-block; padding: 15px 40px; background: #28a745; 
                      color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; 
                      font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ ¡Cuenta Activada!</h1>
                <p>Ya puedes acceder al sistema</p>
            </div>
            
            <div class="content">
                <h2>Hola, {usuario_data['primer_nombre']} {usuario_data['primer_apellido']}</h2>
                
                <div class="success-box">
                    <h3>🎉 ¡Buenas noticias!</h3>
                    <p style="font-size: 16px; margin: 0;">Tu cuenta ha sido <strong>activada exitosamente</strong> por el administrador.</p>
                </div>
                
                <p>Ahora puedes acceder al Sistema de Control de Visitantes con tus credenciales.</p>
                
                <div class="info-box">
                    <h3>🔑 Tus Credenciales:</h3>
                    <p><strong>Usuario:</strong> {usuario_data['usuario']}</p>
                    <p><strong>Rol:</strong> Usuario Funcionario</p>
                    <p style="margin-top: 15px; color: #666; font-size: 14px;">
                        <em>Usa la contraseña que registraste durante tu solicitud.</em>
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5000" class="button">Acceder al Sistema</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Nota:</strong> Si olvidaste tu contraseña, contacta al administrador del sistema.
                </p>
            </div>
            
            <div class="footer">
                <p>Supertiendas Cañaveral SAS</p>
                <p>© {datetime.now().year} - Sistema de Control de Visitantes</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return enviar_correo(usuario_data['dir_correo'], asunto, cuerpo)


def enviar_correo_cuenta_rechazada(usuario_data, motivo=""):
    """
    Envía correo al funcionario notificando que su solicitud fue rechazada
    
    Args:
        usuario_data (dict): Datos del usuario rechazado
        motivo (str): Motivo del rechazo (opcional)
    """
    asunto = "Solicitud de Registro - Sistema de Control de Visitantes"
    
    motivo_html = f"<p><strong>Motivo:</strong> {motivo}</p>" if motivo else ""
    
    cuerpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; 
                      border-radius: 0 0 10px 10px; font-size: 12px; }}
            .notice-box {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; 
                          margin: 20px 0; border-radius: 5px; }}
            .info-box {{ background: #d1ecf1; border-left: 4px solid #0c5460; padding: 15px; 
                        margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Solicitud de Registro</h1>
                <p>Sistema de Control de Visitantes</p>
            </div>
            
            <div class="content">
                <h2>Hola, {usuario_data['primer_nombre']} {usuario_data['primer_apellido']}</h2>
                
                <div class="notice-box">
                    <h3>Actualización de tu Solicitud</h3>
                    <p>Lamentablemente, tu solicitud de registro no ha sido aprobada en este momento.</p>
                    {motivo_html}
                </div>
                
                <div class="info-box">
                    <h3>¿Necesitas más información?</h3>
                    <p>Si tienes dudas o deseas recibir más información sobre esta decisión, 
                       por favor contacta al administrador del sistema.</p>
                </div>
                
                <p>Puedes intentar registrarte nuevamente si lo deseas.</p>
            </div>
            
            <div class="footer">
                <p>Supertiendas Cañaveral SAS</p>
                <p>© {datetime.now().year} - Sistema de Control de Visitantes</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return enviar_correo(usuario_data['dir_correo'], asunto, cuerpo)


def enviar_notificacion_autorizacion_aprobada(autorizacion_data, empresa_data, destinatario_email, pdf_ruta=None):
    """
    Envía notificación email cuando una autorización SST es aprobada

    Args:
        autorizacion_data (dict): to_dict() de AutorizacionSST
        empresa_data (dict): to_dict() de EmpresaContratista
        destinatario_email (str): Email de la empresa contratista
        pdf_ruta (str): Ruta al archivo PDF para adjuntar (opcional)
    """
    consecutivo = f"SST-{datetime.now().year}-{autorizacion_data['id']:04d}"
    asunto = f"Autorización SST Aprobada — {consecutivo}"

    nombre_empresa = empresa_data.get('razon_social') or empresa_data.get('nombre_completo_persona_natural', '')

    cuerpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .info-box {{ background: white; padding: 15px; border-left: 4px solid #1565c0; margin: 15px 0; }}
            .success {{ background: #e8f5e9; border: 2px solid #4caf50; padding: 15px; text-align: center;
                       border-radius: 8px; margin: 15px 0; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center;
                      border-radius: 0 0 10px 10px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Autorización SST Aprobada</h1>
                <p>{consecutivo}</p>
            </div>
            <div class="content">
                <div class="success">
                    <h2 style="color: #2e7d32; margin: 0;">Autorización Aprobada</h2>
                    <p>La autorización de ingreso para contratistas ha sido aprobada.</p>
                </div>

                <div class="info-box">
                    <p><strong>Empresa:</strong> {nombre_empresa}</p>
                    <p><strong>Labor:</strong> {autorizacion_data.get('labor', '-')}</p>
                    <p><strong>Válida desde:</strong> {autorizacion_data.get('fecha_inicio', '-')}</p>
                    <p><strong>Válida hasta:</strong> {autorizacion_data.get('fecha_fin', '-')}</p>
                    <p><strong>Sede:</strong> {autorizacion_data.get('sede_id', 'Todas')}</p>
                </div>

                <p>Los empleados de su empresa pueden presentarse en portería con documento de identidad.
                El operador de seguridad verificará la autorización vigente en el sistema.</p>

                <p><em>Si tiene alguna duda, comuníquese con el área SST.</em></p>
            </div>
            <div class="footer">
                <p>SUPERTIENDAS CAÑAVERAL SAS — Sistema de Gestión SST</p>
                <p>&copy; {datetime.now().year}</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        msg = Message(
            asunto,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario_email]
        )
        msg.html = cuerpo

        # Adjuntar PDF si existe (con validación de sandbox)
        if pdf_ruta:
            import os
            base_storage = os.path.normpath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'uploads')
            )
            pdf_full_path = os.path.normpath(os.path.join(base_storage, pdf_ruta))
            if pdf_full_path.startswith(base_storage + os.sep) and os.path.exists(pdf_full_path):
                with open(pdf_full_path, 'rb') as f:
                    msg.attach(
                        os.path.basename(pdf_ruta),
                        'application/pdf',
                        f.read()
                    )

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error enviando notificación SST aprobada: {str(e)}")
        return False


def enviar_notificacion_autorizacion_rechazada(autorizacion_data, empresa_data, destinatario_email):
    """
    Envía notificación email cuando una autorización SST es rechazada
    """
    consecutivo = f"SST-{datetime.now().year}-{autorizacion_data['id']:04d}"
    asunto = f"Autorización SST Rechazada — {consecutivo}"

    nombre_empresa = empresa_data.get('razon_social') or empresa_data.get('nombre_completo_persona_natural', '')

    cuerpo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #c62828 0%, #b71c1c 100%);
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .info-box {{ background: white; padding: 15px; border-left: 4px solid #c62828; margin: 15px 0; }}
            .alert {{ background: #ffebee; border: 2px solid #ef5350; padding: 15px; text-align: center;
                     border-radius: 8px; margin: 15px 0; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center;
                      border-radius: 0 0 10px 10px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Autorización SST Rechazada</h1>
                <p>{consecutivo}</p>
            </div>
            <div class="content">
                <div class="alert">
                    <h2 style="color: #c62828; margin: 0;">Autorización Rechazada</h2>
                    <p>La solicitud de autorización requiere correcciones.</p>
                </div>

                <div class="info-box">
                    <p><strong>Empresa:</strong> {nombre_empresa}</p>
                    <p><strong>Labor:</strong> {autorizacion_data.get('labor', '-')}</p>
                </div>

                <p>Por favor comuníquese con el área SST de Supertiendas Cañaveral
                para conocer los motivos del rechazo y realizar las correcciones necesarias.</p>
            </div>
            <div class="footer">
                <p>SUPERTIENDAS CAÑAVERAL SAS — Sistema de Gestión SST</p>
                <p>&copy; {datetime.now().year}</p>
            </div>
        </div>
    </body>
    </html>
    """

    return enviar_correo(destinatario_email, asunto, cuerpo)
