# LanzAudit-Docker
## 🐳 Despliegue de la aplicación completamente Dockerizada en producción

### 1. Clona el repositorio

```bash
git clone https://github.com/Xerezanoo/LanzAudit-Desarrollo.git
cd LanzAudit-Desarrollo/LanzAudit-Docker
```

### 2. Configura el entorno
Edita el archivo `.env_example` que se encuentra dentro del proyecto.
Rellena los datos que falten (los que están entre corchetes (`[]`)).

- Para generar claves secretas como la `SECRET_KEY` o la `MARIADB_ROOT_PASSWORD`, puedes usar otro proyecto mío llamado `PassGen`, que genera una clave segura en 1 segundo: https://github.com/Xerezanoo/PassGen.git

Pon también la contraseña del usuario de la base de datos, `MARIADB_PASSWORD`, que será la misma que deberás poner en la `DATABASE_URI`.

- En `MAIL_USERNAME` pon tu correo Gmail y en `MAIL_PASSWORD` tendrás que poner una contraseña de aplicación.
Para generar tu contraseña de aplicación:
1. Activa la verificación en dos pasos de tu cuenta de Google: https://support.google.com/accounts/answer/185839
2. Crea una nueva contraseña de aplicación con el nombre LanzAudit: https://myaccount.google.com/apppasswords
3. Pega la contraseña toda junta, sin espacios (serán 16 digitos o caracteres)

No te olvides de poner también tu correo en el `MAIL_DEFAULT_SENDER`.

- Ahora regístrate, genera tus API Key gratuitas y pégalas en el `.env_example`:
    - WPScan: https://wpscan.com/profile/
    - Cohere (IA): https://dashboard.cohere.com/api-keys

- Y por último, renombra el archivo para que sea tu `.env`:
```bash
mv .env_example .env
```

### 3. Construye la imagen
```bash
docker compose build
```

### 4. Levanta la aplicación
Esto lanzará:

- MariaDB (contenedor `db`)
- LanzAudit (contenedor `web` con Flask + Gunicorn)
- Nginx (contenedor `nginx` como proxy inverso)

```bash
docker compose up -d
```

### 5. Accede a la aplicación
Ya podrás abrir tu navegador y acceder a `http://localhost:8080` para entrar a la aplicación.

Si entras demasiado rápido, es posible que Flask todavía esté arrancando y te de un error `Bad Gateway`. Espera unos segundos tras levantar los contenedores para acceder.

### Detener los contenedores
Para dejar de servir la aplicación, puedes parar los contenedores desde la raíz (donde se encuentra el `docker-compose.yml`) con:
```bash
docker compose down
```

Si quieres dejar de servirla y además, eliminar los datos (se eliminará todo: la base de datos, las fotos de perfil subidas, los reportes generados...):
```bash
docker compose down -v
```
