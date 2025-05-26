import cohere
import os
from datetime import datetime
from weasyprint import HTML

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def generateReport(result):
    prompt = f"""
Genera un informe breve y en texto plano sobre el siguiente resultado de escaneo (puede ser Nmap o WPScan). Es importante que no utilices caracteres especiales como almohadillas, asteriscos ni viñetas. Solo texto limpio y claro.

Este informe está dirigido a un usuario sin conocimientos técnicos en Ciberseguridad, así que utiliza un lenguaje muy sencillo, directo y sin tecnicismos. Evita explicaciones largas o complicadas. Sé conciso y ve al grano.

Sigue esta estructura aproximada (adáptala según el contenido del escaneo):

1. Breve resumen general del estado de seguridad
2. Lista de vulnerabilidades encontradas (si las hay)
3. Usuarios detectados (si los hay)
4. Plugins o temas problemáticos (solo si es WordPress)
5. Recomendaciones básicas que el usuario pueda aplicar

A continuación te proporciono los datos del escaneo en formato JSON:
{result}
"""

    response = co.generate(
        model='command-r-plus',
        prompt=prompt,
        max_tokens=800,
        temperature=0.7
    )

    return response.generations[0].text.strip()

def generatePDF(report, scan_id=None):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    file = f"report-{scan_id or timestamp}.pdf"

    base_path = os.path.join(os.getcwd(), "reports")
    os.makedirs(base_path, exist_ok=True)
    full_path = os.path.join(base_path, file)

    if os.path.exists(full_path):
        return full_path

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 25mm 20mm 25mm 20mm;
            }}
            body {{
                font-family: 'Source Sans 3', sans-serif;
                font-size: 12pt;
                color: #222;
                line-height: 1.5;
            }}
            h2 {{
                color: #005a9c;
                font-size: 20pt;
                margin: 10px 0 5px 0;
            }}
            img.logo {{
                width: 160px;
                margin-bottom: 10px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .summary {{
                background-color: #f9f9f9;
                padding: 20px;
                border-left: 4px solid #005a9c;
                border-radius: 4px;
                white-space: pre-wrap;
                word-break: break-word;
            }}
            .footer {{
                font-size: 10pt;
                color: #666;
                margin-top: 30px;
                border-top: 1px solid #ccc;
                padding-top: 10px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
        <img src="file://{os.getcwd()}/static/assets/img/LanzAuditLogo-Negro.png" class="logo"/>
        <h2>Informe del Escaneo {scan_id}</h2>
        </div>
        <div class="summary">
            {report}
        </div>
        <div class="footer">
            Reporte generado con IA automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} - LanzAudit
        </div>
    </body>
    </html>
    """
    HTML(string=html).write_pdf(full_path)
    return full_path
