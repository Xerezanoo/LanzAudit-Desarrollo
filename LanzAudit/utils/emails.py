from app import mail
from flask_mail import Message
from flask import render_template
from models import User
from datetime import datetime

def newRequest(user, reason, message):
    msg = Message(
        subject="Nueva solicitud de recuperación de contraseña",
        recipients=[admin.email for admin in User.query.filter_by(role='Admin').all()]
    )
    msg.html = render_template('emails/new-request.html', username=user.username, reason=reason, message=message)
    mail.send(msg)

def resolvedRequest(user):
    try:
        msg = Message(
            subject="Tu recuperación de contraseña ha sido completada",
            recipients=[user.email]
        )
        msg.html = render_template('emails/resolved-request.html', username=user.username, current_year=datetime.now().year)
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
