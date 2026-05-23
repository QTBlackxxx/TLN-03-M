from network_scripting import sshHostKeyConn ###
from getpass import getpass
from configs import funcion_comandos
import paramiko
import time
from configs.comandos_validacion_enrutamiento import COMANDOS_SUP ###

hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-M1": "M1",
}

sshHostKeyConn.ssh_exec_multiple_validar(hostname_comando)






