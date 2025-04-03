## Framework Backend:
Flask --> ¿Por qué Flask en vez de Django?


### Proyecto vulnmanager GitHub
1. Para poder usar el script `genSec.sh`, tenemos que instalar el paquete `pwgen`:
```bash
sudo apt install pwgen -y
```

2. Tenemos que eliminar las siguientes líneas del archivo `docker-compose.yml`:
```bash
build: .

build: ./GUI
```

3. El archivo `Dockerfile` será:
```bash
# Stage 1: Builder
FROM ubuntu:20.04 as builder

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    maven openjdk-8-jdk pwgen git && \
    mkdir -p /local/git

RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

WORKDIR /local/git/
RUN git clone -b develop https://github.com/xebia-research/vulnmanager && \
    cd vulnmanager && \
    git pull && \
    bash ./scripts/genSec.sh && \
    bash ./dockerScripts/dbDefinition.sh && \
    mvn install -DskipTests=true && \
    mvn package -DskipTests=true

# Stage 2: Runner
FROM openjdk:8-jdk as runner
RUN mkdir -p /opt/
COPY --from=builder /local/git/vulnmanager/target/vulnmanager-1.0-SNAPSHOT.jar /opt/vulnmanager-1.0-SNAPSHOT.jar
COPY --from=builder /local/git/vulnmanager/example_logs /opt/example_logs
ENTRYPOINT ["java", "-jar", "/opt/vulnmanager-1.0-SNAPSHOT.jar"]
```

4. En el archivo `pom.xml`, haremos varias modificaciones:
5. Primero, añadiremos las siguientes dependencias debajo de las existentes en `<dependencies>`:
```java
<dependency>
     <groupId>javax.xml.bind</groupId>
     <artifactId>jaxb-api</artifactId>
     <version>2.3.1</version>
</dependency>
<dependency>
     <groupId>com.sun.xml.bind</groupId>
     <artifactId>jaxb-impl</artifactId>
     <version>2.3.1</version>
</dependency>
<dependency>
     <groupId>javax.activation</groupId>
     <artifactId>activation</artifactId>
     <version>1.1.1</version>
</dependency>
<dependency>
     <groupId>org.glassfish.jaxb</groupId>
     <artifactId>jaxb-runtime</artifactId>
     <version>2.3.1</version>
</dependency>
```
6. Luego eliminamos las dependencias duplicadas:
- `spring-boot-starter-data-jpa`
- `jjwt`
7. Y por último, ejecutamos el siguiente comando para compilar el proyecto (tenemos que tener instalado el paquete `maven` en nuestra máquina principal):
```bash
mvn clean install -DskipTests=true
```
Se ha compilado correctamente, pero aun así siguen habiendo problemas al hacerle el `sudo docker compose build`.

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
#### Archivo `gunicorn-cfg.py` **temporal
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
1. Clonamos el repositorio que contiene la aplicación
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
5. Ya podemos desarrollar o usar la aplicación
6. La levantamos por el puerto 5000 con:
```bash
flask run
```
### Modo VPS


---
## Plantilla Dashboard LanzAudit (AdminLTE)
He encontrado esta plantilla de Panel de Administración Open Source: [AdminLTE](https://adminlte.io/)

---
## Plantillas HTML usadas
### `base.html`
He tomado como base el `index.html` de AdminLTE para coger la sidebar y la cabecera y heredarla en todas las plantillas con Jinja2. Esto me ha simplificado muchísimo el trabajo, ya que si quisiera cambiar 1 elemento de la sidebar por ejemplo, tendría que cambiarlo manualmente en todas las plantillas que tuvieran sidebar, pero con la herencia se cambiará en todas automáticamente.
Además me ayuda a tenerlo todo más ordenado y organizado y a que tengan el mismo estilo sin variaciones.

### `index.html`
1. En `<head>`:
    - Título.
    - Metadatos.
    - Rutas de los estilos a mi carpeta `static/css`.
2. En `<body>` :
    - Barra de navegación con una herramienta para poner el panel en pantalla completa y con tu perfil de usuario para cerrar sesión o modificar los datos.
    - Sidebar con los enlaces al Inicio, la herramienta para Realizar los escaneos, la página para ver las Estadísticas y los resultados de las auditorías, una página que solo será mostrada al administrador para la gestión de usuarios y las páginas de preguntas frecuentes y la licencia
    - En el panel principal se verán algunas estadísticas principales como los 2 o 3 últimos escaneos, un gráfico con el número de escaneos por tipo y algunas estadísticas más.
    

### `login.html`
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

### `forgot-password.html`
Es casi igual que la de login, pero tiene explicado que la página es para enviarle una solicitud al administrador para recuperar tu contraseña.
Tiene 3 campos para introducir información que le llegará al administrador para que este se ponga en contacto con el usuario para restablecer su contraseña:
- Correo electrónico del usuario
- Motivo de la solicitud
- Algún mensaje adicional --> Tiene un valor por defecto que es `""`, es decir, se enviará un texto vacío.
También tiene el script de validación.

### `license.html`
Una tarjeta informando sobre la licencia que uso en mi aplicación con un enlace a la licencia.

### `faq.html`
Otra tarjeta del mismo estilo que la de la licencia con las preguntas más frecuentes sobre el uso de mi aplicación.



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

![Diagrama ER]("Diagrama ER LanzAuditDB.png")

### Diccionario de Datos y Modelo Lógico o Relacional
Una vez hecho esto, también he hecho el Diccionario de Datos y el Modelo Lógico.

### Conexión de la base de datos con Flask (`en app.py`)
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

### Conexión y configuración de la base de datos con la nueva estructura de proyecto
Usaremos el archivo `models.py` para definir todo lo relacionado con la base de datos:
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum('Admin', 'Worker', 'Analyst', name='user_roles'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<User {self.username}>'

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scan_type = db.Column(db.Enum('Puertos', 'WordPress', name='scan_type_enum'), nullable=False)
    scan_parameters = db.Column(db.JSON, nullable=True)
    status = db.Column(db.Enum('Pendiente', 'En Progreso', 'Completado', 'Fallido', name='status_enum'), default='Pendiente')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('scans', lazy=True))

    def __repr__(self):
        return f'<Scan {self.id} - {self.scan_type}>'

class ScanResult(db.Model):
    __tablename__ = 'scan_results'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    result = db.Column(db.JSON, default=None)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    scan = db.relationship('Scan', backref=db.backref('scan_results', lazy=True))

    def __repr__(self):
        return f'<ScanResult {self.id}>'

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
2. **Creamos el archivo .env en la raíz del proyecto y le añadimos los datos sensibles**
```bash
nano .env
```
La clave secreta la he generado con mi proyecto [PassGen](https://github.com/Xerezanoo/PassGen).
```
SECRET_KEY=69K@i2WlPyy&
DATABASE_URL=mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB
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
## Migración del proyecto a otro equipo
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
DATABASE_URL=mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB
```
7. Y listo, ya se puede usar la app ejecutándola con `flask run`.

---
## Gestión de usuarios
Como LanzAudit está pensado para empresas, no sería lógico que cualquiera se pudiera registrar en la aplicación, cambiarse su contraseña...
Para ello, he creado una página de gestión de usuarios a la cual solo tiene acceso el Administrador de la plataforma, que será quien cree o elimine los usuarios, les asigne o cambie su rol, les cambie la contraseña...

La plantilla HTML usada es muy parecida a la de login, pero con un formulario para creación y edición de usuarios.
