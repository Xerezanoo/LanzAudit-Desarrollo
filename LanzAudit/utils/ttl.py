import subprocess

# Función para hacer ping al objetivo y devolver el TTL
def pingGetTtl(target):
    try:
        result = subprocess.run(["ping", "-c", "1", target], capture_output=True, text=True)
        if result.returncode == 0:
            # Busca el TTL en la salida
            ttl_line = next(line for line in result.stdout.splitlines() if "ttl=" in line)
            ttl = int(ttl_line.split("ttl=")[1].split()[0])
            return ttl
        else:
            return None
    except Exception as e:
        return None

def detectOS(ttl):
    if ttl is None:
        return "No disponible"
    elif ttl <= 64:
        return "Linux / Unix"
    elif ttl <= 128:
        return "Windows"
    elif ttl <= 255:
        return "Cisco / Otros"
    else:
        return "Desconocido"
