from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

def extract_interfaces(device) -> list:
    rows = []
    for intf, data in device.get_interfaces().items():
        rows.append({
            "interface":   intf,
            "is_enabled":  "UP"   if data.get("is_enabled") else "DOWN",
            "is_up":       "UP"   if data.get("is_up")      else "DOWN",
            "description": (data.get("description") or "")[:25],
            "speed_mbps":  data.get("speed", 0)
        })
    return rows

def run_audit():
    results = []
    for name, info in INVENTORY.items():

        if info["type"] == "switch_l2":   # ← único filtro
            continue

        print(f" [INTF] {name}...")
        if not wait_for_ssh(info["ip"]): continue
        try:
            with napalm_session(name, info) as device:
                rows = extract_interfaces(device)
                for row in rows: row["device"] = name
                results.extend(rows)
            print(f"  OK - {len(rows)} interfaces")
        except Exception as e:
            print(f"  {name}: {str(e)[:40]}")
    return results

if __name__ == "__main__":
    print("\n INICIANDO INTERFACES\n")
    data = run_audit()
    headers_map = {"device": "Dispositivo", "interface": "Interfaz", "is_enabled": "Admin",
                   "is_up": "Estado", "description": "Descripción", "speed_mbps": "Velocidad (Mbps)"}
    print(tabulate(data, headers=headers_map, tablefmt="fancy_grid", showindex=False))