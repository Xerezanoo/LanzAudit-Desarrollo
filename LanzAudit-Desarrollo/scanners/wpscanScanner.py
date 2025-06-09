# wpscanScanner.py

import subprocess
import os
import json
from dotenv import load_dotenv

load_dotenv()
WPSCAN_API_KEY = os.getenv("WPSCAN_API_KEY")

# Ejecuta un escaneo con WPScan según el tipo especificado
def runWPScan(target, subtype, options=None):
    if not WPSCAN_API_KEY:
        return {"error": "No se ha definido la API Key de WPScan."}

    # Comando base para ejecutar WPScan para que devuelva el resultado en formato JSON
    cmd = ["/usr/local/bin/wpscan", "--url", target, "--api-token", WPSCAN_API_KEY, "--format", "json"]

    if subtype == "basic":
        pass
    elif subtype == "full":
        cmd.extend(["--enumerate", "ap,at,cb,u", "--plugins-detection", "aggressive"])
    elif subtype == "vulns":
        cmd.extend(["--enumerate", "vp,vt"])
    elif subtype == "plugins":
        cmd.extend(["--enumerate", "ap", "--plugins-detection", "aggressive"])
    elif subtype == "themes":
        cmd.extend(["--enumerate", "at"])
    elif subtype == "users":
        cmd.extend(["--enumerate", "u"])
    elif subtype == "custom" and options:
        cmd.extend(options.strip().split())

    try:
        # Ejecuta el comando con subprocess y devuelve los errores si los hay
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=300)
    
        try:
            return json.loads(stdout) # Devuelve la salida parseada como JSON
        except json.JSONDecodeError as e:
            if "Scan Aborted:" in stdout:
                return {
                    "scan_aborted": stdout.strip()
                }
            return {
                "error": "Error al parsear la salida JSON de WPScan.",
                "exception": str(e),
                "raw_output": stdout,
                "stderr": stderr
            }
    
    except subprocess.TimeoutExpired:
        return {"error": "El escaneo ha tardado demasiado y fue interrumpido."}
    except Exception as error:
        return {"error": f"Error inesperado al ejecutar WPScan: {str(error)}"}