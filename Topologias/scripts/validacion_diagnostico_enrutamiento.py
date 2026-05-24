
from network_scripting import sshHostKeyConn
from getpass import getpass
import paramiko
import time
from configs.comandos_validacion_enrutamiento import COMANDOS_SUP
###########################################################

# =============================================================================
hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "CPE-HQ",
    "clab-ISP-TDP-CLARO-IOL-M3": "M3",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2": "CPE-BRANCH2",
    
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH": "CPE-BRANCH",
    "clab-ISP-TDP-CLARO-IOL-C5": "C5",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK": "CPE-BRANCH2-BK",    
    
    "clab-ISP-TDP-CLARO-IOL-SW2-R-PISO1": "SW2-R-PISO1",
}

# =============================================================================
for hostname_clab, clave in hostname_comando.items():

    device_obj = sshHostKeyConn.device(hostname_clab, "admin", "admin")

    print(f"\n{'='*70}\n  DISPOSITIVO: {clave}\n{'='*70}")

    # PRIMERA PARTE — un exec_command por comando, reconectando cada vez
    for comando in COMANDOS_SUP[clave]:
        try:
            # CONEXIÓN SSH usando función de sshHostKeyConn
            ssh_client = sshHostKeyConn.conexion_ssh(device_obj)
            if ssh_client is None:
                continue

            # VERIFICACIÓN con exec_command
            stdin, stdout, stderr = ssh_client.exec_command(comando, timeout=10)
            output = stdout.read().decode("ascii", errors="replace").strip()
            print(f"\n  >> {comando}")
            print(output if output else "  [Sin output recibido]")
            ssh_client.close()
            time.sleep(0.3)

        except Exception as e:
            print(f"\n  >> {comando}")
            print(f"  [EXCEPCIÓN] {e}")