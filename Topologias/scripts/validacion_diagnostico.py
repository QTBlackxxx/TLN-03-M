from network_scripting import sshHostKeyConn
from getpass import getpass
from configs import funcion_comandos
import paramiko
import time
from configs.comandos import COMANDOS

hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "CPE-HQ",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "CPE-HQ-BK"
}

sshHostKeyConn.ssh_exec_multiple(hostname_comando)






