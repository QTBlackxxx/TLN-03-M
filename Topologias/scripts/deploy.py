#!/usr/bin/python3
import paramiko
import time
import sys
import logging
from commands_hq      import DEVICES as HQ_DEVICES,  CONFIG_MAP as HQ_MAP
from commands_branch2 import DEVICES as B2_DEVICES,  CONFIG_MAP as B2_MAP

logging.basicConfig(level=logging.INFO, format='%(message)s')

# ==========================================
# 1. COMANDOS DE INICIALIZACIÓN DE TERMINAL
# ==========================================
init_cmds = [
    "terminal width 0",
    "terminal length 0",
]

# ==========================================
# 2. CONSTRUCCIÓN DE DEVICES Y CONFIG_MAP
# ==========================================
DEVICES    = HQ_DEVICES + B2_DEVICES
CONFIG_MAP = {**HQ_MAP,  **B2_MAP}

ALL_DEVICES = [
    {
        "host":     d["host"],
        "hostname": d["hostname"],
        "user":     d["username"],
        "password": d["password"],
        "config":   ["conf t"] + CONFIG_MAP[d["hostname"]] + ["end", "write memory"],
    }
    for d in DEVICES
]

# ==========================================
# 3. FUNCIONES CORE
# ==========================================
def send_command_and_wait(channel, command, prompt="#", timeout=30):
    while channel.recv_ready():
        leftover = channel.recv(65535).decode('ascii', errors='ignore')
        sys.stdout.write(leftover)
        sys.stdout.flush()

    channel.send(command + "\n")

    output_buffer = ""
    start_time = time.time()

    while True:
        if channel.recv_ready():
            chunk = channel.recv(65535).decode('ascii', errors='ignore')
            sys.stdout.write(chunk)
            sys.stdout.flush()
            output_buffer += chunk

            stripped = output_buffer.rstrip()
            if stripped.endswith(prompt):
                return output_buffer

        if time.time() - start_time > timeout:
            logging.warning(f"[TIMEOUT] Esperando prompt tras: {command}")
            return output_buffer

        time.sleep(0.1)


def configure_device(device_info):
    print(f"\n{'='*60}")
    print(f"  Conectando a: {device_info['host']} ({device_info['hostname']})")
    print(f"{'='*60}")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(
            hostname=device_info['host'],
            username=device_info['user'],
            password=device_info['password'],
            look_for_keys=False
        )

        channel = ssh_client.invoke_shell()
        time.sleep(1)
        channel.recv(65535)

        for cmd in init_cmds:
            send_command_and_wait(channel, cmd)

        for cmd in device_info['config']:
            send_command_and_wait(channel, cmd)

        print(f"\n[OK] Configuracion completada en {device_info['hostname']}")

    except Exception as e:
        print(f"\n[ERROR] Fallo en {device_info['hostname']}: {str(e)}")
    finally:
        ssh_client.close()


# ==========================================
# 4. MAIN
# ==========================================
if __name__ == "__main__":
    for device in ALL_DEVICES:
        configure_device(device)
