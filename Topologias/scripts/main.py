from network_scripting import sshHostKeyConn
from getpass import getpass
from configs import funcion_comandos
import paramiko
import time
from configs.comandos import COMANDOS

#Creación del objeto del dispositivo con la clase device
#R1 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-M4", "admin", "admin")

#Establecer conexión SSH con el dispositivo utilizando la función conexion_ssh
#ssh_client = sshHostKeyConn.conexion_ssh(R1)

#Ejecutar comandos en el dispositivo utilizando la función ssh_exec
#sshHostKeyConn.ssh_exec(ssh_client, COMANDOS["R1"])

nombre_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "CPE-HQ",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "CPE-HQ-BK",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH": "CPE-BRANCH",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH-BK": "CPE-BRANCH-BK",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2": "CPE-BRANCH2",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK": "CPE-BRANCH2-BK",
    "clab-ISP-TDP-CLARO-IOL-C5": "C5",
    "clab-ISP-TDP-CLARO-IOL-M3": "M3"
}

config_CPE-HQ =funcion_comandos.config_hub("CPE-HQ", funcion_comandos.GLOBAL_DMVPN, funcion_comandos.HUB_PARAMS)
config_CPE-HQ_BK = funcion_comandos.config_hub("CPE-HQ-BK", funcion_comandos.GLOBAL_DMVPN, funcion_comandos.HUB_PARAMS)

strings_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "config_CPE-HQ"
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "config_CPE-HQ_BK"
}
sshHostKeyConn.ssh_exec_multiple(strings_comando)

sshHostKeyConn.ssh_exec_multiple(nombre_comando)




