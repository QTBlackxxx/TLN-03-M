import paramiko

DEVICES = [
    {"host": "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2",    "hostname": "CPE-BRANCH2",    "username": "admin", "password": "admin"},
    {"host": "clab-ISP-TDP-CLARO-IOL-CPE-BRANCH2-BK", "hostname": "CPE-BRANCH2-BK", "username": "admin", "password": "admin"},
    {"host": "clab-ISP-TDP-CLARO-IOL-CPE-HQ",         "hostname": "CPE-HQ",         "username": "admin", "password": "admin"},
]

DMVPN_COMMANDS = [
    "show dmvpn",
    "show ip nhrp",
    "show ip nhrp detail",
    "show interface Tunnel1",
    "show interface Tunnel2",
]

VRRP_COMMANDS = [
    "show vrrp",
    "show vrrp brief",
]

EIGRP_COMMANDS = [
    "show ip eigrp neighbors",
    "show ip route eigrp",
    "show ip eigrp topology",
]

VERIFY_MAP = {
    "CPE-BRANCH2":    DMVPN_COMMANDS + VRRP_COMMANDS + EIGRP_COMMANDS,
    "CPE-BRANCH2-BK": DMVPN_COMMANDS + VRRP_COMMANDS + EIGRP_COMMANDS,
    "CPE-HQ":         DMVPN_COMMANDS + EIGRP_COMMANDS,
}


def run_command(device, command):
    print(f"\n  #### Ejecutando comando: {command} ####\n")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            device["host"],
            username=device["username"],
            password=device["password"],
            look_for_keys=False,
            timeout=10,
        )
        _, stdout, stderr = client.exec_command(command, timeout=10)
        output = stdout.read().decode("utf-8", errors="replace")
        error  = stderr.read().decode("utf-8", errors="replace")
        client.close()
        result = output if output else error
        return result.strip()
    except paramiko.AuthenticationException:
        return "Error: credenciales incorrectas."
    except paramiko.SSHException as e:
        return f"Error SSH: {e}"
    except Exception:
        return "No es posible conectarse al dispositivo."


def verify(devices):
    for device in devices:
        print(f"\n{'═'*55}")
        print(f"Hostname : {device['hostname']}")
        print(f"{'═'*55}")
        if device["hostname"] in VERIFY_MAP:
            commands = VERIFY_MAP[device["hostname"]]
        else:
            commands = DMVPN_COMMANDS + EIGRP_COMMANDS
        for cmd in commands:
            print(run_command(device, cmd))


if __name__ == "__main__":
    verify(DEVICES)
