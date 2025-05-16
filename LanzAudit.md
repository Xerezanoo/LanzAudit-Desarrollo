## Organización Documentación
### 1. Introducción
#### 1.1. Introducción
- Qué es LanzAudit: una herramienta web para realizar escaneos automatizados de seguridad sobre sistemas.
- Público objetivo: administradores de sistemas, pentesters, técnicos en ciberseguridad, etc.
- Justificación: necesidad de tener una herramienta centralizada, fácil de usar y extensible.

#### 1.2. Finalidad
- Facilitar escaneos de seguridad desde una interfaz web.
- Automatizar tareas comunes de pentesting.
- Permitir gestión de usuarios, resultados y análisis.

#### 1.3. Objetivos
- Implementar escaneos de puertos y WordPress en una primera fase.
- Crear un panel de administración completo y seguro.
- Ofrecer resultados claros y organizados.
- Tener un sistema escalable a nuevos tipos de escaneo.

#### 1.4. Medios necesarios
- Hardware: PC con Linux (Kubuntu).
- Software: Python, Flask, MariaDB, Nginx, Gunicorn, herramientas como Nmap, WPScan, etc.
- Otros: Cropper.js, AdminLTE, servicios de correo, etc.

#### 1.5. Planificación
- Herramienta usada: Taiga con metodología Kanban.
- Fases del desarrollo: planificación, desarrollo backend, frontend, integración, pruebas, documentación.
- Tiempo estimado por fase.
- Desvíos del plan original (si los hubo).

### 2. Realización del Proyecto
#### 2.1. Trabajos realizados
- Estructura del proyecto.
- Registro y login con roles.
- Gestión de usuarios.
- Implementación de escaneos y resultados.
- Formularios, validaciones, envío de correos.
- Gestión de imágenes de perfil.
- Seguridad y protección contra errores.

#### 2.2. Problemas encontrados
- Problemas con integraciones externas (por ejemplo, WPScan o permisos con Nmap).
- Manejo de imágenes con Cropper.js.
- Bugs con validaciones o subida de archivos.
- Seguridad de la base de datos y constraints (como el problema con DELETE y claves foráneas).
- Manejo de errores HTTP personalizados.

#### 2.3. Modificaciones sobre el proyecto planteado inicialmente
- Inicialmente iba a usar Django, pero decidiste usar Flask por su ligereza.
- Añadiste recuperación de contraseña por correo.
- Implementaste gestión de usuarios más avanzada de lo que pensabas.
- Algunas funcionalidades previstas se han pospuesto a mejoras futuras.

#### 2.4. Posibles mejoras al proyecto
- Añadir más tipos de escaneos (Joomla, Drupal, etc.).
- Escaneos periódicos programados.
- Exportación de resultados.
- Dashboard con estadísticas más detalladas.
- Sistema de logs.
- Mejora del sistema de permisos.

#### 2.5. Bibliografía
- Documentación oficial de Flask, Nmap, WPScan...
- Stack Overflow, foros, artículos técnicos.
- Apuntes de clase o materiales docentes.

---

## Framework Backend:
Flask --> ¿Por qué Flask en vez de Django?


## Plantilla Dashboard Flask (Flask-adminator)
He encontrado un proyecto en GitHub con una plantilla de Panel muy parecida a lo que necesito:
https://github.com/app-generator/flask-adminator/tree/master

Para montarla:
1. Clonamos el repositorio
2. Entramos en él
3. Activamos nuestro entorno virtual. Voy a usar el propio de Python.
Como estoy en una distribución basada en Debian, lo instalo con `sudo apt install python3-venv -y`, lo creo con `python3 -m venv venv` y lo activo con `source venv/bin/activate` --> Este paso es MUY IMPORTANTE
4. Instalamos las dependencias con `pip3 install -r requirements.txt`
5. `export FLASK_APP=run.py`
6. `export FLASK_DEBUG=True` para trabajar y cuando lo vayamos a montar en el servidor para todos los usuarios, hacemos `export FLASK_DEBUG=False` para que no salgan los mensajes de error y no revelemos rutas sensibles.
7. Montamos la base de datos y exportamos las variables de entorno de la base de datos (ver más abajo)
8. Iniciamos la app en `http://127.0.0.1:5000/` con `flask run` (siempre con el entorno virtual activado, porque si no no tendremos las dependencias necesarias para iniciarla)
### Modificaciones
#### Archivo `gunicorn-cfg.py` temporal
Cambiamos el bind a `0.0.0.0:8080`, que es el puerto donde vamos a levantar la app en DigitalOcean
#### Migrar base de datos SQLite a MariaDB
1. Instalamos y habilitamos MariaDB:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install mariadb-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

2. Creamos la base de datos:
```bash
sudo mysql -u root
```
```mysql
CREATE DATABASE LanzAuditDB;
CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY 'admingarcialanza';
GRANT ALL PRIVILEGES ON LanzAuditDB.* TO 'LanzAdmin'@'localhost';
FLUSH PRIVILEGES;
EXIT
```

3. Configuramos las variables de entorno (según lo que necesites):
```bash
export DB_ENGINE="mysql+pymysql"
export DB_USERNAME="LanzAdmin"
export DB_PASS="admingarcialanza"
export DB_HOST="localhost"
export DB_PORT="3306"
export DB_NAME="LanzAuditDB"
```

4. Actualizamos el archivo `config.py` con los nuevos datos de nuestra base de datos con MariaDB:
```python
import os
import random
import string

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # Set up the App SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ACTUALIZACIÓN: Variables de entorno MariaDB
    DB_ENGINE = os.getenv('DB_ENGINE', 'mysql+pymysql')
    DB_USERNAME = os.getenv('DB_USERNAME', 'LanzAdmin')
    DB_PASS = os.getenv('DB_PASS', 'admingarcialanza')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'LanzAuditDB')

    USE_SQLITE = False  # Cambiar a False ya que estamos usando MariaDB

    # Configuración de la base de datos con MariaDB
    if DB_ENGINE and DB_NAME and DB_USERNAME:
        try:
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE, DB_USERNAME, DB_PASS, DB_HOST, DB_PORT, DB_NAME
            )
        except Exception as e:
            print('> Error: DBMS Exception: ' + str(e))
            print('> Fallback to SQLite ')
            USE_SQLITE = True

    # SQLite como reserva (si MariaDB falla)
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
```

5. Instalamos las dependencias necesarias (con nuestro entorno virtual activado):
```bash
pip3 install pymysql flask-sqlalchemy
```
He añadido estas dependencias al archivo `requirements.txt` con `pip freeze > requirements.txt`

6. Creamos y aplicamos las migraciones con Flask-Migrate:
```bash
# Inicializamos las migraciones
flask db init

# Creamos las migraciones
flask db migrate

# Y aplicamos las migraciones a la base de datos MariaDB
flask db upgrade
```

7. Ejecutamos la aplicación:
```bash
flask run
```

8. Y comprobamos que se ha hecho correctamente la migración desde los logs de la consola al arrancar la aplicación o entrando en la base de datos y comprobando que están las tablas de LanzAudit.

#### Quitar el login y el register
Como no necesito que los usuarios se autentiquen (porque solo quiero un panel simple), voy a quitar la autenticación. Para ello:
1. Modificamos el archivo `apps/authentication/routes.py`:
```python
# 1. Modificamos la ruta por defecto para que sea:
@blueprint.route('/')
def route_default():
    return redirect(url_for('home_blueprint.index'))

# 2. Eliminamos los bloques de login, register, logout y el bloque de unauthorized_handler (no solo los decoradores, sino todo lo que haya debajo de cada uno también)
@blueprint.route('/login', methods=['GET', 'POST'])
@blueprint.route('/register', methods=['GET', 'POST'])
@blueprint.route('/logout')
@login_manager.unauthorized_handler
```

2. Verificamos si tenemos el decorador `@login_required` en los archivos de la plantilla. Si lo tenemos en algún lado, lo eliminamos (SOLO EL DECORADOR, NO EL BLOQUE QUE CONTIENE)

3. Eliminamos las plantillas de `apps/templates/accounts` (las dos plantillas que hay son las de `login`y la de `register`)

4. Eliminamos el archivo `apps/templates/includes/navigation.html` y la línea `{% include 'includes/navigation.html' %}` del archivo `apps/templates/layouts/base.html`.

#### Otras modificaciones
##### Poner mi logo y mi nombre en la barra
En `/apps/templates/includes/sidebar.html`, cambiar el logo por el mío y el nombre por `LanzAudit`. Ajusto la medida del logo a mi gusto y listo.


---
## LanzAudit
### Modo Local
1. Clonamos el repositorio de la aplicación
2. Creamos un entorno virtual
```bash
python3 -m venv .venv
```
3. Activamos el entorno virtual
```bash
source .venv/bin/activate
```
4. Instalamos las dependencias de la aplicación a partir del archivo `requirements.txt`
```bash
pip3 install -r requirements.txt
```
5. Creamos la base de datos `LanzAuditDB` y el usuario `LanzAdmin`. Si lo hacemos en MariaDB o MySQL es:
```mysql
CREATE DATABASE LanzAuditDB;
```
```mysql
CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY 'admingarcialanza';
GRANT ALL PRIVILEGES ON LanzAuditDB.* TO 'LanzAdmin'@'localhost';
FLUSH PRIVILEGES;
```
6. Creamos un archivo `.env` para rellenarlo con nuestra información. Por ejemplo:
```
SECRET_KEY=69K@i2WlPyy&
DATABASE_URI=mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=lanzaudit@gmail.com
MAIL_PASSWORD=xhgtcclowergfbel
MAIL_DEFAULT_SENDER="LanzAudit lanzaudit@gmail.com"
```
7. Inicializamos la base de datos y creamos sus tablas con Flask-Migrate:
```bash
flask db init
```
```bash
flask db migrate -m "Inicializando la base de datos"
```
```bash
flask db upgrade
```
8. La levantamos por el puerto 5000 con:
```bash
flask run
```
### Modo VPS


---
## Plantilla Dashboard LanzAudit (AdminLTE)
He encontrado esta plantilla de Panel de Administración Open Source: [AdminLTE](https://adminlte.io/)

---
## Plantillas HTML usadas (`templates/`)
### `base.html`
He tomado como base el `index.html` de AdminLTE para coger la sidebar y la cabecera y heredarla en todas las plantillas con Jinja2. Esto me ha simplificado muchísimo el trabajo, ya que si quisiera cambiar 1 elemento de la sidebar por ejemplo, tendría que cambiarlo manualmente en todas las plantillas que tuvieran sidebar, pero con la herencia se cambiará en todas automáticamente.
Además me ayuda a tenerlo todo más ordenado y organizado y a que tengan el mismo estilo sin variaciones.

### `index.html`
Es el Dashboard, el panel de administración principal. Es el inicio, el home.
1. En `<head>`:
    - Título.
    - Metadatos.
    - Rutas de los estilos a mi carpeta `static/css`.
2. En `<body>` :
    - Barra de navegación con una herramienta para poner el panel en pantalla completa y con tu perfil de usuario para cerrar sesión o modificar los datos.
    - Sidebar con los enlaces al Inicio, la herramienta para Realizar los escaneos, la página para ver las Estadísticas y los resultados de las auditorías, una página que solo será mostrada al administrador para la gestión de usuarios y las páginas de preguntas frecuentes y la licencia
    - En el panel principal se verán algunas estadísticas principales como los 2 o 3 últimos escaneos, un gráfico con el número de escaneos por tipo y algunas estadísticas más.

### `profile.html`
Es un pequeño formulario para que los usuarios puedan cambiar o actualizar su nombre de usuario, su correo electrónico o su foto de perfil (además de poder eliminarla y volver a usar la predeterminada).

### `login.html`
Es la pantalla para iniciar sesión. Es lo primero que sale cuando entras a la aplicación. Si no existe LanzAdmin, te redirigirá a `setup-admin.html` para realizar la configuración inicial de este. También tendrá un enlace a la página de recuperación de contraseña por si el usuario la ha perdido, se la han robado o ha ocurrido cualquier cosa.
1. En `<head>`:
    - Rutas de los estilos a mi carpeta `static/css`.

2. En `<body>`:
    - Cambiamos el nombre de la aplicación que redirige a otra página por texto en negrita que no redirija a ningún lado y ponemos al lado mi logo.
    - Cambiamos el texto que viene en inglés para poner "Inicia sesión para acceder al panel".
    - Quitamos la opción de iniciar sesión con Google o con Facebook.
    - Quitamos la opción de "Remember me".
    - Quitamos la opción de registrarse, ya que mi aplicación está pensada para empresas, por lo que solo el usuario administrador será el que podrá crear desde dentro de la aplicación al resto de usuarios.
    - Cambio el grid para que el botón de iniciar sesión ocupe todas las columnas de su fila.
    - Dejamos abajo un solo enlace de "He olvidado mi contraseña" que te redirige a un formulario para realizar una solicitud de restablecimiento de contraseña al administrador.
    - He añadido al final un script de validación que viene en uno de los formularios de ejemplos de AdminLTE, en `dist/pages/forms/general.html`. 

### `setup-admin.html`
Es casi igual que el login, pero esta es para configurar el usuario LanzAdmin, el usuario Administrador principal de la plataforma. Solo se podrá acceder y configurarlo 1 vez, mientras que no exista ningún LanzAdmin en la base de datos. Una vez que se cree, se podrá cambiar su correo y su contraseña, pero no el nombre de usuario ni el rol.

### `password-recovery.html`
Es casi igual que el login, pero esta es para enviarle una solicitud al administrador para recuperar tu contraseña.
Tiene 3 campos para introducir información que le llegará al administrador para que este se ponga en contacto con el usuario para restablecer su contraseña:
- Correo electrónico del usuario
- Motivo de la solicitud
- Algún mensaje adicional --> Tiene un valor por defecto que es `""`, es decir, se enviará un texto vacío.
También tiene el script de validación.

### `license.html`
Una tarjeta informando sobre la licencia que uso en mi aplicación con un enlace a la licencia.

### `faq.html`
Otra tarjeta del mismo estilo que la de la licencia con las preguntas más frecuentes sobre el uso de mi aplicación.

### `admin/manage-users.html`
Una tabla con una lista con los usuarios que hay guardados en la base de datos y su información. Además, algunos botones para modificarlos, eliminarlos o crear nuevos. A esta página solo tendrán acceso los usuarios con el rol 'Admin'.
### `admin/add-user.html`
Formulario para añadir nuevos usuarios a la plataforma.
### `admin/edit-user.html`
Formulario para editar al usuario en el que pinchemos (en el icono del lápiz).
### `admin/resolve-reset-request.html`
Formulario para ponerle una contraseña nueva al usuario que solicite la recuperación de la misma y así confirmar que se ha completado la solicitud (cuando pinchemos al icono de la llave que sale en naranja cuando un usuario solicita una recuperacion).


---
## Base de datos
Antes de crear la base de datos, he hecho un análisis para ver qué necesito, qué voy a hacer y cómo lo voy a hacer.
### Análisis inicial
Voy a empezar por una base de datos simple con 3 tablas y ya iré ampliando conforme vaya necesitando cosas.
#### Tabla `users`
Esta tabla almacena la información de los usuarios del sistema.

Atributos:
- `id`: Identificador único de cada usuario (clave primaria).
- `username`: Nombre de usuario único.
- `email`: Correo electrónico del usuario.
- `password_hash`: Contraseña cifrada del usuario.
- `profile_picture`: Foto de perfil del usuario.
- `role`: Rol del usuario (Admin, Worker, Analyst). El Administrador podrá hacerlo todo además de gestionar los usuarios de la aplicación y recibir las solicitudes de recuperación de las contraseñas. Los Trabajadores serán los que realicen los escaneos y los Analistas solo verán las estadísticas y analizarán los resultados.
- `created_at`: Fecha y hora en que se creó el usuario.
#### Tabla `scans`
Esta tabla almacena los escaneos realizados por los usuarios.

Atributos:
- `id`: Identificador único del escaneo (clave primaria).
- `user_id`: ID del usuario que realizó el escaneo (clave foránea a users.id).
- `scan_type`: Tipo de escaneo (Puertos, WordPress en principio).
- `scan_parameters`: Parámetros del escaneo.
- `status`: Estado del escaneo.
- `created_at`: Fecha y hora en que se realizó el escaneo.
#### Tabla `scan_results`
Esta tabla almacena los resultados de cada escaneo.

Atributos:
- `id`: Identificador único del resultado (clave primaria).
- `scan_id`: ID del escaneo al que pertenece el resultado (clave foránea a scans.id).
- `result`: Descripción o detalle del resultado (por ejemplo, "vulnerabilidad encontrada", "puerto abierto").
- `created_at`: Fecha y hora en que se generó el resultado.

### Modelo Entidad - Relación
Ahora una vez que sé lo que necesito, voy a hacer el modelo ER para ver qué relación tienen mis tablas:

![Diagrama ER](db/diseñoLogicoDB/DiagramaERLanzAuditDB.png)

### Diccionario de Datos y Modelo Lógico o Relacional
Una vez hecho esto, también he hecho el Diccionario de Datos y el Modelo Lógico.

### Probar la conexión de la base de datos con Flask (`en app.py`)
1. Instalamos las dependencias necesarias
```bash
pip3 install Flask-SQLAlchemy
pip3 install pymysql
```

2. En `app.py`, configuramos la conexión a la base de datos:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB'

db = SQLAlchemy(app)
```
Importamos text también porque en SQLAlchemy 2.0, las consultas SQL deben envolverse con `text()`.

3. Probamos la conexión creando una nueva ruta en `app.py` para probar si estamos conectados correctamente o no:
```python
@app.route('/test_db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))  # Consulta corregida
        return "Conexión exitosa a la base de datos!"
    except Exception as e:
        return f"Error de conexión: {str(e)}"
```

4. Vamos a `http://localhost:5000/test_db` y comprobamos que se ha hecho una conexión exitosa a la base de datos.

### Conexión y configuración de la base de datos con la nueva estructura de proyecto (`models.py`)
Usaremos el archivo `models.py` para definir todo lo relacionado con la base de datos:
```python
# models.py

# Importación de las librerías necesarias
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inicialización de SQLAlchemy
db = SQLAlchemy() # Objeto que interactúa con la BD

# Modelo de la tabla 'user' (Usuarios)
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), nullable=False, unique=True)
	email = db.Column(db.String(255), nullable=False, unique=True)
	password_hash = db.Column(db.String(255), nullable=False)
	profile_picture = db.Column(db.String(255), nullable=True)
	role = db.Column(db.Enum('Admin', 'Worker', 'Analyst', name='user_roles'), nullable=False)
	password_reset_requested = db.Column(db.Boolean, default=False)
	password_reset_requested_at = db.Column(db.DateTime, default=None)
	created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

def __repr__(self):
	return f'<Usuario {self.username}>' # Usuario LanzAdmin


# Modelo de la tabla 'scan' (Escaneos)
class Scan(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	scan_type = db.Column(db.Enum('Puertos', 'WordPress', name='scan_type_enum'), nullable=False)
	scan_parameters = db.Column(db.JSON, nullable=True)
	status = db.Column(db.Enum('Pendiente', 'En Progreso', 'Completado', 'Fallido', name='status_enum'), default='Pendiente')
	created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Relación con el modelo 'User' (un usuario puede tener muchos escaneos)
user = db.relationship('User', backref=db.backref('scans', lazy=True))
 
def __repr__(self):
	return f'<Escaneo {self.id} - {self.scan_type}>' # Escaneo 1 - Puertos


# Modelo de la tabla 'scan_results' (Resultado de los escanaeos)
class ScanResult(db.Model):
	__tablename__ = 'scan_results'
	id = db.Column(db.Integer, primary_key=True)
	scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
	result = db.Column(db.JSON, default=None)
	created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Relación con el modelo 'Scan' (un escaneo puede tener muchos resultados)
scan = db.relationship('Scan', backref=db.backref('scan_results', lazy=True))

def __repr__(self):
	return f'<Resultado {self.id} - Escaneo {self.scan_id}>' # Resultado 1 - Escaneo 1
```

Y ahora usamos Flask-Migrate para hacer la migración de la base de datos y poder hacer cambios en ella a traves de SQLAlchemy y pymysql:
1. Inicializamos la base de datos
```bash
flask db init
```
2. Generamos la migración y le damos un nombre
```bash
flask db migrate -m "Inicializando la base de datos"
```
3. Aplicamos la migración después de asegurarnos de que todo está bien para actualizar nuestra base de datos
```bash
flask db upgrade
```

Cada vez que hagamos un cambio, haremos:
1. Generamos la migración y le damos un nombre:
```bash
flask db migrate -m "Añadiendo la tabla Scan"
```
2. Y aplicamos la migración:
```bash
flask db upgrade
```

---
## Reorganización de la estructura del proyecto
Conforme he ido desarrollando, me he dado cuenta de que `app.py` se va a sobrecargar demasiado, por lo que después de investigar y ver varios ejemplos de proyectos con Flask, he llegado a la conclusión de que voy a dividir mi proyecto en:
- `app.py` --> La aplicación Flask
- `config.py` --> Para definir la configuración de la base de datos y cualquier otro ajuste
- `models.py` --> Para la inicialización de la base de datos y la definición de modelos dentro de la misma
- `routes.py` --> Para las rutas

También crearé un archivo `.env` que no se subirá a GitHub (lo añadiré a mi `.gitignore`) para escribir ahí datos sensibles como la clave secreta de Flask, la URI a mi base de datos... Luego las importaré en sus archivos correspondientes (`config.py`) para usarlas con `python-dotenv`.

### `.env`
Para configurar mi proyecto con variables de entorno en un archivo `.env`:
1. **Instalamos python-dotenv**
```bash
pip3 install python-dotenv
```
2. **Creamos el archivo .env en la raíz del proyecto y le añadimos los datos sensibles** (voy a poner el ejemplo de 2, pero al final serán muchos más)
```bash
nano .env
```
La clave secreta la he generado con mi proyecto [PassGen](https://github.com/Xerezanoo/PassGen).
```
SECRET_KEY=69K@i2WlPyy&
DATABASE_URI=mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB
```
3. **Añadimos `.env` al archivo `.gitignore`**
4. **Modificamos `config.py` para usar las variables del `.env`**
```python
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')  # Lee el SECRET_KEY del archivo .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Lee la URL de la base de datos
```
5. **Modificamos `app.py` para usar la configuración**
```python
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
```
6. **Reiniciamos la aplicación**

---
## Migración del proyecto a otro equipo para desarrollo
1. Clonamos el proyecto en el nuevo equipo
```bash
git clone https://github.com/Xerezanoo/LanzAudit.git
```
2. Creamos un entorno virtual
```bash
python3 -m venv .venv
```
3. Activamos el entorno virtual
```bash
source .venv/bin/activate
```
4. Instalamos las dependencias
```bash
pip3 install -r requirements.txt
```
5. Creamos nuestra base de datos, que podemos hacerlo de 2 formas:
- Manual --> Instalando un servidor de base de datos en nuestro equipo y creando y configurando la base de datos y el usuario Administrador de la base de datos
- Docker --> Usamos el siguiente comando para crear un contenedor Docker con la base de datos:
```bash
docker run -d \
--name LanzAuditDB \
-e MARIADB_ROOT_PASSWORD=root \
-e MARIADB_DATABASE=LanzAuditDB \
-e MARIADB_USER=LanzAdmin \
-e MARIADB_PASSWORD=admingarcialanza \
-p 3306:3306 mariadb:latest
```
6. Creamos y configuramos nuestro archivo `.env`
```bash
nano .env
```
La clave secreta es la que he generado con mi programa [PassGen](https://github.com/Xerezanoo/PassGen). Voy a usar la misma en todos los equipos donde vaya a desarrollar.
```
SECRET_KEY=69K@i2WlPyy&
DATABASE_URI=mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB
```
7. Y listo, ya se puede usar la app ejecutándola con `flask run`.

---
## Gestión de usuarios
Como LanzAudit está pensado para empresas, no sería lógico que cualquiera se pudiera registrar en la aplicación, cambiarse su contraseña...
Para ello, he creado una página de gestión de usuarios a la cual solo tiene acceso el Administrador de la plataforma, que será quien cree o elimine los usuarios, les asigne o cambie su rol, les cambie la contraseña...

La plantilla HTML usada contiene una tabla donde aparecen todos los usuarios registrados en la plataforma, con su id, nombre de usuario, email, rol, si ha solicitado o no una recuperación de contraseña y un botón para editarlo o eliminarlo.

Al usuario LanzAdmin no se le podrá eliminar y tampoco cambiar el nombre de usuario ni el rol, pero a los demás sí se les puede cambiar todo o eliminarlos.

También incluye un botón para añadir un nuevo usuario a la plataforma.

Todos los formularios (de edición y de creación) tienen validación para que se introduzcan todos los campos correctamente y no hayan problemas al enviar la solicitud. También está todo controlado y verificado para que no se introduzcan datos repetidos como correos que ya están registrados o nombres de usuario que ya estén en uso.

También he modificado el archivo `base.html` para que en la sidebar solo aparezca esta página a los usuarios con el rol 'Admin'.

---
## Flask-Login
Vamos a usar Flask-Login para los manejos de sesión en mi aplicación.

1. **Instalación de Flask-Login**
```bash
pip3 install flask-login
```

2. **Configurar Flask-Login en tu aplicación**
En el archivo app.py, debes inicializar Flask-Login, configurar el cargador de usuarios (user_loader) y asignar la vista a la que se redirige cuando un usuario no está autenticado.

Añade a app.py lo siguiente. La configuración de Flask-Login lo haremos debajo de la inicialización de la base de datos y/o de otras extensiones:
```python
from flask_login import LoginManager

# Inicialización de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Aquí defines la vista de login, que es a la que se redirigirá si no hay sesión activa

# Cargar el usuario
@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))
```
--> En este caso, `login_manager.user_loader` es una función que Flask-Login usará para cargar un usuario basándose en el `user_id`. Este `user_id` se almacena en la sesión, por lo que Flask-Login puede recuperar al usuario autenticado en cada solicitud (con `current_user`).

Cuando hacemos login (`login_user(user)`), Flask-Login guarda el user.id en la sesión del navegador (en una cookie segura).
En cada petición con `current_user`, Flask-Login lee el `user_id` de la sesión, llama a la función con el decorador `@login_manager.user_loader`:
```python
@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))
```
Con esta función, obtiene el objeto `User` completo desde la base de datos, que es el usuario actual que esté logueado y lo asigna a `current_user`.
Así podemos acceder a los elementos del usuario con `current_user.username` para el nombre de usuario, `current_user.role` para el rol... etc.

3. **Agregar la gestión de sesiones con Flask-Login**
Para manejar el inicio de sesión y la autenticación de un usuario, debes modificar la ruta de login en `routes.py` para hacer uso de las funcionalidades de Flask-Login.
Estos son algunos ejemplos de algunas rutas que usan Flask-Login:
```python
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User
from app import app  # Asegúrate de importar la app desde app.py

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

# Ruta para la vista de dashboard (solo accesible si el usuario está autenticado)
@app.route('/dashboard')
@login_required
def home():
    return render_template('index.html')

# Ruta para el logout (cerrar sesión)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Se ha cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))
```

4. **Plantilla login.html**
En la plantilla de login (`login.html`), ya estamos pidiendo un correo y una contraseña. Solo tenemos que asegurarnos de que el formulario esté configurado para enviar la información correctamente a la ruta de login (`action="{{ url_for('login') }}"`).

5. **Control de acceso con @login_required**
En las vistas donde deseas restringir el acceso a usuarios autenticados, usa el decorador `@login_required`. Como se ve en la ruta `/dashboard`, el acceso está restringido a usuarios que hayan iniciado sesión:
```python
@login_required
def dashboard():
    return render_template('dashboard.html')
```

6. **Manejo de la sesión**
Cuando el usuario inicia sesión correctamente, Flask-Login se encarga de gestionar la sesión del usuario. Podemos acceder al usuario actual a través de `current_user` en cualquier parte de tu aplicación:
```python
from flask_login import current_user

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
```

Resumen de los cambios importantes:
`user_loader`: Se configura para cargar el usuario desde la base de datos usando el user_id almacenado en la sesión.

`login_user`: Autentica al usuario.

`@login_required`: Se usa para proteger las vistas que solo deben ser accesibles para usuarios autenticados.

`logout_user`: Cierra la sesión del usuario.

---
## Mensajes Flash
Usaremos este bloque justo antes de la etiqueta `<form>` de los formularios para poder mostrar en el frontend los mensajes de error que envía el backend:
```html
<!--begin::Mensajes Flash-->
{% with messages = get_flashed_messages(with_categories=true) %}
{% if messages %}
<div class="alert-container">
    {% for category, message in messages %}
    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    {% endfor %}
</div>
{% endif %}
{% endwith %}
<!--end::Mensajes Flash-->
```

---
## Flask-Mail
Vamos a configurar Flask-Mail para poder enviar un correo a los usuarios administradores cuando un usuario de la plataforma solicite una recuperación de su contraseña.
Para ello, si lo hacemos con Google:
1. Nos creamos una cuenta de correo desde la que vamos a mandar los correos. La he llamado `lanzaudit@gmail.com`
2. Ahora vamos a activar la verificación en 2 pasos
3. Una vez activada, vamos a "Contraseñas de aplicación", en Seguridad de nuestra cuenta Google
4. Creamos una nueva contraseña de aplicación y la copiamos
5. Ahora, tenemos que modificar los archivos de nuestra aplicación para implementar Flask-Mail e importar el archivo de configuración:
`app.py`
```python
from flask_mail import Mail
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)
```

`config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')    # Recupera la clave del .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') # Recupera la URI del .env
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Mejora el rendimiento al dejar de seguir las modificaciones de los objetos de la BD
    MAIL_SERVER = os.getenv('MAIL_SERVER')  # Servidor de correo
    MAIL_PORT = os.getenv('MAIL_PORT')  # Puerto para TLS
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')    # Activar TLS
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Correo (para autenticarme)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Contraseña de la cuenta
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')  # El correo desde el que se enviarán los mensajes (puede ser el mismo que MAIL_USERNAME o distinto)
```

`.env`
```
SECRET_KEY=[tuContraseña]
DATABASE_URI=mysql+pymysql://LanzAdmin:[tuContraseña]/LanzAuditDB
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=[tuCorreo]@gmail.com
MAIL_PASSWORD=[tuContraseñaDeAplicacion]
MAIL_DEFAULT_SENDER=[tuCorreo]@gmail.com
```

Y listo, ya estará configurado para usarse.
Para cambiar el nombre del remitente y ponerle mayúsculas por ejemplo, lo hacemos así:
`MAIL_DEFAULT_SENDER="LanzAudit [tuCorreo]@gmail.com"`

---
## Recuperación de contraseñas
Los usuarios que pierdan su contraseña, entrarán en "Recuperar mi contraseña" en la pantalla de login.
Rellenarán el formulario con su correo, el motivo del por qué necesitan recuperar la contraseña y algún mensaje adicional.

La solicitud le llegará por correo a todos los usuarios cuyo rol sea "Admin", quienes entrarán en la pestaña de "Gestión de usuarios" y verán en naranja que se ha solicitado una recuperación de contraseña, le darán al botón naranja con el icono de la llave que aparecerá en la derecha y restablecerán la contraseña del usuario, comunicándoselo al mismo para que pueda acceder a la plataforma de nuevo.

Como medida de seguridad, se usará [PassGen](https://github.com/Xerezanoo/PassGen) para crear contraseñas seguras.

---
## Perfil
Los usuarios podrán pinchar arriba a la derecha en su perfil y entrar a un formulario donde podrán cambiarse el nombre de usuario, el correo y la foto de perfil.
La ruta en `routes.py` se ha quedado así:
```python
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
```

### Explicación foto de perfil
En el HTML, hemos creado un input para subir imágenes que está configurado así:
```html
<div class="form-group mt-3">
	<label for="imageInput" class="mb-2 d-block">Foto de perfil</label>
	<input type="file" class="form-control-file" id="imageInput" accept="image/*">
	<div class="mt-3 text-center">
		<img id="imagePreview" style="max-width: 100%; display: none;" />
	</div>
	<canvas id="croppedCanvas" style="display: none;"></canvas>
	<input type="hidden" name="cropped_image" id="croppedImageData">
</div>
```

Vamos a usar Cropper.js para recortar imágenes directamente desde el navegador. Así podemos:
1. Permitir que el usuario suba su imagen
2. Mostrar una previsualización de la misma
3. Permitir al usuario mover y redimensionar el área de recorte, quedando siempre con las medidas que yo quiera (lo he configurado a 128x128, como las imágenes de ejemplo del panel Adminlte)
4. Obtener la imagen recortada como el usuario ha querido y codificarla en base64 para tratarla como una cadena de texto

Incluiremos este script al final del archivo HTML:
```html
<script>
	let cropper;
	const imageInput = document.getElementById('imageInput');
	const imagePreview = document.getElementById('imagePreview');
	const croppedImageData = document.getElementById('croppedImageData');

	imageInput.addEventListener('change', (e) => {
		const file = e.target.files[0];
		if (!file) return;
		
		const reader = new FileReader();
		reader.onload = function (event) {
			imagePreview.src = event.target.result;
			imagePreview.style.display = 'block';

			if (cropper) cropper.destroy();

			cropper = new Cropper(imagePreview, {
				aspectRatio: 1,
				viewMode: 1,
				dragMode: 'move',
				autoCropArea: 1,
				minCropBoxWidth: 128,
				minCropBoxHeight: 128,
				ready() {
					document.querySelector('form').addEventListener('submit', function () {
						if (cropper) {
							const canvas = cropper.getCroppedCanvas({ width: 128, height: 128 });
							croppedImageData.value = canvas.toDataURL('image/png');
						}
					});
				}
			});
		};
		reader.readAsDataURL(file);
	});
</script>
```

En el backend, en la parte del perfil en `routes.py`, esta es la parte que trabaja con la imagen:
```python
from PIL import Image
from io import BytesIO
import base64
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	user = current_user
	
	if request.method == 'POST':
		cropped_data = request.form.get('cropped_image')
	
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
```
1. Si la solicitud es `POST`, recoge el `cropped_image`, que como vimos antes en el formulario HTML, es la imagen recortada que sube el usuario
2. Si existe `cropped_data`:
	1. Divide la cadena en base64 que ha recibido en 2 partes:
		1. `header` --> Contiene el tipo MIME (el identificador del tipo de medio, que será `"data:image/png;base64"`)
		2. `encoded` --> Es la imagen codificada en base64
	2. Decodifica la imagen (`encoded`) en la variable `image_data`
	3. Convierte `image_data` en bytes y se guarda en la variable `image`, por lo que `image` ya es la imagen tal cual, sin codificación en base64. Ya podemos guardarla o abrirla o lo que queramos.
	4. Ahora crea un nombre genérico de fotos de perfil para todos los usuarios que estará compuesto por `user_` + `user.id` + `.png`. Así todas las fotos tendrán el mismo formato y serán reconocibles para gestionarlas y si un usuario cambia de foto de perfil, no se duplicará, sino que se sobrescribirá. La foto de perfil del usuario con el id=4 por ejemplo, tendrá el nombre de `user_4.png`.
	5. En la variable `image_path` se guarda la ruta de la imagen, que estará compuesta por la ruta que hayamos configurado en nuestro `config.py` (yo he puesto `static/profile_pics)`) y el nombre del archivo (`user_1.png`, `user_2.png`...)
	6. Ahora, guardamos la imagen en la ruta indicada con `image.save(image_path)`
	7. Le asignamos al `current_user` (que estamos llamando como `user` porque al principio de la función definimos que `user = current_user`) la foto de perfil que ha subido para que se refleje en la base de datos.
	8. Si hubiera algún error, saldría en pantalla y redirigiría al usuario al formulario del perfil de nuevo
3. Una vez terminado, se aplicarían los cambios en la base de datos con `db.session.commit()` y saldría un mensaje de que todo ha salido correctamente.
4. Por último, si el usuario tiene foto de perfil:
	1. Decimos que `image_url` es `static/profile_pics/user.profile_picture`. Por ejemplo, para el usuario 8, `image_url` es `static/profile_pics/user_18.png`.
5. Y si no tiene:
	1. Decimos que `image_url` sea la predeterminada (`static/profile_pics/default.png`)
6. Y renderizamos la plantilla HTML del perfil, pasándole la variable `image_url`, que la podrá usar dentro de la plantilla.

---
## Errores
He creado varias páginas HTML con el mismo formato y estilos que las de AdminLTE (el estilo que llevo siguiendo todo el Proyecto) para el manejo de errores. Las he metido en la carpeta `templates/error/` y he hecho páginas para los errores más comunes de las páginas web.
Luego, en `routes.py` he configurado las funciones con sus decoradores para cada error:
```python
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
```

---
## Scanners
### nmapScanner.py
Vamos a instalar nmap con:
```bash
sudo apt install nmap -y
```

Y le damos permisos para que pueda ejecutar escaneos con permisos de root:
```bash
sudo setcap cap_net_raw,cap_net_admin=eip $(which nmap)
```

Ahora hacemos `sudo visudo` y añadimos la siguiente línea:
```bash
tu_usuario	ALL=(ALL) NOPASSWD: /usr/bin/nmap
```

Script para pasar de `scan_type` en `scan_parameters` a `subtype`:
```python
from app import db
from models import Scan  # Cambia esto si tu modelo está en otro archivo
import json

# Buscar todos los escaneos
scans = Scan.query.all()

for scan in scans:
    params = scan.scan_parameters
    if isinstance(params, str):  # Por si estuviera en formato texto
        params = json.loads(params)

    # Actualizar 'scan_type' a 'subtype' si existe
    if "scan_type" in params:
        params["subtype"] = params.pop("scan_type")

    # Asignar los cambios nuevamente a 'scan_parameters'
    scan.scan_parameters = json.dumps(params)  # Convertir a string nuevamente si es necesario

# Guardar todos los cambios en la base de datos
db.session.commit()
print("Todos los registros actualizados.")

```

### wpscanScanner.py
Instalamos wpscan:
```bash
sudo apt install ruby-full build-essential libcurl4-openssl-dev libssl-dev zlib1g-dev
```
```bash
sudo gem install wpscan
```


Nos damos de alta en la página para generar nuestra API Key. Tenemos 25 peticiones gratuitas al día.


Para parsear el resultado de forma más bonita y fácil de leer, usamos la siguiente web: https://jsonformatter.org/json-parser
