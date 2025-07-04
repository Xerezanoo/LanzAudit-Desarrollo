import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models import User

def sendEmail(to_email, subject, body):
    message = Mail(
        from_email=os.getenv('MAIL_SENDER'),
        to_emails=to_email,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)
    except Exception as error:
        pass

def newRequest(user, reason, message):
    admins = User.query.filter_by(role='Admin').all()
    for admin in admins:
        subject = "Nueva solicitud de recuperación de contraseña"
        body = f"""
        <p>Se ha recibido una nueva solicitud de recuperación de contraseña en el sistema:</p>
        <p><strong>Usuario:</strong> {user.username}<br>
        <strong>Motivo:</strong> {reason}<br>
        <strong>Mensaje adicional:</strong> {message}</p>
        <p>Revisa y completa la solicitud y ponte en contacto por un medio seguro con el usuario afectado para facilitarle la nueva contraseña.</p>
        <p><em>LanzAudit</em></p>
        """
        sendEmail(admin.email, subject, body)

def resolvedRequest(user):
    subject = "Tu recuperación de contraseña ha sido completada"
    body = f"""
    <p>Hola {user.username},</p>
    <p>Tu solicitud de recuperación de contraseña ha sido completada, nos pondremos en contacto lo antes posible para facilitarte la nueva contraseña.</p>
    <p><em>LanzAudit</em></p>
    """
    sendEmail(user.email, subject, body)