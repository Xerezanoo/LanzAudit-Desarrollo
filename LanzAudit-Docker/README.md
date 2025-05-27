# LanzAudit

LanzAudit es una aplicación web para realizar, gestionar y visualizar escaneos de seguridad (con herramientas como Nmap, WPScan) a través de una interfaz web Flask muy intuitiva, lista para ejecutarse en producción usando Docker, Gunicorn y Nginx.

Está diseñada para que pueda usarse en el ámbito empresarial sin la necesidad de tener amplios conocimientos técnicos en Ciberseguridad.

Cuenta con una herramienta para la gestión de usuarios por parte del Administrador para poder asignar roles (Admin, Worker y Analyst). Según el rol, podrán hacer o no ciertas cosas en la aplicación.

También cuenta con una IA para generar informes de los escaneos en PDF en un formato amigable y presentable en apenas 1 minuto.

---

## 🐳 **Cómo usar LanzAudit con Docker**

### 1. Clona el repositorio

```bash
git clone https://github.com/Xerezanoo/LanzAudit.git
cd LanzAudit
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

### 3. Construye los contenedores
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

Si entras demasiado rápido, es posible que Flask todavía esté arrancando. Espera unos segundos tras levantar los contenedores para acceder.

### Detener los contenedores
Para dejar de servir la aplicación, puedes parar los contenedores desde la raíz (donde se encuentra el `docker-compose.yml`) con:
```bash
docker compose down
```

Si quieres dejar de servirla y además, eliminar los datos (se eliminará todo: la base de datos, las fotos de perfil subidas, los reportes generados...):
```bash
docker compose down -v
```

### Tiempo de espera configurado
Se ha configurado la aplicación para aguantar hasta 10 minutos de espera, por si un escaneo se hace más largo de la cuenta.
Aun así, si realiza algún escaneo que supere los 10 min, se guardará como fallido por exceder el tiempo máximo de espera.

### Estructura principal
- `/app`: Código fuente de Flask

- `/app/static`: Archivos estáticos

- `/app/templates`: Plantillas HTML (Jinja2)

- `Dockerfile`: Imagen de LanzAudit

- `docker-compose.yml`: Orquestación completa de los 3 contenedores

- `nginx/default.conf`: Configuración del proxy inverso
