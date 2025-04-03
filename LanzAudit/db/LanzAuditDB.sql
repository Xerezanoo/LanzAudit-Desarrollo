/* LanzAuditDB */

/* 1. Creamos la base de datos LanzAuditDB */
CREATE DATABASE LanzAuditDB;


/* 2. Creamos el usuario Administrador: LanzAdmin */
CREATE USER 'LanzAdmin'@'localhost' IDENTIFIED BY 'admingarcialanza';


/* 3. Le damos todos los permisos al usuario que acabamos de crear para la base de datos LanzAuditDB y actualizamos los permisos para que se apliquen los cambios */
GRANT ALL PRIVILEGES ON LanzAuditDB.* TO 'LanzAdmin'@'localhost';

FLUSH PRIVILEGES;


/* 4. Entramos en la base de datos LanzAuditDB y creamos las tablas */
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
