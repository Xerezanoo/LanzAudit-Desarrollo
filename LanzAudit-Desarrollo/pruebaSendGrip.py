from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()
sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
message = Mail(
    from_email=os.getenv('MAIL_SENDER'),
    to_emails='juangarcialanzarendon@gmail.com',
    subject='Prueba directa',
    html_content='<p>Funciona bien</p>'
)
response = sg.send(message)
print(response.status_code)