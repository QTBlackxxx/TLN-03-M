from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

def extract_facts(device) -> dict:
    """Core testeable: Extrae identidad y ciclo de vida."""
    facts = device.get_facts()
    return {
        "hostname": facts.get("hostname", "N/A"),
        "os_version": facts.get("os_version", "N/A"),
        "serial_number": facts.get("serial_number", "N/A"),
        "uptime": f"{facts.get('uptime', 0)}s"
    }

def run_audit():
    results = []
    for name, info in INVENTORY.items():
        print(f" [FACTS] {name} ({info['ip']})...")
        if not wait_for_ssh(info['ip']):
            results.append({"device": name, "hostname": "ERROR", "os_version": "SSH Timeout", "serial_number": "-", "uptime": "-"})
            continue
        try:
            with napalm_session(name, info) as device:
                data = extract_facts(device)
                data["device"] = name
                results.append(data)
            print(f" OK")
        except Exception as e:
            err_msg = str(e)[:60]
            print(f" {name} ({type(e).__name__}): {err_msg}")
            results.append({"device": name, "hostname": "ERROR", "os_version": err_msg, "serial_number": "-", "uptime": "-"})
    return results

if __name__ == "__main__":
    print("\n INICIANDO FACTS \n")
    data = run_audit()
    headers_map = {
        "device": "Dispositivo", "hostname": "Hostname", "os_version": "Versión OS",
        "serial_number": "N° Serie", "uptime": "Uptime"
    }
    print(tabulate(data, headers=headers_map, tablefmt="fancy_grid", showindex=False))