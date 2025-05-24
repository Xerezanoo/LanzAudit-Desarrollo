import cohere
import os
from datetime import datetime
from weasyprint import HTML

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def generateSummary(result):
    prompt = f"""
Eres un asistente de Ciberseguridad. Haz un breve reporte en texto plano (no uses asteriscos ni caracteres de ese tipo) del siguiente resultado de un escaneo (puede ser Nmap o WPScan).
Ten en cuenta que este reporte va dirigido para un usuario de una empresa sin conocimientos técnicos en Ciberseguridad, así que todo fácil, sencillo, claro, conciso, sin rodeos ni complicaciones.

Me gustaría que llevara más o menos esta estructura, pero quiero que lo que NO aparezca en el resultado, que NO lo nombres en el reporte:
- Breve resumen
- Lista de vulnerabilidades relevantes
- Usuarios detectados
- Plugins o temas problemáticos
- Recomendaciones básicas

Aquí están los datos del escaneo (en JSON):
{result}
"""

    response = co.generate(
        model='command-r-plus',
        prompt=prompt,
        max_tokens=800,
        temperature=0.7
    )

    return response.generations[0].text.strip()

def generatePDF(summary, scan_id=None):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    file = f"summary-{scan_id or timestamp}.pdf"

    base_path = os.path.join(os.getcwd(), "static", "reports")
    os.makedirs(base_path, exist_ok=True)
    full_path = os.path.join(base_path, file)

    if os.path.exists(full_path):
        return full_path

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: sans-serif;
                margin: 30px;
            }}
            h1 {{
                color: #005a9c;
            }}
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f0f0f0;
                padding: 15px;
            }}
        </style>
    </head>
    <body>
        <img src="file://{os.getcwd()}/static/assets/LanzAuditLogo-Negro.png" style="width: 150px; margin-bottom: 20px;">
        <h1>Informe Escaneo {scan_id} -- {datetime.now().strftime('%Y-%m-%d %H:%M')}</h1>
        <pre>{summary}</pre>
    </body>
    </html>
    """
    HTML(string=html).write_pdf(full_path)
    return full_path
