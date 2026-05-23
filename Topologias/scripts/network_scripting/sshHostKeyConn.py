import paramiko
import time
import json
from getpass import getpass
from colorama import Fore, Style, init
from configs.comandos import COMANDOS
from configs.comandos_validacion import COMANDOS_SUP

class device(object):
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
    
    def set_password(self):
        self.password = getpass(prompt=f"\n\nIngresar contraseña para: {self.username}@{self.hostname}: ")

def conexion_ssh(device):

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=device.hostname, 
            username=device.username, 
            password=device.password,
            look_for_keys=False
        )

        #print(f"{Fore.GREEN}{Style.BRIGHT}Conexión exitosa a {device.hostname}{Style.RESET_ALL}")
        print(
            f"\n\n{Fore.GREEN}{Style.BRIGHT}Conexión exitosa a "
            f"{Fore.YELLOW}{device.hostname}"
            f"{Style.RESET_ALL}", end = ""
        )
        separador = "=" * 70
        encabezado = f"\n{separador}\n  DISPOSITIVO: {device.hostname}\n{separador}"

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{encabezado}{Style.RESET_ALL}", end = "")

        return ssh_client

    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}Error al conectar a {device.hostname}: {e}{Style.RESET_ALL}")
        return None

def ssh_exec(ssh_client, comandos):
    try:
        SHELL_ACCESO = ssh_client.invoke_shell()
        SHELL_ACCESO.send("terminal length 0\n")
        time.sleep(0.5)
        output = SHELL_ACCESO.recv(65535).decode('ascii')
            
        lineas = output.splitlines()

        for linea in lineas:

            # Detectar prompts Cisco
            if "#" in linea:
                print(
                    f"\n\n{Fore.YELLOW}{Style.BRIGHT}"
                    f"{linea}"
                    f"{Style.RESET_ALL}", end = ""
                )

            else:
                print(linea)
                
        for comando in comandos:
            SHELL_ACCESO.send(f'{comando}\n')
            time.sleep(0.4)
            output = SHELL_ACCESO.recv(65535).decode('ascii')
            
            lineas = output.splitlines()

            for linea in lineas:

                # Detectar prompts Cisco
                if "#" in linea:
                    print(
                        f"\n\n{Fore.YELLOW}{Style.BRIGHT}"
                        f"{linea}"
                        f"{Style.RESET_ALL}", end = ""
                    )

                else:
                    print(linea)

            #print(output.decode('ascii'), end="") 

        print("\n\n")

    except Exception as e:
        print(f"Error al ejecutar el comando '{comando}': {e}")
        return None

def ssh_exec_multiple(comandos):
    try:
        for hostname, comando_key in comandos.items():
            device_obj = device(hostname, "admin", "admin")
            ssh_client = conexion_ssh(device_obj)
            if ssh_client:
                ssh_exec(ssh_client, COMANDOS[comando_key])
                ssh_client.close()

    except Exception as e:
        print(f"Error al ejecutar comandos en múltiples dispositivos: {e}")

def ssh_exec_multiple_validar(comandos):
    try:
        for hostname, comando_key in comandos.items():
            device_obj = device(hostname, "admin", "admin")
            ssh_client = conexion_ssh(device_obj)
            if ssh_client:
                ssh_exec(ssh_client, COMANDOS_SUP[comando_key])
                ssh_client.close()

    except Exception as e:
        print(f"Error al ejecutar comandos en múltiples dispositivos: {e}")


def ssh_exec_multiple_json(hostname_comando):
    with open("configs/comandos_generados.json", "r") as f:
        comandos_a_ejecutar = json.load(f)

    try:
        for hostname, comando_key in hostname_comando.items():
            device_obj = device(hostname, "admin", "admin")
            ssh_client = conexion_ssh(device_obj)
            if ssh_client:
                ssh_exec(ssh_client, comandos_a_ejecutar[comando_key])
                ssh_client.close()

    except Exception as e:
        print(f"Error al ejecutar comandos en múltiples dispositivos: {e}")
