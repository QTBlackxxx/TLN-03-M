import time
import paramiko 
import os

# =====================================================================
# 1. VARIABLES GLOBALES
# =====================================================================
equipos = [
    {   # SEDE REMOTA BRANCH2
        "hostname": "CPE-BRANCH2",
        "ip_gestion": "172.20.20.48", 
        "archivo_txt": "configuraciones/CPE-BRANCH2.txt" 
    },
    {   # SEDE REMOTA BRANCH2-BK
        "hostname": "CPE-BRANCH2-BK",
        "ip_gestion": "172.20.20.49", 
        "archivo_txt": "configuraciones/CPE-BRANCH2-BK.txt" 
    },
    {   # SWITCH DE LA SEDE BRANCH2
        "hostname": "SW-R2-PISO1",
        "ip_gestion": "172.20.20.50",  
        "archivo_txt": "configuraciones/SW.txt" 
    },
    {   # ISP M2
        "hostname": "M2",
        "ip_gestion": "172.20.20.19",
        "archivo_txt": "configuraciones/M2.txt" 
    },
    {   # ISP C2
        "hostname": "C2",
        "ip_gestion": "172.20.20.31", 
        "archivo_txt": "configuraciones/C2.txt" 
    },
    {   # SEDE PRINCIPAL HQ
        "hostname": "CPE-HQ",
        "ip_gestion": "172.20.20.10", 
        "archivo_txt": "configuraciones/CPE-HQ.txt" 
    },
    {   # SEDE PRINCIPAL HQ-BK
        "hostname": "CPE-HQ-BK",
        "ip_gestion": "172.20.20.11",  
        "archivo_txt": "configuraciones/CPE-HQ-BK.txt" 
    },
    {   # SEDE REMOTA BRANCH
        "hostname": "CPE-BRANCH",
        "ip_gestion": "172.20.20.22",  
        "archivo_txt": "configuraciones/CPE-BRANCH1.txt" 
    },
    {   # SEDE REMOTA BRANCH-BK
        "hostname": "CPE-BRANCH-BK",
        "ip_gestion": "172.20.20.23", 
        "archivo_txt": "configuraciones/CPE-BRANCH1-BK.txt" 
    }
]

# =====================================================================
# 2. BUCLE DE EJECUCIÓN PRINCIPAL
# =====================================================================
for device in equipos:
    ip_actual = device["ip_gestion"]
    archivo_actual = device["archivo_txt"]
    nombre_equipo = device.get("hostname", ip_actual)

    print(f"\n{'='*60}")
    print(f"## Procesando: {nombre_equipo} ({ip_actual}) ##")
    print(f"{'='*60}")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip_actual, 
            port=22,
            username="admin", 
            password="admin",
            look_for_keys=False, 
            allow_agent=False,
            timeout=10 
        )
        
        print(f"[*] FASE 1: Conectado a {nombre_equipo}. Iniciando shell...")
        ssh_shell = client.invoke_shell()
        time.sleep(1) 
        
        # Preparamos la terminal
        ssh_shell.send("terminal length 0\n")
        time.sleep(0.5)
        ssh_shell.send("configure terminal\n")
        time.sleep(0.5)

        if not os.path.exists(archivo_actual):
            print(f"\n[ERROR] No se encuentra el archivo: {archivo_actual}")
            print("Saltando al siguiente dispositivo...\n")
            continue 

        # ---------------------------------------------------------
        # Lectura e inyeccion
        # ---------------------------------------------------------
        comandos_validos = []
        with open(archivo_actual, 'r') as file:
            for linea in file:
                comando = linea.strip()
                if comando and not comando.startswith(("{#", "!")):
                    comandos_validos.append(comando)

        for comando in comandos_validos:
            print(f"   Inyectando > {comando}")
            ssh_shell.send(comando + "\n")
            time.sleep(0.02) # Retardo mínimo para que se vea en terminal sin frenar la ejecución

        # Damos tiempo al final para que el router asimile comandos pesados 
        time.sleep(2)
        # ---------------------------------------------------------

        # Finalizamos y guardamos
        ssh_shell.send("end\n")
        time.sleep(1)
        ssh_shell.send("write memory\n")
        time.sleep(2)
        
        ssh_shell.close() 
        print(f"\n[+] Configuración aplicada y guardada en {nombre_equipo}.\n")

    except Exception as e:
        print(f"\n[ERROR CRÍTICO] Fallo en {nombre_equipo} ({ip_actual}): {e}")
    finally:
        client.close()
        print(f"<< Sesión con {nombre_equipo} finalizada.")