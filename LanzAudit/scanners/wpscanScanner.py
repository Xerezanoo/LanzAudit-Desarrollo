import subprocess
import os
import json
from dotenv import load_dotenv

load_dotenv()
WPSCAN_API_KEY = os.getenv("WPSCAN_API_KEY")

def runWPScan(target, subtype, options=None):
    if not WPSCAN_API_KEY:
        return {"error": "No se ha definido la API Key de WPScan."}

    cmd = ["wpscan", "--url", target, "--api-token", WPSCAN_API_KEY, "--format", "json"]

    if subtype == "basic":
        pass
    elif subtype == "vulns":
        cmd.extend(["--enumerate", "vp,vt"])
    elif subtype == "plugins":
        cmd.extend(["--enumerate", "p"])
    elif subtype == "themes":
        cmd.extend(["--enumerate", "t"])
    elif subtype == "users":
        cmd.extend(["--enumerate", "u"])
    elif subtype == "custom" and options:
        cmd.extend(options.strip().split())

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "summary": extractSummary(data, subtype),
                "details": data
            }
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "El escaneo ha tardado demasiado y fue interrumpido."}


# Función de filtrado de resultados para obtener un resumen
def extractSummary(data, subtype):
    summary = {
        "url": data.get("target_url", "No disponible"),
        "version": data.get("version", {}).get("number", "Desconocida"),
        "interestingFindings": len(data.get('interesting_findings', [])),
        "mainTheme": data.get('main_theme', {}).get('slug', 'Desconocido').capitalize()
    }

    if subtype == "basic":
        summary["totalVulns"] = len(data.get("vulnerabilities", []))
    elif subtype == "vulns":
        important = sum(1 for v in data.get("vulnerabilities", []) if v.get("severity") == "high")
        low = sum(1 for v in data.get("vulnerabilities", []) if v.get("severity") == "low")
        summary.update({
            "totalVulns": len(data.get("vulnerabilities", [])),
            "importantVulns": important,
            "nonImportantVulns": low
        })
    elif subtype == "plugins":
        summary["totalPlugins"] = len(data.get("plugins", []))
    elif subtype == "themes":
        summary["totalThemes"] = len(data.get("themes", []))
    elif subtype == "users":
        summary["totalUsers"] = len(data.get("users", []))

    return summary