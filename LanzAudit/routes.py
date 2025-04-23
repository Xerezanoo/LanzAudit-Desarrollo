# routes.py

# Importación de las librerías y objetos necesarios
import os
from flask import render_template, redirect, url_for, flash, request, abort
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User, Scan, ScanResult
from app import app, mail
from flask_mail import Message
from sqlalchemy import func
from PIL import Image
from io import BytesIO
import base64
from scanners.nmapScanner import runNmapScan, validatePorts

# Rutas para el manejo de errores
# Error 400 - Solicitud incorrecta
@app.errorhandler(400)
def badRequest(error):
    return render_template('error/400.html'), 400

# Error 401 - No autorizado
@app.errorhandler(401)
def unauthorized(error):
    return render_template('error/401.html'), 401

# Error 403 - Aceso denegado
@app.errorhandler(403)
def forbidden(error):
    return render_template('error/403.html'), 403

# Error 404 - Página no encontrada
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('error/404.html'), 404

# Error 405 - Método no permitido
@app.errorhandler(405)
def methodNotAllowed(error):
    return render_template('error/405.html'), 405

# Error 500 - Error interno del servidor
@app.errorhandler(500)
def internalServerError(error):
    return render_template('error/500.html'), 500

# Error 502 - Gateway incorrecto
@app.errorhandler(502)
def badGateway(error):
    return render_template('error/502.html'), 502

# Error 503 - Servicio no disponible
@app.errorhandler(503)
def serviceUnavailable(error):
    return render_template('error/503.html'), 503

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
@app.route('/password-recovery', methods=['GET', 'POST'])
def passwordRecovery():
    if request.method == 'POST':
        email = request.form['email']
        motivo = request.form['motivo']
        mensaje = request.form['mensaje']

        user = User.query.filter_by(email=email).first()

        if user:
            if user.password_reset_requested:
                flash('Ya hay una solicitud pendiente para este usuario.', 'warning')
                return redirect(url_for('login'))

            user.password_reset_requested = True
            user.password_reset_requested_at = func.current_timestamp()
            db.session.commit()

            admins = User.query.filter_by(role='Admin').all()
            for admin in admins:
                msg = Message('Nueva solicitud de recuperación de contraseña', recipients=[admin.email])
                msg.body = f"Usuario: {user.username}\nMotivo: {motivo}\nMensaje adicional: {mensaje}"
                mail.send(msg)

            flash('Solicitud de recuperación enviada correctamente.', 'success')
            return redirect(url_for('login'))

        flash('No se encontró ningún usuario con ese correo electrónico', 'danger')
        return redirect(url_for('login'))
    return render_template("password-recovery.html")

# Ruta para confirmar que se ha completado la recuperación de la contraseña de un usuario
@app.route('/resolve-reset-request/<int:user_id>', methods=['GET', 'POST'])
@login_required
def resolveResetRequest(user_id):
    if current_user.role != 'Admin':
        abort(403)
        
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        
        if new_password:
            user.password_hash = generate_password_hash(new_password)
            user.password_reset_requested = False
            user.password_reset_requested_at = None
            db.session.commit()
            flash('Contraseña cambiada y solicitud resuelta', 'success')
            return redirect(url_for('manageUsers'))

        flash('No se ha modificado la contraseña. La solicitud no ha sido resuelta', 'warning')
        return redirect(url_for('manageUsers'))

    return render_template('admin/resolve-reset-request.html', user=user)

# Ruta para el Dashboard (página principal después de iniciar sesión)
@app.route('/dashboard')
@login_required
def home():
    return render_template("index.html")

# Ruta para la página de gestión de usuarios (solo para administradores)
@app.route('/manage-users')
@login_required
def manageUsers():
    if current_user.role != 'Admin':
        abort(403)
        
    users = User.query.all()
    return render_template('admin/manage-users.html', users=users)

# Ruta para añadir un usuario desde la página de gestión de usuarios (solo para administradores)
@app.route('/manage-users/add', methods=['GET', 'POST'])
@login_required
def addUser():
    if current_user.role != 'Admin':
        abort(403)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        existing_user = db.session.query(User).filter((User.username == username) | (User.email == email)).first()
        
        if existing_user:
            flash("El nombre de usuario o el correo electrónico ya están registrados", "danger")
            return redirect(url_for('addUser'))
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()

        flash(f'Usuario {username} añadido correctamente', 'success')
        return redirect(url_for('manageUsers'))

    return render_template('admin/add-user.html')

# Ruta para editar un usuario desde la página de gestión de usuarios (solo para administradores)
@app.route('/manage-users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editUser(user_id):
    if current_user.role != 'Admin':
        abort(403)

    user = User.query.get_or_404(user_id)
    
    if user.username == 'LanzAdmin' and request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        existing_email = db.session.query(User).filter((User.email == email)).first()
        
        if existing_email:
            flash("El correo electrónico ya está registrado", "danger")
            return redirect(url_for('editUser', user_id=user.id))
        
        if email:
            user.email = email
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash('Usuario LanzAdmin actualizado correctamente', 'success')
        return redirect(url_for('manageUsers'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        existing_user = db.session.query(User).filter((User.username == username) | (User.email == email)).filter(User.id != user.id).first()
        
        if existing_user:
            flash("El nombre de usuario o el correo electrónico ya están registrados", "danger")
            return redirect(url_for('editUser', user_id=user.id))
        
        user.username = username
        user.email = email
        user.role = role
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash(f'Usuario {username} actualizado correctamente', 'success')
        return redirect(url_for('manageUsers'))

    return render_template('admin/edit-user.html', user=user)

# Ruta para eliminar un usuario desde la página de gestión de usuarios (solo para administradores)
@app.route('/manage-users/delete/<int:user_id>', methods=['POST'])
@login_required
def deleteUser(user_id):
    if current_user.role != 'Admin':
        abort(403)

    user = User.query.get_or_404(user_id)
    
    if user.username == 'LanzAdmin':
        flash('No puedes eliminar al usuario LanzAdmin', 'danger')
        return redirect(url_for('manageUsers'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {user.username} eliminado correctamente', 'success')
    return redirect(url_for('manageUsers'))

# Ruta para la página de preguntas frecuentes (FAQ)
@app.route('/faq')
@login_required
def faq():
    return render_template("faq.html")

# Ruta para la página de la licencia del software
@app.route('/license')
@login_required
def license():
    return render_template("license.html")

# Ruta para la página de modificación del perfil de los usuarios
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        cropped_data = request.form.get('cropped_image')

        if new_email != user.email and new_username != user.username:
            existing_email = User.query.filter_by(email=new_email).first()
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_email and existing_user:
                flash('El correo electrónico y el nombre de usuario ya están registrados', 'danger')
                return redirect(url_for('profile'))

        if new_email != user.email:
            existing_email = User.query.filter_by(email=new_email).first()
            if existing_email:
                flash('El correo electrónico ya está registrado', 'danger')
                return redirect(url_for('profile'))
            user.email = new_email

        if user.username != 'LanzAdmin' and new_username != user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash('El nombre de usuario ya está en uso', 'danger')
                return redirect(url_for('profile'))
            user.username = new_username

        if cropped_data:
            try:
                header, encoded = cropped_data.split(",", 1)
                image_data = base64.b64decode(encoded)
                image = Image.open(BytesIO(image_data))

                filename = f"user_{user.id}.png"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                user.profile_picture = filename
            except Exception as error:
                flash('Error al procesar la imagen recortada', 'danger')
                print(error)
                return redirect(url_for('profile'))

        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('profile'))

    if user.profile_picture:
        image_url = url_for('static', filename='profile_pics/' + user.profile_picture)
    else:
        image_url = url_for('static', filename='profile_pics/default.png')

    return render_template('profile.html', image_url=image_url)

# Ruta para eliminar la foto de perfil y volver a tener la predeterminada
@app.route('/remove-profile-picture', methods=['POST'])
@login_required
def removeProfilePicture():
    user = current_user
    
    if user.profile_picture is not None:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        user.profile_picture = None
        db.session.commit()
        flash('Foto de perfil eliminada correctamente', 'success')
    else:
        flash('No tienes una foto de perfil personalizada', 'info')

    return redirect(url_for('profile'))

# Ruta para el logout (cerrar sesión)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Se ha cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))




# Ruta para la página de selección de escaneo
@app.route('/scan', methods=['GET'])
@login_required
def scan():
    if current_user.role not in ['Admin', 'Worker']:
        abort(403)
    return render_template('scan/scan.html')

# Ruta para redirigir a los formularios específicos
@app.route('/scan_type', methods=['GET'])
@login_required
def scan_type():
    if current_user.role not in ['Admin', 'Worker']:
        abort(403)

    scan_type = request.args.get('scan_type')
    if scan_type == 'nmap':
        return redirect(url_for('nmapScan'))
    elif scan_type == 'wpscan':
        return redirect(url_for('wpscanScan'))
    else:
        flash("Selección no válida", 'danger')
        return redirect(url_for('scan'))

# Ruta para la ejecución de los escaneos con Nmap
@app.route('/scan/nmap', methods=['GET', 'POST'])
@login_required
def nmapScan():
    if current_user.role not in ['Admin', 'Worker']:
        abort(403)
        
    if request.method == 'POST':
        target = request.form.get('target')
        scan_type = request.form.get('scan_type')
        ports = request.form.get('ports') if scan_type == 'custom' else None

        # Validar los puertos si es un escaneo personalizado
        if scan_type == 'custom' and ports:
            if not validatePorts(ports):
                flash('Formato de puertos no válido', 'danger')
                return redirect(url_for('nmapScan'))

        # Ejecutar el escaneo
        try:
            hosts, result = runNmapScan(target, scan_type, ports)

            # Guardar en la base de datos
            new_scan = Scan(
                user_id=current_user.id,
                scan_type='Nmap',
                scan_parameters={"target": target, "scan_type": scan_type, "ports": ports},
                status='Completado'
            )
            db.session.add(new_scan)
            db.session.commit()

            scan_result = ScanResult(
                scan_id=new_scan.id,
                result=result
            )
            db.session.add(scan_result)
            db.session.commit()

            flash('Escaneo realizado con éxito', 'success')
            return render_template('scan/nmap-scan.html', result=result, target=target, scan_type=scan_type)

        except Exception as error:
            flash(f'Error al ejecutar el escaneo: {str(error)}', 'danger')
            return redirect(url_for('nmapScan'))

    return render_template('scan/nmap-scan.html')


# Ruta para la ejecución de los escaneos con WPScan
@app.route('/scan/wpscan', methods=['GET', 'POST'])
def wpscanScan():
    return render_template('scan/wpscan-scan.html')

