import nmap

def scanPortsNmap(host, ports):
    nm = nmap.PortScanner()
    try:
        nm.scan(host, ports)
        openPorts = []
        for port in ports.split(","):
            port = int(port)
            if nm[host].has_tcp(port) and nm[host]["tcp"][port]["state"] == "open":
                openPorts.append(port)
        return openPorts
    except Exception as error:
        print(f"Error al escanear: {error}")
        return []
