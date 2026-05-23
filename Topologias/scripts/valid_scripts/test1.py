#!/usr/bin/env python3

import paramiko
from getpass import getpass
import time
import sys

sys.path.insert(0, '/home/antonio/Escritorio/TLN-03-M/Topologias/scripts')
from configs.comandos_modify import COMANDOS

password = getpass("Ingrese password: ")

routers = {
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2": {
        "configuracion": COMANDOS["clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2"],
        "verificacion": [
            "show ip interface brief",
            "show ip route",
            "show running-config interface Loopback0"
        ]
    },
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK": {
        "configuracion": COMANDOS["clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK"],
        "verificacion": [
            "show ip interface brief",
            "show ip route",
            "show running-config interface Loopback0"
        ]
    }
}

for router, datos in routers.items():
    print(f"\n======== {router} ========\n")

    # ==========================================================
    # PARTE 1: CONFIGURACIÓN con invoke_shell()
    # ==========================================================
    print("\n--- Aplicando configuración ---\n")
    
    cliente_config = paramiko.SSHClient()
    cliente_config.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    cliente_config.connect(
        hostname=router,
        username="admin",
        password=password,
        port=22
    )
    
    shell = cliente_config.invoke_shell()
    time.sleep(2)
    
    # Limpiar buffer
    shell.recv(65535)
    
    # Desactivar paginación
    shell.send("terminal length 0\n")
    time.sleep(1)
    shell.recv(65535)
    
    # Enviar comandos de configuración
    for comando in datos["configuracion"]:
        print(f"Enviando: {comando}")
        shell.send(comando + "\n")
        time.sleep(1)
    
    time.sleep(2)
    
    # Leer salida de configuración
    salida_config = ""
    while shell.recv_ready():
        salida_config += shell.recv(65535).decode()
        time.sleep(0.5)
    
    print("\n--- Resultado configuración ---\n")
    print(salida_config)
    
    # CERRAR la conexión de configuración
    cliente_config.close()
    
    # Esperar que los recursos se liberen
    time.sleep(2)
    
# ==========================================================
# PARTE 2: VERIFICACIÓN con exec_command()
# ==========================================================
print("\n--- Verificación ---\n")

for comando in datos["verificacion"]:
    print(f"\n--- {comando} ---\n")
    
    # Crear NUEVA conexión para CADA comando
    cliente_verif = paramiko.SSHClient()
    cliente_verif.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    cliente_verif.connect(
        hostname=router,
        username="admin",
        password=password,
        port=22,
        timeout=30
    )
    
    try:
        stdin, stdout, stderr = cliente_verif.exec_command(comando)
        
        salida = stdout.read().decode()
        error = stderr.read().decode()
        
        if salida:
            print(salida)
        if error:
            print("ERROR:", error)
    except Exception as e:
        print(f"Error ejecutando {comando}: {e}")
    finally:
        cliente_verif.close()
        time.sleep(1)  # Pausa entre conexiones

print(f"\n--- Verificación de {router} completada ---\n")