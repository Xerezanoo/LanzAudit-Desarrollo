## Descripción de las tablas
### Tabla `user`
Esta tabla almacena la información de los usuarios del sistema.

Atributos:
- `id`: Identificador único de cada usuario (clave primaria).
- `username`: Nombre de usuario único.
- `email`: Correo electrónico del usuario.
- `password_hash`: Contraseña cifrada del usuario.
- `profile_picture`: Foto de perfil del usuario.
- `role`: Rol del usuario (administrador, trabajador, usuario).
- `created_at`: Fecha y hora en que se creó el usuario.

### Tabla `scan`
Esta tabla almacena los escaneos realizados por los usuarios.

Atributos:
- `id`: Identificador único del escaneo (clave primaria).
- `user_id`: ID del usuario que realizó el escaneo (clave foránea a user.id).
- `scan_type`: Tipo de escaneo (por ejemplo, "puertos", "vulnerabilidades", etc.).
- `scan_parameters`: Parámetros del escaneo.
- `status`: Estado del escaneo.
- `created_at`: Fecha y hora en que se realizó el escaneo.


### Tabla `scan_results`
Esta tabla almacena los resultados de cada escaneo.

Atributos:
- `id`: Identificador único del resultado (clave primaria).
- `scan_id`: ID del escaneo al que pertenece el resultado (clave foránea a scan.id).
- `result`: Descripción o detalle del resultado (por ejemplo, "vulnerabilidad encontrada", "puerto abierto").
- `created_at`: Fecha y hora en que se generó el resultado.


## Relaciones entre las tablas:
**Relación entre user y scan**: Un usuario puede realizar múltiples escaneos, por lo tanto, hay una relación uno a muchos entre user y scan (un usuario puede tener varios escaneos, pero cada escaneo pertenece a un único usuario).

**Relación entre scan y scan_results**: Un escaneo puede generar múltiples resultados, por lo tanto, hay una relación uno a muchos entre scan y scan_results (un escaneo tiene muchos resultados, pero cada resultado pertenece a un solo escaneo).

## Modelo Entidad-Relación:
Aquí tienes una descripción de cómo representar todo eso en Dia:

- **Entidad `user`:**
**Atributos:** id (PK), username, email, password_hash, role

**Relación:**
Relación uno a muchos con scan (un usuario puede realizar múltiples escaneos).
Relación uno a muchos con password_resets (un usuario puede tener múltiples solicitudes de restablecimiento de contraseña).

- **Entidad `scan`:**
**Atributos:** id (PK), user_id (FK), scan_type, created_at

**Relación:**
Relación muchos a uno con user (varios escaneos pueden pertenecer a un único usuario).
Relación uno a muchos con scan_results (un escaneo puede generar múltiples resultados).

- **Entidad `scan_results`:**
**Atributos:** id (PK), scan_id (FK), result, created_at

**Relación:**
Relación muchos a uno con scan (varios resultados pueden pertenecer a un único escaneo).
