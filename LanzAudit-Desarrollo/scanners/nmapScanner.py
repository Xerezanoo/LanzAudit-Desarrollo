# nmapScanner.py

import nmap
from utils.ttl import pingGetTtl

# Ejecuta un escaneo Nmap según el tipo especificado y devuelve el resultado y el TTL del host. Si da algún error, se especifica
def runNmapScan(target, scan_type, ports=None):
    nm = nmap.PortScanner()
    
    # Obtiene el TTL del host con un ping
    ttl = pingGetTtl(target)
    
    try:
        if scan_type == "fast":
            nm.scan(hosts=target, arguments="-F -T4")
        elif scan_type == "full":
            nm.scan(hosts=target, arguments="-p- -sVC--min-rate 5000")
        elif scan_type == "versions":
            nm.scan(hosts=target, arguments="-sV")
        elif scan_type == "discovery":
            nm.scan(hosts=target, arguments="-sn")
        elif scan_type == "custom" and ports:
            nm.scan(hosts=target, arguments="-sVC" , ports=ports)
        else:
            return False, {"error": "Tipo de escaneo inválido o puertos no especificados."}, ttl
    except Exception as error:
        return False, {"error": str(error)}, ttl
    
    all_hosts = nm.all_hosts()
    if not all_hosts:
        return False, {"error": "Ningún host activo detectado."}, ttl
        
    return True, nm._scan_result, ttl

def validatePorts(ports):
    # Verifica si los puertos están en el formato adecuado (números o rangos como "22,80,443" o "1-1000")
    try:
        port_list = ports.split(",")
        for port in port_list:
            if "-" in port:
                # Verifica que el rango de puertos sea válido y que ambos extremos sean números
                start, end = port.split("-")
                if not (start.isdigit() and end.isdigit() and int(start) < int(end)):
                    return False
            elif not port.isdigit():
                return False
        return True
    except Exception:
        return False
