from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

def extract_ospf_status(device) -> dict:
    try:
        out  = device.cli(["show ip ospf neighbor"])
        text = out.get("show ip ospf neighbor", "")

        total, full = 0, 0
        for line in text.splitlines():
            # Líneas de vecinos: empiezan con una IP
            parts = line.split()
            if not parts or not parts[0].replace(".", "").isdigit():
                continue
            total += 1
            if "FULL" in line.upper():
                full += 1

        if total == 0:
            return {"ospf_status": " Sin vecinos OSPF"}
        if full == total:
            return {"ospf_status": f" FULL ({full}/{total})"}
        return {"ospf_status": f" No-Full ({total - full}/{total} caídos)"}

    except Exception as e:
        return {"ospf_status": f" Error: {str(e)[:30]}"}

def run_audit():
    results = []
    for name, info in INVENTORY.items():

        if info["type"] == "switch_l2":   # ← único filtro
            continue

        print(f" [OSPF] {name} ({info['ip']})...")
        if not wait_for_ssh(info["ip"]):
            print(f"    SSH Timeout")
            results.append({"device": name, "ospf_status": " SSH Timeout"})
            continue
        try:
            with napalm_session(name, info) as device:
                data = extract_ospf_status(device)
                data["device"] = name
                results.append(data)
            print(f"   {data['ospf_status']}")
        except Exception as e:
            print(f"    {name}: {str(e)[:50]}")
            results.append({"device": name, "ospf_status": " Error"})
    return results

if __name__ == "__main__":
    print("\n VERIFICANDO OSPF STATUS — solo routers\n")
    data = run_audit()
    headers = {"device": "Dispositivo", "ospf_status": "OSPF Status"}
    print(tabulate(data, headers=headers, tablefmt="fancy_grid", showindex=False))