from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

def extract_interfaces_ip(device) -> list:
    rows = []
    for intf, families in device.get_interfaces_ip().items():
        ipv4 = [f"{ip}/{d.get('prefix_length', '32')}" for ip, d in families.get("ipv4", {}).items()]
        ipv6 = [f"{ip}/{d.get('prefix_length', '128')}" for ip, d in families.get("ipv6", {}).items()]
        rows.append({
            "interface": intf,
            "ipv4": ", ".join(ipv4) if ipv4 else "-",
            "ipv6": ", ".join(ipv6) if ipv6 else "-"
        })
    return rows

def run_audit():
    results = []
    for name, info in INVENTORY.items():
        print(f"[IP] {name}...")
        if not wait_for_ssh(info['ip']): continue
        try:
            with napalm_session(name, info) as device:
                rows = extract_interfaces_ip(device)
                for row in rows: row["device"] = name
                results.extend(rows)
            print(f"  OK - {len(rows)} interfaces")
        except Exception as e:
            print(f"   {name}: {str(e)[:40]}")
    return results

if __name__ == "__main__":
    print("\n INICIANDO DIRECCIONAMIENTO IP \n")
    data = run_audit()
    headers_map = {"device": "Dispositivo", "interface": "Interfaz", "ipv4": "Direcciones IPv4", "ipv6": "Direcciones IPv6"}
    print(tabulate(data, headers=headers_map, tablefmt="fancy_grid", showindex=False))