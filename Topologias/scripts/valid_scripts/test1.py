#!/usr/bin/env python3

import paramiko
from getpass import getpass
import time

# Autor: Antonio Alejandro Saenz Camero
# Objetivo: Primer acercamiento a la automatización de tareas en routers Cisco usando Python y Paramiko.
# Test1: 2 routers (M1 y M2), comandos show básicos.

password = getpass("Ingrese password: ")

routers = [
    "clab-ISP-TDP-CLARO-IOL-M1",
    "clab-ISP-TDP-CLARO-IOL-M2"
]

comandos = [
    "show ip interface brief",
    "show version"
]

for router in routers:

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

    # Espera inicial para estabilizar sesión SSH
    time.sleep(2)

    # Limpia buffer inicial
    shell.recv(65535)

    # Desactiva paginación en Cisco IOS
    shell.send("terminal length 0\n")

    time.sleep(1)

    # Limpia salida del comando anterior
    shell.recv(65535)

    for comando in comandos:

        print(f"\n--- {comando} ---\n")

        shell.send(comando + "\n")

        time.sleep(3)

        salida = ""

        # Lee toda la salida disponible
        while shell.recv_ready():

            salida += shell.recv(65535).decode()

            time.sleep(1)

        print(salida)

    cliente.close()