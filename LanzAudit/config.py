# config.py

# Importación de las librerías necesarias
import os   # Para interactuar con el sistema
from dotenv import load_dotenv  # Para cargar las variables de entorno del .env

# Carga de las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la aplicación Flask
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')    # Recupera la clave del .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') # Recupera la URI del .env
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Mejora el rendimiento al dejar de seguir las modificaciones de los objetos de la BD
    MAIL_SERVER = os.getenv('MAIL_SERVER')  # Servidor de correo
    MAIL_PORT = int(os.getenv('MAIL_PORT'))  # Puerto para TLS
    MAIL_USE_TLS = True    # Activar TLS
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Correo (para autenticarme)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Contraseña de la cuenta
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')  # El correo desde el que se enviarán los mensajes (puede ser el mismo que MAIL_USERNAME o distinto)
