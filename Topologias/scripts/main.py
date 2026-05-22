from network_scripting import sshHostKeyConn
from getpass import getpass
import paramiko
import time
from configs.comandos import COMANDOS

#Creación del objeto del dispositivo con la clase device
R1 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-M4", "admin", "")
R1.set_password()


#Establecer conexión SSH con el dispositivo utilizando la función conexion_ssh
ssh_client = sshHostKeyConn.conexion_ssh(R1)

#Ejecutar comandos en el dispositivo utilizando la función ssh_exec
sshHostKeyConn.ssh_exec(ssh_client, COMANDOS["R1"])

if ssh_client is not None:
    ssh_client.close()