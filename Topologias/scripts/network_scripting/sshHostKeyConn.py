import paramiko
import time
from getpass import getpass

class device(object):
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
    
    def set_password(self):
        self.password = getpass(prompt=f"Ingresar contraseña para: {self.username}@{self.hostname}: ")

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

        print("Conexión exitosa a", device.hostname)

        return ssh_client

    except Exception as e:
        print(f"Error al conectar a {device.hostname}: {e}")
        return None

def ssh_exec(ssh_client, comandos):
    try:
        SHELL_ACCESO = ssh_client.invoke_shell()
        SHELL_ACCESO.send("terminal length 0\n")
        for comando in comandos:
            SHELL_ACCESO.send(f'{comando}\n')
            time.sleep(1)
            output = SHELL_ACCESO.recv(65535)
            print(output.decode('ascii')) 

    except Exception as e:
        print(f"Error al ejecutar el comando '{comando}': {e}")
        return None