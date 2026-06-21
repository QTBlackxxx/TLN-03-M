from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

BGP_NODES = {"P1", "P2", "PE1", "PE2", "RR1", "RR2"}   # CPE-1/2 no tienen BGP

def extract_bgp(device) -> list:
    rows = []
    for vrf, vrf_data in device.get_bgp_neighbors().items():
        peers = vrf_data.get("peers", {})
        if not peers:          # ← skip VRFs vacías
            continue
        for peer_ip, peer_data in peers.items():
            rx = sum(
                af.get("received_prefixes", 0) or 0
                for af in peer_data.get("address_family", {}).values()
            )
            rows.append({
                "vrf":        vrf,
                "peer_ip":    peer_ip,
                "remote_as":  peer_data.get("remote_as", "-"),
                "is_up":      "UP" if peer_data.get("is_up") else "DOWN",
                "rx_prefixes": rx,
            })
    return rows

def run_audit():
    results = []
    for name, info in INVENTORY.items():
        if info["type"] == "switch_l2":
            continue

        print(f" [BGP] {name} ({info['ip']})...")
        if not wait_for_ssh(info["ip"]):
            print(f"   SSH Timeout"); continue

        try:
            with napalm_session(name, info) as device:
                rows = extract_bgp(device)

            if not rows:
                label = "esperado" if name not in BGP_NODES else "⚠️  INESPERADO"
                print(f"   Sin peers BGP ({label})")
                results.append({
                    "device": name, "vrf": "—", "peer_ip": "—",
                    "remote_as": "—", "is_up": f"sin BGP ({label})",
                    "rx_prefixes": "—",
                })
            else:
                for row in rows: row["device"] = name
                results.extend(rows)
                print(f"   OK — {len(rows)} peers")

        except Exception as e:
            print(f"   {name}: {str(e)[:50]}")

    return results

if __name__ == "__main__":
    print("\n AUDITORÍA BGP — todos los routers\n")
    data = run_audit()
    headers = {"device": "Dispositivo", "vrf": "VRF", "peer_ip": "Peer IP",
               "remote_as": "Remote AS", "is_up": "Estado", "rx_prefixes": "Prefixes RX"}
    print(tabulate(data, headers=headers, tablefmt="fancy_grid", showindex=False))