# models.py

# Importación de las librerías necesarias
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inicialización de SQLAlchemy
db = SQLAlchemy()   # Objeto que interactúa con la BD

# Modelo de la tabla 'user' (Usuarios)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum('Admin', 'Worker', 'Analyst', name='role_enum'), nullable=False)
    password_reset_requested = db.Column(db.Boolean, default=False)
    password_reset_requested_at = db.Column(db.DateTime, nullable=True, default=None)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Usuario {self.username}>' # Usuario LanzAdmin

# Modelo de la tabla 'scan' (Escaneos)
class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scan_type = db.Column(db.Enum('Nmap', 'WPScan', name='scan_type_enum'), nullable=False)
    scan_parameters = db.Column(db.JSON, nullable=True)
    status = db.Column(db.Enum('Completado', 'Fallido', name='status_enum'), default='Fallido')
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relación con el modelo 'User' (un usuario puede tener muchos escaneos). Con esta línea podremos acceder a los escaneos de un usuario desde el objeto User con User.scans:
    user = db.relationship('User', backref=db.backref('scans', lazy=True))

    def __repr__(self):
        return f'<Escaneo {self.id} - {self.scan_type}>'    # Escaneo 1 - Puertos

# Modelo de la tabla 'scan_results' (Resultado de los escaneos)
class ScanResults(db.Model):
    __tablename__ = 'scan_results'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    result = db.Column(db.JSON, nullable=True, default=None)
    ttl = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relación con el modelo 'Scan' (un escaneo puede tener muchos resultados). Con esta línea podremos acceder a los resultados de los escaneos desde el objeto Scan con Scan.results:
    scan = db.relationship('Scan', backref=db.backref('results', lazy=True))

    def __repr__(self):
        return f'<Resultado {self.id} - Escaneo {self.scan_id}>' # Resultado 1 - Escaneo 1
