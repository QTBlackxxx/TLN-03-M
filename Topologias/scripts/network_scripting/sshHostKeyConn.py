import paramiko
import time
from getpass import getpass
from colorama import Fore, Style, init
from configs.comandos import COMANDOS

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

        return ssh_client

    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}Error al conectar a {device.hostname}: {e}{Style.RESET_ALL}")
        return None

def ssh_exec(ssh_client, comandos):
    try:
        SHELL_ACCESO = ssh_client.invoke_shell()
        SHELL_ACCESO.send("terminal length 0\n")
        
        for comando in comandos:
            SHELL_ACCESO.send(f'{comando}\n')
            time.sleep(0.5)
            output = SHELL_ACCESO.recv(65535)
            print(output.decode('ascii'), end="") 

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