from network_scripting import sshHostKeyConn
from getpass import getpass
from configs import funcion_comandos
import paramiko
import time
from configs.comandos import COMANDOS



hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "CPE-HQ",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "CPE-HQ-BK",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH": "CPE-BRANCH",
    #"clab-ISP-TDP-CLARO-IOL-CPE-BRANCH-BK": "CPE-BRANCH-BK",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2": "CPE-BRANCH2",
    #"clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK": "CPE-BRANCH2-BK",
    "clab-ISP-TDP-CLARO-IOL-M3": "M3",
    #"clab-ISP-TDP-CLARO-IOL-C5": "C5",
    "clab-ISP-TDP-CLARO-IOL-SW2-R-PISO1": "SW2-R-PISO1"
    #
}

sshHostKeyConn.ssh_exec_multiple(hostname_comando)

#funcion_comandos.config_hub("comando_1", "CPE-HQ", funcion_comandos.GLOBAL_DMVPN, funcion_comandos.HUB_PARAMS)
#funcion_comandos.config_hub("comando_2", "CPE-HQ-BK", funcion_comandos.GLOBAL_DMVPN, funcion_comandos.HUB_PARAMS)
#funcion_comandos.config_spoke("comando_3", "CPE-BRANCH2", funcion_comandos.GLOBAL_DMVPN, funcion_comandos.SPOKE_PARAMS)
#funcion_comandos.config_spoke("comando_4", "CPE-BRANCH2-BK", funcion_comandos.GLOBAL_DMVPN, funcion_comandos.SPOKE_PARAMS)

"""hostname_comando_funciones = {
    #"clab-ISP-TDP-CLARO-IOL-CPE-HQ": "comando_1",
    #"clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "comando_2",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2": "comando_3",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK": "comando_4"
}
"""
#sshHostKeyConn.ssh_exec_multiple_json(hostname_comando_funciones)



#Creación del objeto del dispositivo con la clase device
#R1 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-M4", "admin", "admin")

#Establecer conexión SSH con el dispositivo utilizando la función conexion_ssh
#ssh_client = sshHostKeyConn.conexion_ssh(R1)

#Ejecutar comandos en el dispositivo utilizando la función ssh_exec
#sshHostKeyConn.ssh_exec(ssh_client, COMANDOS["R1"])


