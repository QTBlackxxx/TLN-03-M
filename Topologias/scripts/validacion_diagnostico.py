# Parte 4 - Validación y Diagnóstico de Túneles DMVPN

#### NO TOCAR
from network_scripting import sshHostKeyConn
from getpass import getpass
import paramiko
import time
from configs.comandos_validacion import COMANDOS_VALIDACION
###########################################################

from colorama import Fore, Style, init

init(autoreset=True)

# FUNCIÓN exec_command abre un canal independiente por cada comando, ideal para
# comandos de solo lectura (show) donde se necesita output limpio y completo.
def ssh_exec_command(device_obj, comandos):
    """
    NOTA TÉCNICA: Cisco IOL cierra el canal SSH después de cada exec_command,
    por lo que no es posible reusar la misma conexión entre comandos.
    Solución: se abre una conexión SSH nueva e independiente por cada comando,
    garantizando que exec_command opere sobre un canal limpio cada vez.
    """
    resultados = []

    for comando in comandos:
        try:
            # Nueva conexión SSH por cada comando 
            cliente_temp = paramiko.SSHClient()
            cliente_temp.load_system_host_keys()
            cliente_temp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cliente_temp.connect(
                hostname=device_obj.hostname,
                username=device_obj.username,
                password=device_obj.password,
                look_for_keys=False
            )

            stdin, stdout, stderr = cliente_temp.exec_command(comando, timeout=10)
            output = stdout.read().decode("ascii", errors="replace").strip()
            error  = stderr.read().decode("ascii", errors="replace").strip()
            resultados.append((comando, output, error))
            cliente_temp.close()
            time.sleep(0.3)

        except Exception as e:
            resultados.append((comando, "", f"[EXCEPCIÓN] {e}"))

    return resultados

# FUNCIÓN DE IMPRESIÓN 
def imprimir_resultado(hostname, resultados):
    """
    Imprime en consola con colores los resultados de validación.
    """
    separador = "=" * 70
    encabezado = f"\n{separador}\n  DISPOSITIVO: {hostname}\n{separador}"

    print(f"\n{Fore.CYAN}{Style.BRIGHT}{encabezado}{Style.RESET_ALL}")

    for comando, output, error in resultados:
        # Encabezado del comando 
        linea_cmd = f"\n  >> {comando}"
        print(f"{Fore.YELLOW}{Style.BRIGHT}{linea_cmd}{Style.RESET_ALL}")

        # Output normal 
        if output:
            print(output)

        # Errores o advertencias
        if error:
            print(f"{Fore.RED}  [STDERR] {error}{Style.RESET_ALL}")

        # Sin output ni error
        if not output and not error:
            print(f"{Fore.MAGENTA}  [Sin output recibido]{Style.RESET_ALL}")

# MAPA DE DISPOSITIVOS
# hostname containerlab  ->  clave en COMANDOS_VALIDACION
DISPOSITIVOS = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ":        "CPE-HQ",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK":     "CPE-HQ-BK",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2":   "CPE-BRANCH2",
    "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK":"CPE-BRANCH2-BK",
}

USUARIO   = "admin"
PASSWORD  = "admin"

# MAIN — recorre los 4 dispositivos y ejecuta la validación
def main():
    encabezado = (
        f"REPORTE DE VALIDACIÓN DMVPN\n"
        f"Topología: ISP-TDP-CLARO-IOL\n"
        + "=" * 70
    )
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{encabezado}{Style.RESET_ALL}")

    for hostname_clab, clave in DISPOSITIVOS.items():

        # PRIMERA PARTE — CONEXIÓN SSH
        dispositivo = sshHostKeyConn.device(hostname_clab, USUARIO, PASSWORD)
        ssh_client  = sshHostKeyConn.conexion_ssh(dispositivo)

        if ssh_client is None:
            print(f"{Fore.RED}\n[ERROR] No se pudo conectar a {hostname_clab}. Se omite.\n{Style.RESET_ALL}")
            continue

        # SEGUNDA PARTE — EJECUCIÓN DE COMANDOS con exec_command
        comandos = COMANDOS_VALIDACION[clave]
        resultados = ssh_exec_command(dispositivo, comandos)

        # Imprime en consola
        imprimir_resultado(clave, resultados)

        ssh_client.close()

if __name__ == "__main__":
    main()