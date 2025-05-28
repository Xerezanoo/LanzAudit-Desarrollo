## Puesta en producción en un VPS remoto DigitalOcean
Como tenemos dominios gratis y 200€ para gastar en DigitalOcean con GitHub Education, voy a hacerlo aquí.
Primero nos commpramos un dominio (en Name.com por ejemplo tenemos varios gratuitos). Me he decidido por lanzaudit.systems
Ahora vamos a crear el VPS, es decir, creamos un Droplet de DigitalOcean:
1. Elegimos la región: Frankfurt es la que mejor funciona en el sur de España
2. Elegimos una imagen Ubuntu 24.04 LTS porque es la versión estable más reciente
3. Elegimos que queremos un Droplet básico con una CPU Premium Intel (32€ mensuales, 4Gb de RAM, 2 Intel CPUs, 120Gb NVMe SSDs, 4TB Transfer)
4. Elegimos el tipo de autenticación (se recomienda con SSH key). Podemos generar una clave SSH con `ssh-keygen` y copiar aquí el contenido de la pública (`~/.ssh/clave.pub`)
5. Activamos algunas cosas gratuitas como la conectividad IPv6 por si acaso o la monitorización del VPS

Ya tendremos creado el Droplet, así que se nos dará su IP pública.

Para acceder al VPS, haremos (desde el PC donde tengamos la clave SSH que hemos pegado en DigitalOcean):
```bash
ssh root@[IP_VPS]
```
Una vez dentro, vamos a cambiar la zona horaria a la española:
```bash
timedatectl set-timezone Europe/Madrid
```
Y lo verificamos con:
```bash
timedatectl
```

1. Actualizamos los paquetes de la máquina:
```bash
apt update && sudo apt upgrade -y
```

2. Instalamos lo que necesitamos y algunas dependencias o librerías de algunos paquetes:
```bash
apt install python3 python3-venv python3-pip nmap nginx mariadb-server -y
```
```bash
apt install ruby-full build-essential libcurl4-openssl-dev libssl-dev zlib1g-dev -y
gem install wpscan
```
```bash
apt install libpango-1.0-0 libpango1.0-dev libcairo2 libcairo2-dev libgdk-pixbuf-2.0-0 libgdk-pixbuf2.0-dev libffi-dev -y
```
```bash
apt install libjpeg-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk -y
```

3. Creamos y configuramos la base de datos y el usuario Administrador de la base de datos:
```bash
mysql -u root
```
```mysql
CREATE DATABASE LanzAuditDB;
CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY 'admingarcialanza';
GRANT ALL PRIVILEGES ON LanzAuditDB.* TO 'LanzAdmin'@'localhost';
FLUSH PRIVILEGES;
```

4. Desde nuestro PC, copiamos la app a nuestro servidor:
```bash
scp -r ~/ProyectoASIR/LanzAudit-Desarrollo/LanzAudit-Produccion root@[IP_VPS]:/var/www/
```

5. Desde el VPS, le cambiamos el nombre a LanzAudit:
```bash
mv /var/www/LanzAudit-Produccion /var/www/LanzAudit
```

6. Le damos los permisos correctos a la carpeta para que Nginx pueda acceder:
```bash
chown -R root:www-data /var/www/LanzAudit
chmod -R 750 /var/www/LanzAudit/
```

7. Dentro del directorio `/var/www/LanzAudit`, creamos un entorno virtual y lo activamos:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

8. Instalamos las dependencias:
```bash
pip3 install -r requirements.txt
```

9. Creamos un `.env` con lo que necesitamos:
```bash
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=[tu_secret_key]
DATABASE_URI=mysql+pymysql://LanzAdmin:admingarcialanza@localhost/LanzAuditDB
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=[tu_correo]@gmail.com
MAIL_PASSWORD=[tu_contraseña_de_aplicacion]
MAIL_DEFAULT_SENDER="LanzAudit [tu_correo]@gmail.com"
WPSCAN_API_KEY=[tu_api_key_wpscan]
COHERE_API_KEY=[tu_api_key_cohere]
```

10. Inicializamos la base de datos con Flask:
```bash
flask db init
flask db migrate -m "Inicializando la base de datos"
flask db upgrade
```

11. Configuramos el servicio:
```bash
nano /etc/systemd/system/lanzaudit.service
```
```bash
[Unit]
Description=LanzAudit App
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/LanzAudit
Environment="PATH=/var/www/LanzAudit/.venv/bin"
ExecStart=/var/www/LanzAudit/.venv/bin/gunicorn --workers 4 --timeout 600 --bind unix:/var/www/LanzAudit/lanzaudit.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

12. Reiniciamos y vemos que está funcionando perfectamente:
```bash
systemctl daemon-reload
systemctl start lanzaudit
systemctl enable lanzaudit
systemctl status lanzaudit
```

13. Configuramos Nginx como proxy inverso:
```bash
nano /etc/nginx/sites-available/lanzaudit
```
```bash
server {
        listen 80;
        server_name lanzaudit.systems www.lanzaudit.systems;
        location / {
                include proxy_params;
                proxy_pass http://unix:/var/www/LanzAudit/lanzaudit.sock:/;
                proxy_read_timeout 600;
           proxy_connect_timeout 600;
           proxy_send_timeout 600;
           send_timeout 600;
        }
}
```

14. Agregamos un registro de tipo A en la administración de DNS de nuestro dominio para que de como respuesta la IP de nuestro VPS cuando se ingrese el nombre de `lanzaudit.systems` o `www.lanzaudit.systems`.

15. Habilitamos el sitio:
```bash
ln -s /etc/nginx/sites-available/lanzaudit /etc/nginx/sites-enabled
```

16. Comprobamos si hay errores de sintaxis y si nos da OK, reiniciamos todo:
```bash
nginx -t
systemctl daemon-reload
systemctl restart lanzaudit
systemctl restart nginx
```

17. Por último, vamos a instalar un certificado SSL para poder tener HTTPS:
```bash
apt install python3-certbot-nginx -y

certbot --nginx -d lanzaudit.systems -d www.lanzaudit.systems
```

Ahora, introducimos un correo, aceptamos los Términos y Condiciones y elegimos si queremos que se nos envíe publicidad.

Y listo, ya podemos entrar a https://www.lanzaudit.systems para usar LanzAudit.
