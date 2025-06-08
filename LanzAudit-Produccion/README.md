# LanzAudit-Desarrollo
## 🚀 Despliegue en entorno de producción

### 1. Clona el repositorio

```bash
git clone https://github.com/Xerezanoo/LanzAudit-Desarrollo.git
```

### 2. Para no tener problemas de permisos, llevamos la aplicación a `/var/www` y le damos permisos 
```bash
mv LanzAudit-Desarrollo/LanzAudit-Produccion /var/www/
chown -R [tu_usuario]:www-data /var/www/LanzAudit-Produccion
chmod -R 750 /var/www/LanzAudit-Produccion/
```

### 3. Entra en el directorio, crea y activa el entorno virtual

```bash
cd /var/www/LanzAudit-Produccion
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instala las dependencias

```bash
pip3 install -r requirements.txt
```

### 5. Configura el entorno
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

### 6. Crea la base de datos
Asegúrate de tener MariaDB en tu equipo. Ahora accede al servidor y ejecuta los siguientes comandos para crear la base de datos:
```mysql
CREATE DATABASE LanzAuditProduccionDB

CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY '[tu_mariadb_password]';

GRANT ALL PRIVILEGES ON LanzAuditProduccionDB.* TO 'LanzAdmin'@'localhost';

FLUSH PRIVILEGES;
```

### 7. Inicializa la base de datos
```bash
flask db init

flask db migrate -m "Inicializando la base de datos"

flask db upgrade
```

### 8. Configura LanzAudit como un servicio
```bash
sudo nano /etc/systemd/system/lanzauditproduccion.service
```
```bash
[Unit]
Description=Instancia Gunicorn para servir LanzAudit en Producción en local
After=network.target

[Service]
User=[tu_usuario]
Group=www-data
WorkingDirectory=/var/www/LanzAudit-Produccion
Environment="PATH=/var/www/LanzAudit-Produccion/.venv/bin"
ExecStart=/var/www/LanzAudit-Produccion/.venv/bin/gunicorn --workers 4 --timeout 600 --bind unix:/var/www/LanzAudit-Produccion/lanzauditproduccion.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

Reiniciamos:

```bash
sudo systemctl daemon-reload
```

Y ya podremos manejarlo como un servicio cualquiera:

```bash
sudo systemctl start lanzauditproduccion
sudo systemctl enable lanzauditproduccion
sudo systemctl status lanzauditproduccion
```

### 9. Configuramos Nginx como proxy inverso
```bash
nano /etc/nginx/sites-available/lanzauditproduccion
```
```bash
server {
        listen 80;
        server_name localhost 127.0.0.1;
        location / {
                include proxy_params;
                proxy_pass http://unix:/var/www/LanzAudit-Produccion/lanzauditproduccion.sock:/;
                proxy_read_timeout 600;
           proxy_connect_timeout 600;
           proxy_send_timeout 600;
           send_timeout 600;
        }
}
```

### 10. Habilitamos el sitio
```bash
sudo ln -s /etc/nginx/sites-available/lanzauditproduccion /etc/nginx/sites-enabled
```

### 11. Comprobamos si tenemos errores de sintaxis
```bash
sudo nginx -t
```
### 12. Y reiniciamos todo
```bash
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl restart lanzauditproduccion
```

Ya podremos acceder desde el navegador: http://localhost
