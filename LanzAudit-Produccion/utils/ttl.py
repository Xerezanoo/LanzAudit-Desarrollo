import subprocess

# Función para hacer ping al objetivo y devolver el valor del TTL (Time to Live)
def pingGetTtl(target):
    try:
        # Ejecuta el comando ping con 1 paquete al objetivo
        result = subprocess.run(["/usr/bin/ping", "-c", "1", target], capture_output=True, text=True)
        
        # Busca una línea en la salida que contenga "ttl="
        ttl_line = next(line for line in result.stdout.splitlines() if "ttl=" in line)
        
        # Guarda el valor del TTL como un entero en la variable 'ttl'
        if ttl_line:
            ttl = int(ttl_line.split("ttl=")[1].split()[0])
            return ttl  # Devuelve el valor del TTL encontrado
        
    except Exception as error:
        # En caso de error (comando no disponible o problema de conexión por ejemplo), devuelve None
        return None

# Función para determinar el sistema operativo probable basado en el TTL
def detectOS(ttl):
    if ttl is None:
        # Si el TTL no está disponible, devuelve "No disponible"
        return "No disponible"
    elif ttl <= 64:
        # TTL típico para sistemas basados en Linux o Unix
        return "Linux / Unix"
    elif ttl <= 128:
        # TTL típico para sistemas Windows
        return "Windows"
    elif ttl <= 255:
        # TTL típico para dispositivos de red como routers (por ejemplo, los de Cisco)
        return "Cisco / Otros"
    else:
        # Si el TTL no coincide con los rangos anteriores, devuelve "Desconocido"
        return "Desconocido"
