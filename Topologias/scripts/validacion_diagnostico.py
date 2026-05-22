####NO TOCAR

from network_scripting import sshHostKeyConn
from getpass import getpass
import paramiko
import time
from configs.comandos_validacion import COMANDOS_SUP
###########################################################


####PRIMERA PARTE - CONEXIÓN SSH
#Creación del objeto del dispositivo con la clase device
#device(hostname, username, password)
M4 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-M4", "admin", "admin")
#Establecer conexión SSH con el dispositivo utilizando la función conexion_ssh
ssh_client = sshHostKeyConn.conexion_ssh(M4)



####SEGUNDA PARTE - EJECUCIÓN DE COMANDOS
#Ejecutar comandos en el dispositivo utilizando la función ssh_exec
#sshHostKeyConn.ssh_exec(objeto_conexion, COMANDOS_SUP[nombre])
sshHostKeyConn.ssh_exec(ssh_client, COMANDOS_SUP["script_moises"])



#####################
C2 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-C2", "admin", "admin")
ssh_client_c2 = sshHostKeyConn.conexion_ssh(C2)
sshHostKeyConn.ssh_exec(ssh_client_c2, COMANDOS_SUP["script_moises"])

if ssh_client is not None:
    ssh_client.close()


