import time
import paramiko 
import os

# =====================================================================
# 1. VARIABLES GLOBALES
# =====================================================================
equipos = [
    {   #BRANCH2 
        "ip_gestion": "172.20.20.48", 
    },
    {   #HQ 
        "ip_gestion": "172.20.20.10", 
    }
]

# Comandos 
comandos_verificacion = [
    "show ip interface brief",
    "show dmvpn",
    "show ip route",
    "show ip eigrp 1 neighbors",
    "show crypto isakmp sa",
    "ping 192.168.10.10 source 192.168.50.2"
]

# =====================================================================
# 2. BUCLE DE EJECUCIÓN PRINCIPAL
# =====================================================================

for indice, device in enumerate(equipos):
    
    ip_del_equipo = device["ip_gestion"] # Extraemos la IP
    
    print(f"\n{'='*50}")
    print(f"## Procesando equipo: {ip_del_equipo} ##")
    print(f"{'='*50}")
    
    print("[*] : Ejecutando comandos de validación...")
    time.sleep(3) 
    
    for cmd in comandos_verificacion:
        
        
        if "ping" in cmd and indice != 0:
            continue
            
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # --- CONEXIÓN SSH ---
            client.connect(
                hostname=ip_del_equipo, 
                port=22,
                username="admin", password="admin",
                look_for_keys=False, allow_agent=False
            )
            
            print(f"\n--- Resultado de: {cmd} ---")
            
            # exec_command 
            stdin, stdout, stderr = client.exec_command(cmd)
            
            # Leemos la salida (stdout) y los posibles errores (stderr)
            resultado = stdout.read().decode('utf-8').strip()
            errores = stderr.read().decode('utf-8').strip()
            
            if resultado:
                print(resultado)
            elif errores:
                print(f"[ERROR DEL ROUTER]: {errores}")
            else:
                print("(Sin resultados. El comando no devolvió datos).")

        except Exception as e:
            print(f"\n[ERROR CRÍTICO] Fallo al ejecutar '{cmd}' en {ip_del_equipo}: {e}")
            
        finally:
            # Cerramos la conexión después de cada comando exitoso o fallido
            client.close()
            
    print(f"\n<< Validación completa en {ip_del_equipo}. Sesiones finalizadas de forma segura.")