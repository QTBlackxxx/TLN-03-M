#!/usr/bin/env python3

import paramiko
import time
from getpass import getpass
from colorama import Fore, Style, init

# Solución para que python detecte scripts/ como módulo y permita importar desde configs.comandos
import sys
sys.path.insert(0, '/home/antonio/Escritorio/TLN-03-M/Topologias/scripts')  ##Cambiar ruta
from configs.comandos_modify import COMANDOS

# ==========================================================
# Inicialización Colorama
# ==========================================================

init(autoreset=True)

# ==========================================================
# Clase Device
# ==========================================================

class device(object):

    def __init__(self, hostname, username, password):

        self.hostname = hostname
        self.username = username
        self.password = password

    def set_password(self):

        self.password = getpass(
            prompt=f"\n\nIngresar contraseña para: "
                   f"{self.username}@{self.hostname}: "
        )

# ==========================================================
# Conexión SSH
# ==========================================================

def conexion_ssh(device):

    try:

        ssh_client = paramiko.SSHClient()

        ssh_client.load_system_host_keys()

        ssh_client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        ssh_client.connect(

            hostname=device.hostname,
            username=device.username,
            password=device.password,
            port=22,
            look_for_keys=False

        )

        print(

            f"\n\n{Fore.GREEN}{Style.BRIGHT}Conexión exitosa a "
            f"{Fore.YELLOW}{device.hostname}"
            f"{Style.RESET_ALL}"

        )

        return ssh_client

    except Exception as e:

        print(

            f"{Fore.RED}{Style.BRIGHT}"
            f"Error al conectar a {device.hostname}: {e}"
            f"{Style.RESET_ALL}"

        )

        return None

# ==========================================================
# Configuración -> invoke_shell()
# ==========================================================

def ssh_config(ssh_client, comandos_config):

    try:

        shell = ssh_client.invoke_shell()

        time.sleep(2)

        # Limpia buffer inicial
        shell.recv(65535)

        # Desactiva paginación
        shell.send("terminal length 0\n")

        time.sleep(1)

        shell.recv(65535)

        print(

            f"\n{Fore.CYAN}{Style.BRIGHT}"
            f"Aplicando configuración..."
            f"{Style.RESET_ALL}"

        )

        for comando in comandos_config:

            print(

                f"{Fore.YELLOW}"
                f"Enviando -> {comando}"
                f"{Style.RESET_ALL}"

            )

            shell.send(comando + "\n")

            time.sleep(2)

        # Espera final
        time.sleep(3)

        salida = ""

        while shell.recv_ready():

            salida += shell.recv(65535).decode()

            time.sleep(1)

        print(

            f"\n{Fore.GREEN}{Style.BRIGHT}"
            f"Resultado configuración:"
            f"{Style.RESET_ALL}"

        )

        print(salida)

    except Exception as e:

        print(

            f"{Fore.RED}{Style.BRIGHT}"
            f"Error en configuración: {e}"
            f"{Style.RESET_ALL}"

        )

# ==========================================================
# Verificación -> exec_command()
# ==========================================================

def ssh_verify(ssh_client, comandos_show):

    try:

        print(

            f"\n{Fore.CYAN}{Style.BRIGHT}"
            f"Verificación:"
            f"{Style.RESET_ALL}"

        )

        for comando in comandos_show:

            print(

                f"\n{Fore.MAGENTA}{Style.BRIGHT}"
                f"--- {comando} ---"
                f"{Style.RESET_ALL}"

            )

            stdin, stdout, stderr = ssh_client.exec_command(
                comando
            )

            salida = stdout.read().decode()

            error = stderr.read().decode()

            if salida:

                print(salida)

            if error:

                print(

                    f"{Fore.RED}{Style.BRIGHT}"
                    f"ERROR:"
                    f"{Style.RESET_ALL}"

                )

                print(error)

    except Exception as e:

        print(

            f"{Fore.RED}{Style.BRIGHT}"
            f"Error en verificación: {e}"
            f"{Style.RESET_ALL}"

        )

# ==========================================================
# Ejecución múltiple
# ==========================================================

def ssh_exec_multiple(comandos):

    try:

        password = getpass(
            "\nIngrese password para todos los routers: "
        )

        for hostname, datos in comandos.items():

            print(

                f"\n{Fore.BLUE}{Style.BRIGHT}"
                f"=================================================="
                f"\nDEVICE -> {hostname}"
                f"\n=================================================="
                f"{Style.RESET_ALL}"

            )

            device_obj = device(
                hostname,
                "admin",
                password
            )

            ssh_client = conexion_ssh(device_obj)

            if ssh_client:

                # ==========================================
                # CONFIGURACIÓN
                # ==========================================

                ssh_config(
                    ssh_client,
                    datos["configuracion"]
                )

                # ==========================================
                # VERIFICACIÓN
                # ==========================================

                ssh_verify(
                    ssh_client,
                    datos["verificacion"]
                )

                ssh_client.close()

                print(

                    f"\n{Fore.GREEN}{Style.BRIGHT}"
                    f"Conexión cerrada -> {hostname}"
                    f"{Style.RESET_ALL}"

                )

    except Exception as e:

        print(

            f"{Fore.RED}{Style.BRIGHT}"
            f"Error general: {e}"
            f"{Style.RESET_ALL}"

        )

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    ssh_exec_multiple(COMANDOS)