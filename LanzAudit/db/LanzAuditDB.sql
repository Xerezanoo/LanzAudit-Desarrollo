/* LanzAuditDB */

/* En los comandos hay que sustituir el campo `[tuContraseña]` por tu contraseña propia. */

/* 1. Creamos la base de datos LanzAuditDB */
CREATE DATABASE LanzAuditDB;


/* 2. Creamos el usuario Administrador: LanzAdmin */
CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY '[tuContraseña]';


/* 3. Le damos todos los permisos al usuario que acabamos de crear para la base de datos LanzAuditDB y actualizamos los permisos para que se apliquen los cambios */
GRANT ALL PRIVILEGES ON LanzAuditDB.* TO 'LanzAdmin'@'localhost';

FLUSH PRIVILEGES;


/* 4. Entramos en la base de datos LanzAuditDB y creamos las tablas (esto ya no es necesario, con definir los modelos en `models.py` y hacer la inicialización de la base de datos con Flask-Migrate ya se crearán las tablas (ver punto 5)) */
USE LanzAuditDB

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(255),
    role ENUM('Admin', 'Worker', 'Analyst') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scan_type ENUM('Puertos', 'WordPress') NOT NULL,
    scan_parameters JSON DEFAULT NULL,
    status ENUM('Pendiente', 'En Progreso', 'Completado', 'Fallido') DEFAULT 'Pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE scan_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_id INT NOT NULL,
    result JSON DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scan(id) ON DELETE CASCADE
);


/* 5. Lo que hemos hecho en el punto 4 realmente no es necesario. Solo tendremos que hacer los puntos 1, 2 y 3. Una vez hechos, escribiremos en nuestro `.env`, en el apartado de `DATABASE_URI` el siguiente contenido:
mysql+pymysql://LanzAdmin:[tuContraseña]@localhost/LanzAuditDB */


/* 6. Como ya tenemos el `models.py` con los modelos de las tablas y el usuario Administrador LanzAdmin creados, solo queda usar Flask-Migrate: */

flask db init --> Para inicializar la base de datos

flask db migrate -m "Inicializando la base de datos" --> Para confirmar la migración

flask db upgrade --> Para aplicar los cambios

/* 7. Y listo, se crearán las tablas en la base de datos sin tener que usar SQL como en el punto 4. */
