# app.py

# Importación de las librerías y objetos necesarios
from flask import Flask
from config import Config
from models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()

# Inicialización de la aplicación Flask y carga de la configuración desde Config
app = Flask(__name__)
app.config.from_object(Config)

# Conexión de la base de datos con la aplicación Flask e inicialización del sistema de migración
db.init_app(app)
migrate = Migrate(app, db)

# Inicialización de Flask-Login, definición de la vista de login a la que se redirigirá cuando no haya sesión activa (no se esté autenticado) y manejador del error que aparece cuando se intenta acceder a una página en la que es obligatorio estar autenticado
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Por favor, inicia sesión para acceder a esta página', 'warning')
    return redirect(url_for('login'))

# Inicialización de Flask-Mail
# mail = Mail(app)

# Importación de todas las rutas del proyecto
from routes import *

# Ejecución de la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
