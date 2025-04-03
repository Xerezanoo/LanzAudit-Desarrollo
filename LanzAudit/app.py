# app.py

# Importación de las librerías y objetos necesarios
from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate

# Inicialización de la aplicación Flask y carga de la configuración desde Config
app = Flask(__name__)
app.config.from_object(Config)

# Conexión de la base de datos con la aplicación Flask e inicialización del sistema de migración
db.init_app(app)
migrate = Migrate(app, db)

# Importación de todas las rutas del proyecto
from routes import *

# Ejecución de la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
