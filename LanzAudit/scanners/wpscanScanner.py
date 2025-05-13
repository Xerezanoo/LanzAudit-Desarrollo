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
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=180)

        # Guardar logs en archivos para inspección
        with open('wpscan_stdout.log', 'w', encoding='utf-8') as f:
            f.write(stdout)
        with open('wpscan_stderr.log', 'w', encoding='utf-8') as f:
            f.write(stderr)

        if process.returncode == 0:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError as e:
                return {"error": f"Error al convertir la salida a JSON: {str(e)}"}
        else:
            return {"error": stderr or "Error desconocido en WPScan."}
    
    except subprocess.TimeoutExpired:
        return {"error": "El escaneo ha tardado demasiado y fue interrumpido."}
