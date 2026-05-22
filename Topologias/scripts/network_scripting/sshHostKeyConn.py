import paramiko
from getpass import getpass

class device(object):
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
    
    def set_password(self):
        self.password = getpass(prompt=f"Ingresar contraseña para: {self.username}@{self.hostname}: ")

def conexion_ssh(device):
    comandos = [
        "show version",
        "show ip interface brief",
        "show running-config"]

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=device.hostname, 
            username=device.username, 
            password=device.password
        )

        for comando in comandos:
            stdin, stdout, stderr = ssh_client.exec_command(comando)
            time.sleep(1)  # Esperar un momento para que el comando se ejecute
            print(f"Salida de '{comando}' en {device.hostname}:\n{stdout.read().decode()}")

        return ssh_client
        
    except Exception as e:
        print(f"Error al conectar a {device.hostname}: {e}")
        return None