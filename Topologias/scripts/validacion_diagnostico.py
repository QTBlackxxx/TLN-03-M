from network_scripting import sshHostKeyConn
from getpass import getpass
from configs import funcion_comandos
import paramiko
import time
from configs.comandos import COMANDOS

hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "script_moises",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "script_moises_c2",
}

sshHostKeyConn.ssh_exec_multiple_validar(hostname_comando)






