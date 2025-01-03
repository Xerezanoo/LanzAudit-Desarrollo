# LanzAudit
## Framework Backend:
Flask --> ¿Por qué Flask en vez de Django?

## Docker:
Panel y herramienta están en Docker, a lo mejor lo hacemos así nosotros también
### ¿Cómo instalar Docker en Linux?
1. Instalamos `docker.io`:
```bash
sudo apt install docker.io
```

2. Ya podemos usarlo, pero solo como `root`

3. Para usarlo sin ser `root`, ejecutamos los siguientes comandos:
```bash
sudo usermod -aG docker ${USER}

su - ${USER}

sudo usermod -aG docker kali # O el nombre de tu usuario
```

4. Y listo, ya podemos usar docker sin ser `root`.

### Comandos Docker
Con `docker ps`, vemos los contenedores de Docker.
Con `docker images` vemos las imágenes de Docker.
 
### Instalación de Docker Compose
#### Para nuestro usuario
1. Creamos el directorio de los plugins si no existe y descargamos el archivo docker-compose en la ruta del HOME del usuario:
```bash
$ DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}

$ mkdir -p $DOCKER_CONFIG/cli-plugins

$ curl -SL https://github.com/docker/compose/releases/download/v2.32.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
```
Si queremos otra versión, cambiamos la versión en la URL del comando `curl`

2. Aplicamos permisos de ejecución al archivo:
```bash
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

3. Comprobamos la instalación:
```bash
docker compose version
```
#### Para todos los usuarios del sistema
1. Creamos el directorio de los plugins si no existe y descargamos el archivo docker-compose en la ruta que queremos:
```bash
$ sudo mkdir -p /usr/local/lib/docker/cli-plugins
$ sudo curl -SL https://github.com/docker/compose/releases/download/v2.32.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
```

2. Aplicamos permisos de ejecución al archivo:
```bash
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

3. Comprobamos la instalación:
```bash
sudo docker compose version
```

#### Para desinstalarlo
##### Para nuestro usuario
```bash
rm $HOME/.docker/cli-plugins/docker-compose
```
##### Para todos los usuarios
```bash
sudo rm /usr/local/lib/docker/cli-plugins/docker-compose
```

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

## Plantilla Dashboard Flask
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
7. Iniciamos la app en `http://127.0.0.1:5000/` con `flask run` (siempre con el entorno virtual activado, porque si no no tendremos las dependencias necesarias para iniciarla)
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

3. Configuramos las variables de entorno:
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