## Pre-proyecto
LanzAudit, una aplicación web de gestión de auditorías de seguridad diseñada para realizar, registrar y gestionar auditorías automáticas de redes y sistemas.
### 1. Funcionalidades
### 1.1. Gestión de Auditorías
- Panel centralizado para ejecutar y gestionar auditorías.
- Registro de hallazgos.
### 1.2. Automatización de Escaneos
- Integración con OpenVAS / Nessus / Nmap / WPS Scan (WordPress)... u otras herramientas para realizar **escaneos automáticos**.
- Análisis de configuraciones de **red** y **sistemas**.
- Vinculación automática de los resultados al **panel de auditorías**.
### 1.3. Dashboard (Panel) Centralizado de Auditorías
- Visualización de métricas clave: hallazgos críticos, niveles de **riesgo**, y tendencias.
- **Gráficos** interactivos para comparar auditorías y evaluar el cumplimiento normativo.
- 
### 1.4. Informes Automatizados
- Generación de **informes** completos en **PDF** con detalles de hallazgos, riesgos y recomendaciones.
- Sección de análisis histórico para observar mejoras en las auditorías.

## 2. Arquitectura y Tecnologías
- El framework web **Flask** para la interfaz del panel de auditorías.
- **Chart.js o Plotly** para gráficos y estadísticas.

- **Python** para la lógica principal.
- Integración de APIs de **OpenVAS / Nessus / Nmap** y otras herramientas de escaneos para recopilar resultados de escaneo.

- **MariaDB** como SGBD para almacenar los resultados y configuraciones que obtengamos.

- **Módulo de Escaneos**: Automatización de escaneos y procesamiento de resultados.
- **Módulo de Gestión**: Registro de hallazgos y asignación de criticidad.
- **Módulo de Informes**: Generación de informes en formato PDF con recomendaciones. WeasyPrint o ReportLab.

## 3. Flujo de la aplicación
### 3.1. Creación de una Auditoría
- El usuario realiza una nueva auditoría en el panel, seleccionando la IP, puertos o sistemas a auditar.
### 3.2. Ejecución del Escaneo
- El backend lanza un escaneo automático usando OpenVAS / Nessus / Nmap y las herramientas que vaya a usar y recopila los resultados.
- Se almacenan los hallazgos y su criticidad en la base de datos.
### 3.3. Visualización de Resultados
- El panel muestra los hallazgos organizados por sistemas y criticidad.
- Incluye gráficos que muestran estadísticas de riesgo.
### 3.4. Generación de Informes
- El sistema genera un informe PDF con todos los hallazgos y recomendaciones.
- Los informes se almacenan en un historial para consulta futura.
### 3.5. Seguimiento
- El usuario puede marcar hallazgos como resueltos y hacer seguimiento a las auditorías.
