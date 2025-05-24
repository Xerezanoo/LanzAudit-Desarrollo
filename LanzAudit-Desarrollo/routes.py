# routes.py

# Importación de las librerías y objetos necesarios
import os
from flask import render_template, redirect, url_for, flash, request, abort, send_file, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func
from PIL import Image
from io import BytesIO
import base64
from collections import Counter
from datetime import datetime
from models import db, User, Scan, ScanResults
from app import app
from scanners.nmapScanner import runNmapScan, validatePorts
from scanners.wpscanScanner import runWPScan
from utils.stats import topOpenPorts, PORT_SERVICE_NAMES, PORT_ICONS, totalVulns, topThemes, topPlugins, vulnerablePlugins, vulnerableThemes
from utils.ttl import detectOS
from utils.emails import newRequest, resolvedRequest
from utils.pdf import generateSummary, generatePDF

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
        reason = request.form['motivo']
        message = request.form['mensaje']

        user = User.query.filter_by(email=email).first()

        if user:
            if user.password_reset_requested:
                flash('Ya hay una solicitud pendiente para este usuario.', 'warning')
                return redirect(url_for('login'))

            user.password_reset_requested = True
            user.password_reset_requested_at = func.current_timestamp()
            db.session.commit()

            # Llamamos a la función newRequest para notificar a los administradores
            newRequest(user, reason, message)

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

            # Llamamos a la función resolvedRequest para notificar al usuario
            resolvedRequest(user)

            flash('Contraseña cambiada y solicitud resuelta', 'success')
            return redirect(url_for('manageUsers'))

        flash('No se ha modificado la contraseña. La solicitud no ha sido resuelta', 'warning')
        return redirect(url_for('manageUsers'))

    return render_template('admin/resolve-reset-request.html', user=user)

# Ruta para el Dashboard (página principal después de iniciar sesión)
@app.route('/dashboard')
@login_required
def home():
    # Total de escaneos
    total_scans = Scan.query.count()
    
    # Escaneos por tipo (Nmap y WPScan)
    nmap_scans = Scan.query.filter_by(scan_type='Nmap').count()
    wpscan_scans = Scan.query.filter_by(scan_type='WPScan').count()
    
    # Últimos 5 escaneos
    latest_scans = Scan.query.order_by(Scan.created_at.desc()).limit(5).all()

    # Actividad reciente (últimos escaneos con su estado)
    activity = []
    for scan in latest_scans:
        activity.append({
            'date': scan.created_at.strftime('%d/%m/%Y %H:%M'),
            'target': scan.scan_parameters.get('target'),
            'type': scan.scan_type,
            'status': scan.status
        })
    
    # Todos los escaneos (para estadísticas)
    all_scans = Scan.query.all()

    # IP/Host más escaneado
    targets = [scan.scan_parameters.get('target') for scan in all_scans if scan.scan_parameters.get('target')]
    most_common = Counter(targets).most_common(1)
    most_scanned_target = most_common[0][0] if most_common else 'N/A'

    # Porcentaje de escaneos completados
    completed = sum(1 for scan in all_scans if scan.status == 'Completado')
    failed = sum(1 for scan in all_scans if scan.status == 'Fallido')
    total_done = completed + failed
    completed_percentage = int((completed / total_done) * 100) if total_done > 0 else 0

    # Escaneos por día (para gráfico de líneas)
    date_counts = Counter(scan.created_at.strftime('%d/%m') for scan in all_scans)
    # Ordenar por fecha
    sorted_dates = sorted(date_counts.keys(), key=lambda x: datetime.strptime(x, "%d/%m"))
    scan_dates = sorted_dates
    scan_counts = [date_counts[date] for date in sorted_dates]
    
    # Total de vulnerabilidades encontradas con WPScan (de versiones de WordPress, de temas, de plugins...)
    total_vulns=totalVulns()
    
    return render_template("index.html", total_scans=total_scans, nmap_scans=nmap_scans, wpscan_scans=wpscan_scans, latest_scans=latest_scans, activity=activity, most_scanned_target=most_scanned_target, completed_percentage=completed_percentage, scan_dates=scan_dates, scan_counts=scan_counts, total_vulns=total_vulns)

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
@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if current_user.role not in ['Admin', 'Worker']:
        abort(403)

    # Si es un GET, solo mostramos el formulario
    return render_template('scan/scan.html')

# Ruta para la ejecución de los escaneos con Nmap
@app.route('/scan/nmap', methods=['GET', 'POST'])
@login_required
def nmapScan():
    if current_user.role not in ['Admin', 'Worker']:
        abort(403)

    if request.method == 'POST':
        target = request.form.get('target')
        subtype = request.form.get('subtype')
        ports = request.form.get('ports') if subtype == 'custom' else None

        # Validar puertos si es personalizado
        if subtype == 'custom' and ports:
            if not validatePorts(ports):
                flash('Formato de puertos no válido', 'danger')
                return redirect(url_for('nmapScan'))

        try:
            # Ejecutar escaneo
            hosts, result, ttl = runNmapScan(target, subtype, ports)

            # Guardar escaneo exitoso
            new_scan = Scan(
                user_id=current_user.id,
                scan_type='Nmap',
                scan_parameters={"target": target, "subtype": subtype, "ports": ports},
                status='Completado'
            )
            db.session.add(new_scan)
            db.session.commit()

            scan_result = ScanResults(
                scan_id=new_scan.id,
                result=result,
                ttl=ttl
            )
            db.session.add(scan_result)
            db.session.commit()

            flash('Escaneo realizado con éxito', 'success')
            return render_template('scan/nmap-scan.html', result=result, target=target, subtype=subtype)

        except Exception as error:
            # Guardar escaneo fallido
            new_scan = Scan(
                user_id=current_user.id,
                scan_type='Nmap',
                scan_parameters={"target": target, "subtype": subtype, "ports": ports},
                error_message=str(error)
            )
            db.session.add(new_scan)
            db.session.commit()

            flash('Escaneo fallido', 'danger')
            return render_template('scan/nmap-scan.html', result=None, target=target, subtype=subtype)

    return render_template('scan/nmap-scan.html')



# Ruta para la ejecución de los escaneos con WPScan
@app.route('/scan/wpscan', methods=['GET', 'POST'])
@login_required
def WPScan():
    if current_user.role not in ['Admin', 'Worker']:
        abort(403)
        
    if request.method == 'POST':
        target = request.form.get('target')
        subtype = request.form.get('subtype')
        options = request.form.get('options') if subtype == "custom" else None
        
        try:
            # Ejecutar WPScan
            result = runWPScan(target, subtype, options)
            
            if result.get('scan_aborted'):
                raise ValueError(result.get('scan_aborted'))
            
            if result.get('not_fully_configured'):
                raise ValueError("La web está en modo instalación de WordPress. No se puede escanear.")
            
            if result.get('error'):
                raise ValueError(result.get('error'))
            
            # Crear escaneo
            new_scan = Scan(
                user_id=current_user.id,
                scan_type="WPScan",
                scan_parameters={"target": target, "subtype": subtype, "options": options},
                status="Completado"
            )
            db.session.add(new_scan)
            db.session.commit()
            # Guardar la ruta del archivo en el registro
            scan_result = ScanResults(
                scan_id=new_scan.id,
                result=result
            )
            db.session.add(scan_result)
            db.session.commit()
            flash('Escaneo realizado con éxito', 'success')
            return render_template('scan/wpscan-scan.html', result=result, target=target, subtype=subtype, options=options)          

        except Exception as error:
            # Guardar escaneo fallido
            new_scan = Scan(
                user_id=current_user.id,
                scan_type='WPScan',
                scan_parameters={"target": target, "subtype": subtype, "options": options},
                error_message=str(error)
            )
            db.session.add(new_scan)
            db.session.commit()

            flash('Escaneo fallido', 'danger')
            return render_template('scan/wpscan-scan.html', result=None, target=target, subtype=subtype, options=options)

    return render_template('scan/wpscan-scan.html')



# Ruta para mostrar los resultados y las estadísticas de los escaneos
@app.route('/stats', methods=['GET'])
@login_required
def stats():
    # Obtener el parámetro de ordenación desde la URL (por defecto es 'date_desc')
    sort_by = request.args.get('sort', 'date_desc')

    # Diccionario que mapea las opciones de ordenación a las columnas reales de la base de datos
    sort_options = {
        'date_desc': Scan.created_at.desc(),
        'date_asc': Scan.created_at.asc(),
        'type': Scan.scan_type,
        'user': Scan.user_id 
    }

    # Por defecto, ordenamos por fecha descendente
    order = sort_options.get(sort_by, Scan.created_at.desc()) 

    # Obtener los escaneos ordenados según el parámetro 'sort'
    scans = Scan.query.order_by(order).all()
    
    # Contar el total de escaneos
    total_scans = Scan.query.count()
    
    # Contar el total de escaneos completados
    completed_scans = Scan.query.filter_by(status='Completado').count()
    
    # Contar el total de escaneos fallidos
    failed_scans = Scan.query.filter_by(status='Fallido').count()

    # Último escaneo realizado
    last_scan = Scan.query.order_by(Scan.created_at.desc()).first()
    
    # Escaneos realizados con Nmap
    total_nmap = Scan.query.filter_by(scan_type='Nmap').count()

    # Escaneos realizados con WPScan
    total_wpscan = Scan.query.filter_by(scan_type='WPScan').count()
    
    # Usar la función topOpenPorts() que está en el archivo stats.py en la carpeta utils/ para obtener los 5 puertos que más veces se han encontrado abiertos
    top_ports = topOpenPorts()
    
    # Ahora hacemos uso del diccionario PORT_SERVICE_NAMES que hemos creado en util/stats.py también para sustituir los números de los puertos por el nombre del servicio
    top_ports_named = [
    {
        "port": port,
        "label": PORT_SERVICE_NAMES.get(port, f"Puerto {port}"),
        "count": count
    }
    for port, count in top_ports
    ]
    
    # Y por último, ponemos las estadísticas de WPScan
    top_themes = topThemes()
    top_plugins = topPlugins()
    vulnerable_plugins = vulnerablePlugins()
    vulnerable_themes = vulnerableThemes()

    return render_template('scan/stats.html', scans=scans, total_scans=total_scans, completed_scans=completed_scans, failed_scans=failed_scans, last_scan=last_scan, total_nmap=total_nmap, total_wpscan=total_wpscan, top_ports=top_ports_named, PORT_ICONS=PORT_ICONS, sort_by=sort_by, top_themes=top_themes, top_plugins=top_plugins, vulnerable_plugins=vulnerable_plugins, vulnerable_themes=vulnerable_themes)

# Ruta para ver los detalles de un escaneo Nmap en concreto
@app.route('/stats/nmap/<int:scan_id>')
@login_required
def nmapDetail(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    error = scan.error_message
    scan_result = ScanResults.query.filter_by(scan_id=scan_id).first()

    if scan.scan_type != 'Nmap':
        flash('Tipo de escaneo desconocido.', 'warning')
        return redirect(url_for('stats'))
    
    if scan.status == 'Fallido':
        return render_template('scan/nmap-detail.html', scan=scan, error=error)
        
    result = scan_result.result

    estimatedOS = detectOS(scan_result.ttl)
    return render_template('scan/nmap-detail.html', scan=scan, result=result, estimatedOS=estimatedOS)

# Ruta para ver los detalles de un escaneo WPScan en concreto
@app.route('/stats/wpscan/<int:scan_id>')
@login_required
def wpscanDetail(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    error = scan.error_message
    scan_result = ScanResults.query.filter_by(scan_id=scan_id).first()

    if scan.scan_type != 'WPScan':
        flash('Tipo de escaneo desconocido.', 'warning')
        return redirect(url_for('stats'))

    if scan.status == 'Fallido':
        return render_template('scan/wpscan-detail.html', scan=scan, error=error)

    result = scan_result.result
    return render_template('scan/wpscan-detail.html', scan=scan, result=result)

# Ruta para los informes generados por la IA
@app.route('/ai-report/<int:scan_id>')
@login_required
def aiReport(scan_id):
    try:
        file = f"summary-{scan_id}.pdf"
        report_path = os.path.join(os.getcwd(), "static", "reports", file)

        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True)

        scan_result = ScanResults.query.filter_by(scan_id=scan_id).first()

        if not scan_result or not scan_result.result:
            return jsonify({'error': 'No se encontró el resultado del escaneo'}), 404
        
        result = scan_result.result

        summary = generateSummary(result)
        file = generatePDF(summary, scan_id)

        return send_file(file, as_attachment=True)

    except Exception as error:
        return jsonify({'error': str(error)}), 500

# Ruta para eliminar un escaneo
@app.route('/stats/delete/<int:scan_id>', methods=['POST'])
@login_required
def deleteScan(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    
    if current_user.role != 'Admin' and scan.user_id != current_user.id:
        abort(403)
    
    try:
        # Eliminar los resultados del escaneo antes de eliminar el escaneo
        ScanResults.query.filter_by(scan_id=scan_id).delete()
        db.session.delete(scan)
        db.session.commit()
        flash(f'Escaneo {scan_id} eliminado correctamente', 'success')
    except Exception as error:
        db.session.rollback()
        flash('Error al eliminar el escaneo', 'danger')

    return redirect(url_for('stats'))