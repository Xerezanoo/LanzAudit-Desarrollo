from subprocess import call

def get_host():
    target = input("Introduce el host al que deseas hacerle el scan: ")
    return target

def get_ports():
    portnumber = input("Introduce el puerto o los puertos que deseas escanear (Si deseas un rango de puertos, escribelos de la manera 1-1000): ")
    return portnumber

def intensescan(target):
    call(["sudo","nmap","-A","-T4","-sS","-Pn","-O","-sV","-p","1-10000","-v", target])

def fastscan(target):
    call(["nmap","--open","-F", target])

def detectserv(target):
    call(["nmap","-sP", target])

def detectver(target):
    call(["nmap","-sV", target])

def escanport(target, portnumber):
    call(["nmap","-p", portnumber, target])

def recsystem(target):
    call(["sudo","nmap","-O", target])

def enumdns(target):
    call(["dnsenum", target])

def bypasscloud(target):
    try:
        call(["fierce","-dns", target]) 
    except OSError:
        call(["fierce.pl","-dns", target])
    except Exception as e:
        print("Ha ocurrido un error:", e)

def menu():
    while True:
        print("""
        a) Escaneo full de un host (Lento pero el mas completo).
        b) Escaneo rapido de un host.
        c) Detectar servidores corriendo de un host.
        d) Detectar versiones de los servicios corriendo en un host.
        e) Escanear un puerto especifico o un rango de puertos.
        f) Detectar el sistema operativo de un host.
        g) Enumerar los DNS de un host.
        h) Bypassear cloudflare.
        i) Salir.
        """)
        sel = input("Introduce tu opcion: ")
        
        if sel == "a":
            target = get_host()
            intensescan(target)
        elif sel == "b":
            target = get_host()
            fastscan(target)
        elif sel == "c":
            target = get_host()
            detectserv(target)
        elif sel == "d":
            target = get_host()
            detectver(target)
        elif sel == "e":
            target = get_host()
            portnumber = get_ports()
            escanport(target, portnumber)
        elif sel == "f":
            target = get_host()
            recsystem(target)
        elif sel == "g":
            target = get_host()
            enumdns(target)
        elif sel == "h":
            target = get_host()
            bypasscloud(target)
        elif sel == "i":
            print("Saliendo.")
            break
        else:
            print("Opción inválida. Intenta nuevamente.")

menu()
