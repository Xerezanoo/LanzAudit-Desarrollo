from app import mail
from flask_mail import Message
from models import User

def newRequest(user, reason, message):
    admins = User.query.filter_by(role='Admin').all()
    for admin in admins:
        msg = Message(
            subject="Nueva solicitud de recuperación de contraseña",
            recipients=[admin.email]
        )
        msg.body = f"""
        Se ha recibido una nueva solicitud de recuperación de contraseña en el sistema:

        Usuario: {user.username}
        Motivo: {reason}
        Mensaje adicional: {message}
        
        Revisa y completa la solicitud y ponte en contacto por un medio seguro con el usuario afectado para facilitarle la nueva contraseña.

        LanzAudit
        """
        mail.send(msg)

def resolvedRequest(user):
    msg = Message(
        subject="Tu recuperación de contraseña ha sido completada",
        recipients=[user.email]
    )
    msg.body = f"""
    Hola {user.username},

    Tu solicitud de recuperación de contraseña ha sido completada, nos pondremos en contacto lo antes posible para facilitarte la nueva contraseña.
    
    LanzAudit
    """
    mail.send(msg)
