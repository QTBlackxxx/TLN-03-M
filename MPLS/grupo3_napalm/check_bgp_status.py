from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

def extract_bgp_status(device) -> dict:
    try:
        bgp_data    = device.get_bgp_neighbors()
        total_peers = 0
        up_peers    = 0

        for vrf_data in bgp_data.values():
            peers        = vrf_data.get("peers", {})
            total_peers += len(peers)
            up_peers    += sum(1 for p in peers.values() if p.get("is_up"))

        if total_peers == 0:
            return {"bgp_status": " Sin vecinos"}
        if up_peers == total_peers:
            return {"bgp_status": f" Established ({up_peers}/{total_peers})"}
        return {"bgp_status": f" Down ({total_peers - up_peers}/{total_peers} caídos)"}

    except Exception as e:
        return {"bgp_status": f" Error: {str(e)[:30]}"}

def run_audit():
    results = []
    for name, info in INVENTORY.items():

        if info["type"] == "switch_l2":   # ← único filtro
            continue

        print(f"📡 [BGP] {name} ({info['ip']})...")
        if not wait_for_ssh(info["ip"]):
            print(f"    SSH Timeout")
            results.append({"device": name, "bgp_status": " SSH Timeout"})
            continue
        try:
            with napalm_session(name, info) as device:
                data = extract_bgp_status(device)
                data["device"] = name
                results.append(data)
            print(f"   {data['bgp_status']}")
        except Exception as e:
            print(f"    {name}: {str(e)[:50]}")
            results.append({"device": name, "bgp_status": " Error"})
    return results

if __name__ == "__main__":
    print("\n  AUDITORÍA BGP STATUS — solo routers\n")
    data = run_audit()
    headers = {"device": "Dispositivo", "bgp_status": "BGP Status"}
    print(tabulate(data, headers=headers, tablefmt="fancy_grid", showindex=False))