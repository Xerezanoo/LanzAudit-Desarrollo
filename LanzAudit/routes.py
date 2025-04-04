# routes.py

# Importación de las librerías y objetos necesarios
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User
from app import app, mail # App Flask
from flask_mail import Message


# Ruta para la página de inicio de sesión, la 1º que se mostrará al entrar a la app. Si no existe el usuario LanzAdmin, se redigirá a la página de configuración inicial del mismo
@app.route('/', methods=['GET', 'POST'])
def login():
    if not User.query.filter_by(username="LanzAdmin").first():
        return redirect(url_for('setupAdmin'))
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Correo electrónico o contraseña incorrectos', 'danger')
    return render_template('login.html')

# Ruta para la configuración inicial del usuario LanzAdmin y la creación del mismo
@app.route('/setup-admin', methods=['GET', 'POST'])
def setupAdmin():
    adminExists = User.query.filter_by(username="LanzAdmin").first()
    if adminExists:
        flash('El usuario Administrador LanzAdmin ya está creado', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = 'LanzAdmin'
        
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico introducido ya está registrado. Usa otro diferente', 'danger')
            return redirect(url_for('setupAdmin'))
        
        lanzAdmin = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='Admin'
        )
        
        db.session.add(lanzAdmin)
        db.session.commit()
        
        flash('Usuario LanzAdmin creado con éxito. Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template("setup-admin.html")

# Ruta para la página de recuperación de contraseña
@app.route('/password-recovery')
def passwordRecovery():
    return render_template("password-recovery.html")

# Ruta para el Dashboard (página principal después de iniciar sesión)
@app.route('/dashboard')
@login_required
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

# Ruta para el logout (cerrar sesión)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Se ha cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/send_test_email')
def send_test_email():
    msg = Message('Test Email', recipients=['juangarcialanzarendon@gmail.com'])
    msg.body = 'Este es un correo de prueba.'
    mail.send(msg)
    return 'Correo enviado con éxito'