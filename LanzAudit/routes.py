# routes.py

# Importación de las librerías y objetos necesarios
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash
from flask_login import login_user
from models import User
from app import app, db # App Flask

# Ruta para la página de inicio de sesión, la 1º que se mostrará al entrar a la app
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

# Ruta para la página de recuperación de contraseña
@app.route('/password-recovery')
def passwordRecovery():
    return render_template("password-recovery.html")

# Ruta para el Dashboard (página principal después de iniciar sesión)
@app.route('/dashboard')
def home():
    return render_template("index.html")

# Ruta para la página de preguntas frecuentes (FAQ)
@app.route('/faq')
def faq():
    return render_template("faq.html")

# Ruta para la página de la licencia del software
@app.route('/license')
def license():
    return render_template("license.html")

# Ruta para la página de gestión de usuarios (solo para administradores)
@app.route('/manage-users')
def manageUsers():
    return render_template('manage-users.html')
