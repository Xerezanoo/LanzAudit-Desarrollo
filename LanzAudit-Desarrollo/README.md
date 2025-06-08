# LanzAudit-Desarrollo
## 🛠️  Proyecto en entorno de desarrollo local

### 1. Clona el repositorio

```bash
git clone https://github.com/Xerezanoo/LanzAudit-Desarrollo.git
cd LanzAudit-Desarrollo/LanzAudit-Desarrollo
```

### 2. Crea y activa el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip3 install -r requirements.txt
```

### 4. Configura el entorno
Edita el archivo `.env_example` que se encuentra dentro del proyecto.
Rellena los datos que falten (los que están entre corchetes (`[]`)).

- Para generar claves secretas como la `SECRET_KEY`, puedes usar otro proyecto mío llamado `PassGen`, que genera una clave segura en 1 segundo: https://github.com/Xerezanoo/PassGen.git

- En `MAIL_SENDER`, pon tu correo activado y configurado con SendGrid.

- Ahora regístrate, genera tus API Key gratuitas y pégalas en el `.env_example`:
    - WPScan: https://wpscan.com/profile/
    - Cohere (IA): https://dashboard.cohere.com/api-keys
    - SendGrid (correos): https://sendgrid.com

- Y por último, renombra el archivo para que sea tu `.env`:
```bash
mv .env_example .env
```

### 5. Crea la base de datos
Asegúrate de tener MariaDB en tu equipo. Ahora accede al servidor y ejecuta los siguientes comandos para crear la base de datos:
```mysql
CREATE DATABASE LanzAuditDesarrolloDB

CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY '[tu_mariadb_password]';

GRANT ALL PRIVILEGES ON LanzAuditDesarrolloDB.* TO 'LanzAdmin'@'localhost';

FLUSH PRIVILEGES;
```

### 6. Inicializa la base de datos
```bash
flask db init

flask db migrate -m "Inicializando la base de datos"

flask db upgrade
```

### 7. Arranca la aplicación
```bash
flask run
```

Ya podremos acceder desde el navegador: http://localhost:5000

