# LanzAudit
Desarrollo completo de mi aplicación LanzAudit - Proyecto Administración de Sistemas Informáticos en Red 2025

LanzAudit es una aplicación web para realizar, gestionar y visualizar escaneos de seguridad (con herramientas como Nmap, WPScan) a través de una interfaz web Flask muy intuitiva.

Está diseñada para que pueda usarse en el ámbito empresarial sin la necesidad de tener amplios conocimientos técnicos en Ciberseguridad.

Cuenta con una herramienta para la gestión de usuarios por parte del Administrador para poder asignar roles (Admin, Worker y Analyst). Según el rol, podrán tener o no ciertas funciones en la aplicación.

También cuenta con una IA para generar informes de los escaneos en PDF en un formato amigable y presentable en apenas 1 minuto.

El repositorio incluye:
- **LanzAudit - Aplicación web de auditorías de seguridad con panel de administración.md** ➡️​ Primer documento sobre lo que podía hacer con mi aplicación.
- **LanzAudit.md** ➡️​ Documentación que he ido tomando mientras que desarrollaba la aplicación.
- **db/** ➡️​ Directorio donde se encuentra lo relacionado con la base de datos. Aquí hice un boceto de lo que necesitaba en la base de datos de mi aplicación (diseño lógico) para luego crearla.
- **Ideas/** ➡️​ Directorio con ideas parecidas o que me podían servir como inspiración para mi aplicación.
- **Logo/** ➡️​ El logo de mi aplicación con diferentes fondos o colores.
- **LanzAudit-Desarrollo/** ➡️​ Aplicación en Desarrollo. Donde pruebo cualquier cambio para depurar errores sin romper la aplicación en producción.
- **LanzAudit-Produccion/** ➡️​ Aplicación en Producción en local, configurada como un servicio con Gunicorn y con Nginx como proxy inverso. Para comprobar cómo se comportará en un VPS remoto.
- **LanzAudit-Docker/** ➡️​ Aplicación completamente Dockerizada. Personalmente creo que esta es la versión más valiosa de todas.
