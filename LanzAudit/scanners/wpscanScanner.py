import subprocess
import os
import json
from dotenv import load_dotenv

load_dotenv()
WPSCAN_API_KEY = os.getenv("WPSCAN_API_KEY")

def runWPScan(target, subtype, custom_options=None):
    if not WPSCAN_API_KEY:
        return {"error": "No se ha definido la API Key de WPScan."}

    # Comando base
    cmd = ["wpscan", "--url", target, "--api-token", WPSCAN_API_KEY, "--format", "json"]

    # Opciones según tipo de escaneo
    if subtype == "basic":
        pass  # Solo el escaneo base
    elif subtype == "vulns":
        cmd.append("--enumerate")
        cmd.append("vp,vt")
    elif subtype == "plugins":
        cmd.extend(["--enumerate", "p"])
    elif subtype == "themes":
        cmd.extend(["--enumerate", "t"])
    elif subtype == "users":
        cmd.extend(["--enumerate", "u"])
    elif subtype == "advanced":
        cmd.extend(["--enumerate", "ap,at,cb,dbe,m,tt,u,vp,vt"])
    elif subtype == "custom" and custom_options:
        cmd.extend(custom_options.strip().split())

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "El escaneo ha tardado demasiado y fue interrumpido."}
