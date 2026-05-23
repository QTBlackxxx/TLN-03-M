#!/usr/bin/env python3

import paramiko
from getpass import getpass
import time

# Autor: Antonio Alejandro Saenz Camero
# Objetivo: Automatización básica de comandos show usando Python y Paramiko.
# Test2: Diccionario escalable, routers con comandos "show" personalizados.

password = getpass("Ingrese password: ")

routers = {

    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": [
        "show ip interface brief",
        "show version",
        "show ip route"
    ],

    "clab-ISP-TDP-CLARO-IOL-M1": [
        "show ip ospf neighbor",
        "show ip bgp summary",
        "show running-config",
        "show ip interface brief"
    ],

    "clab-ISP-TDP-CLARO-IOL-M3": [
        "show ip ospf neighbor",
        "show ip bgp summary",
        "show running-config",
        "show ip interface brief"
    ],
}

for router, comandos in routers.items():

    print(f"\n======== {router} ========\n")

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    cliente.connect(
        hostname=router,
        username="admin",
        password=password,
        port=22
    )

    shell = cliente.invoke_shell()

    # Espera inicial
    time.sleep(2)

    # Limpia buffer inicial
    shell.recv(65535)

    # Desactiva paginación Cisco
    shell.send("terminal length 0\n")

    time.sleep(1)

    shell.recv(65535)

    for comando in comandos:

        print(f"\n--- {comando} ---\n")

        shell.send(comando + "\n")

        time.sleep(3)

        salida = ""

        while shell.recv_ready():

            salida += shell.recv(65535).decode()

            time.sleep(1)

        print(salida)

    cliente.close()