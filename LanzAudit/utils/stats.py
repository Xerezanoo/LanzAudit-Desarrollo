import json
from collections import Counter
from models import Scan,ScanResults

def topOpenPorts(n=5):
    # Obtener todos los resultados de escaneos desde la base de datos
    all_results = ScanResults.query.join(Scan).filter(
        Scan.scan_type == 'Nmap',
        Scan.status == 'Completado'
    ).all()
    
    # Crear un contador para contar las veces que se han encontrado los puertos abiertos
    port_counter = Counter()

    for result in all_results:
        try:
            # Obtener los datos del escaneo en formato JSON
            data = result.result
            # Extraer los datos del apartado 'scan', que es donde se encuentra la información obtenida en el escaneo
            scan_data = data.get("scan", {})

            # Hacemos un bucle sobre cada host en los resultados del escaneo
            for host_info in scan_data.values():
                # Obtener los puertos TCP del host
                tcp_ports = host_info.get("tcp", {})

                # Hacemos otro bucle sobre cada puerto y sus datos
                for port, port_data in tcp_ports.items():
                    # Si el puerto está abierto, contarlo
                    if port_data.get("state") == "open":
                        port_counter[int(port)] += 1
        except Exception as error:
            # Si ocurre un error, mostrar un mensaje y continuar con el siguiente resultado
            print(f"Error procesando scan_result {result.id}: {error}")
            continue

    # Devolver los 'n' puertos más comunes con sus cuentas
    return port_counter.most_common(n)


PORT_SERVICE_NAMES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    69: "TFTP",
    80: "HTTP",
    88: "Kerberos",
    110: "POP3",
    119: "NNTP",
    135: "MS RPC",  
    137: "NetBIOS-NS", 
    138: "NetBIOS-DGM", 
    139: "NetBIOS",
    143: "IMAP",
    161: "SNMP",
    162: "SNMPTRAP",
    177: "X Windows",
    194: "IRC", 
    443: "HTTPS",
    445: "SMB",
    465: "SMTP-SSL",
    513: "Rlogin", 
    514: "Syslog",
    543: "Kerberos",
    544: "klogin",
    563: "NNTPS",
    587: "SMTP (Submission)",
    593: "RPC HTTP",
    623: "IPMI",
    631: "IPP",
    636: "LDAPS",
    6660: "IRC", 
    6666: "IRC",  
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    6660: "IRC", 
    8080: "HTTP-alt",
    8081: "HTTP-alt2", 
    8443: "HTTPS-alt", 
    8888: "HTTP-alt3",  
    9200: "Elasticsearch",
    9300: "Elasticsearch TCP",
    10000: "Webmin",
    11211: "Memcached",
    27017: "MongoDB",
    3128: "Squid Proxy",
    5000: "UPnP",
    5009: "UPnP", 
    5432: "PostgreSQL",
    5900: "VNC",
    8081: "HTTP-alt4",
    49152: "DynDNS",
    49153: "RDP",
    49154: "RDP",
    49155: "RDP",
    49156: "RDP",
    49157: "RDP",
    49158: "RDP",
    49159: "RDP",
    49160: "RDP",
    49161: "RDP",
    49162: "RDP",
    49163: "RDP",
    49164: "RDP",
    49165: "RDP",
    49166: "RDP",
    49167: "RDP",
    49168: "RDP",
    49169: "RDP",
    49170: "RDP",
    49171: "RDP",
    49172: "RDP",
    49173: "RDP",
    49174: "RDP",
    49175: "RDP",
    49176: "RDP",
    49177: "RDP",
    49178: "RDP",
    49179: "RDP",
    49180: "RDP",
    49181: "RDP",
    49182: "RDP",
    49183: "RDP",
    49184: "RDP",
    49185: "RDP",
    49186: "RDP",
    49187: "RDP",
    49188: "RDP",
    49189: "RDP",
    49190: "RDP",
    49191: "RDP",
    49192: "RDP",
    49193: "RDP",
    49194: "RDP",
    49195: "RDP",
    49196: "RDP",
    49197: "RDP",
    49198: "RDP",
    49199: "RDP",
    50000: "UPnP",
    50200: "HTTP",
}

PORT_ICONS = {
    21: "bi bi-terminal",    
    22: "bi bi-terminal",    
    23: "bi bi-terminal",       
    25: "bi bi-envelope",     
    53: "bi bi-globe",       
    67: "bi bi-server",       
    69: "bi bi-download",     
    80: "bi bi-globe",        
    88: "bi bi-shield-lock",      
    110: "bi bi-envelope",    
    119: "bi bi-envelope",    
    135: "bi bi-server",        
    137: "bi bi-network",  
    138: "bi bi-network",         
    139: "bi bi-network",        
    143: "bi bi-envelope-open",
    161: "bi bi-gear",
    162: "bi bi-gear",            
    177: "bi bi-window",          
    194: "bi bi-chat",       
    443: "bi bi-lock",        
    445: "bi bi-server",     
    465: "bi bi-lock",            
    513: "bi bi-terminal",      
    514: "bi bi-terminal",      
    543: "bi bi-shield-lock",     
    544: "bi bi-lock",          
    563: "bi bi-shield-lock",  
    587: "bi bi-envelope-check", 
    593: "bi bi-network",         
    623: "bi bi-shield-lock", 
    631: "bi bi-printer",    
    636: "bi bi-shield-lock",  
    6660: "bi bi-chat",      
    6666: "bi bi-chat",      
    3306: "bi bi-database",    
    3389: "bi bi-terminal",  
    5432: "bi bi-database",       
    5900: "bi bi-tv",        
    6379: "bi bi-database",    
    8080: "bi bi-globe",          
    8081: "bi bi-globe",          
    8443: "bi bi-globe",          
    8888: "bi bi-globe",          
    9200: "bi bi-globe",          
    9300: "bi bi-globe",          
    10000: "bi bi-server",      
    11211: "bi bi-server",        
    27017: "bi bi-database",     
    3128: "bi bi-server",       
    5000: "bi bi-house-door", 
    5009: "bi bi-house-door", 
    49152: "bi bi-server",      
    49153: "bi bi-terminal", 
    49154: "bi bi-terminal", 
    49155: "bi bi-terminal", 
    49156: "bi bi-terminal", 
    49157: "bi bi-terminal", 
    49158: "bi bi-terminal", 
    49159: "bi bi-terminal", 
    50000: "bi bi-house-door",
    50200: "bi bi-globe"                
}

def totalVulns():
    wpscan_results = ScanResults.query.join(Scan).filter(
        Scan.scan_type == 'WPScan',
        Scan.status == 'Completado'
    ).all()

    total_vulns = 0

    for result in wpscan_results:
        try:
            data = result.result 

            if isinstance(data, str):
                data = json.loads(data)

            if 'plugins' in data:
                for plugin in data['plugins'].values():
                    vulns = plugin.get('vulnerabilities', [])
                    total_vulns += len(vulns)

            if 'themes' in data:
                for theme in data['themes'].values():
                    vulns = theme.get('vulnerabilities', [])
                    total_vulns += len(vulns)

            if 'version' in data and 'vulnerabilities' in data['version']:
                total_vulns += len(data['version']['vulnerabilities'])

        except Exception as error:
            print(f"Error procesando resultado WPScan: {error}")

    return total_vulns

def topThemes(n=5):
    all_results = ScanResults.query.join(Scan).filter(
        Scan.scan_type == 'WPScan',
        Scan.status == 'Completado'
    ).all()
    themes_counter = Counter()

    for result in all_results:
        try:
            data = result.result if isinstance(result.result, dict) else json.loads(result.result)
            themes_data = data.get("themes", {})

            for slug, theme_info in themes_data.items():
                theme_name = theme_info.get("style_name", slug)
                themes_counter[theme_name] += 1

        except Exception as error:
            print(f"Error procesando scan_result {result.id}: {error}")
            continue

    # Devolver lista de diccionarios para el render
    return [{"name": a, "count": b} for a, b in themes_counter.most_common(n)]

def topPlugins(n=5):
    all_results = ScanResults.query.join(Scan).filter(
        Scan.scan_type == 'WPScan',
        Scan.status == 'Completado'
    ).all()
    plugins_counter = Counter()

    for result in all_results:
        try:
            data = result.result if isinstance(result.result, dict) else json.loads(result.result)
            plugins_data = data.get("plugins", {})

            for slug, plugin_info in plugins_data.items():
                plugin_name = plugin_info.get("slug", slug)
                if plugin_name != "*":
                    plugins_counter[plugin_name] += 1

        except Exception as error:
            print(f"Error procesando scan_result {result.id}: {error}")
            continue

    return [{"name": a, "count": b} for a, b in plugins_counter.most_common(n)]

def vulnerableThemes(n=5):
    all_results = ScanResults.query.join(Scan).filter(
        Scan.scan_type == 'WPScan',
        Scan.status == 'Completado'
    ).all()
    vuln_counter = Counter()

    for result in all_results:
        try:
            data = result.result if isinstance(result.result, dict) else json.loads(result.result)
            themes_data = data.get("themes", {})

            for slug, theme_info in themes_data.items():
                vulns = theme_info.get("vulnerabilities", [])
                if vulns:
                    theme_name = theme_info.get("style_name", slug)
                    vuln_counter[theme_name] += len(vulns)

        except Exception as e:
            print(f"Error procesando scan_result {result.id}: {e}")
            continue

    return [{"name": a, "count": b} for a, b in vuln_counter.most_common(n)]

def vulnerablePlugins(n=5):
    all_results = ScanResults.query.join(Scan).filter(
        Scan.scan_type == 'WPScan',
        Scan.status == 'Completado'
    ).all()
    vuln_counter = Counter()

    for result in all_results:
        try:
            data = result.result if isinstance(result.result, dict) else json.loads(result.result)
            plugins_data = data.get("plugins", {})

            for slug, plugin_info in plugins_data.items():
                vulns = plugin_info.get("vulnerabilities", [])
                if slug != "*" and vulns:
                    plugin_name = plugin_info.get("slug", slug)
                    vuln_counter[plugin_name] += len(vulns)

        except Exception as error:
            print(f"Error procesando scan_result {result.id}: {error}")
            continue

    return [{"name": a, "count": b} for a, b in vuln_counter.most_common(n)]