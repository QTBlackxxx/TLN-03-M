from network_scripting import sshHostKeyConn
from getpass import getpass
import paramiko
import time
from configs.comandos import COMANDOS

#Creación del objeto del dispositivo con la clase device
#R1 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-M4", "admin", "admin")

#Establecer conexión SSH con el dispositivo utilizando la función conexion_ssh
#ssh_client = sshHostKeyConn.conexion_ssh(R1)

#Ejecutar comandos en el dispositivo utilizando la función ssh_exec
#sshHostKeyConn.ssh_exec(ssh_client, COMANDOS["R1"])

CPE_HQ = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-CPE-HQ", "admin", "admin")
ssh_client_cpe_hq = sshHostKeyConn.conexion_ssh(CPE_HQ)
sshHostKeyConn.ssh_exec(ssh_client_cpe_hq, COMANDOS["CPE_HQ"])
ssh_client_cpe_hq.close()

CPE_HQ_BK = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK", "admin", "admin")
ssh_client_cpe_hq_bk = sshHostKeyConn.conexion_ssh(CPE_HQ_BK)
sshHostKeyConn.ssh_exec(ssh_client_cpe_hq_bk, COMANDOS["CPE_HQ_BK"])
ssh_client_cpe_hq_bk.close()

CPE_BRANCH = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-CPE-BRANCH", "admin", "admin")
ssh_client_cpe_branch = sshHostKeyConn.conexion_ssh(CPE_BRANCH)
sshHostKeyConn.ssh_exec(ssh_client_cpe_branch, COMANDOS["CPE_BRANCH"])
ssh_client_cpe_branch.close()

CPE_BRANCH_BK = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-CPE-BRANCH-BK", "admin", "admin")
ssh_client_cpe_branch_bk = sshHostKeyConn.conexion_ssh(CPE_BRANCH_BK)
sshHostKeyConn.ssh_exec(ssh_client_cpe_branch_bk, COMANDOS["CPE_BRANCH_BK"])
ssh_client_cpe_branch_bk.close()

CPE_BRANCH2 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2", "admin", "admin")
ssh_client_cpe_branch2 = sshHostKeyConn.conexion_ssh(CPE_BRANCH2)
sshHostKeyConn.ssh_exec(ssh_client_cpe_branch2, COMANDOS["CPE_BRANCH2"])
ssh_client_cpe_branch2.close()

CPE_BRANCH2_BK = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK", "admin", "admin")
ssh_client_cpe_branch2_bk = sshHostKeyConn.conexion_ssh(CPE_BRANCH2_BK)
sshHostKeyConn.ssh_exec(ssh_client_cpe_branch2_bk, COMANDOS["CPE_BRANCH2_BK"])
ssh_client_cpe_branch2_bk.close()

C2 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-C2", "admin", "admin")
ssh_client_c2 = sshHostKeyConn.conexion_ssh(C2)
sshHostKeyConn.ssh_exec(ssh_client_c2, COMANDOS["C2"])
ssh_client_c2.close()

M2 = sshHostKeyConn.device("clab-ISP-TDP-CLARO-IOL-M2", "admin", "admin")
ssh_client_m2 = sshHostKeyConn.conexion_ssh(M2)
sshHostKeyConn.ssh_exec(ssh_client_m2, COMANDOS["M2"])
ssh_client_m2.close()





if ssh_client is not None:
    ssh_client.close()