from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

SKIP_VRFS = {"default", "clab-mgmt"}

def get_vrf_routes_v6(device, vrf_name) -> int:
    """Cuenta rutas IPv6 en una VRF específica via CLI directo."""
    try:
        out  = device.cli([f"show ipv6 route vrf {vrf_name}"])
        text = out.get(f"show ipv6 route vrf {vrf_name}", "")
        count = 0
        for line in text.splitlines():
            stripped = line.strip()
            # Códigos IOS para IPv6: C, L, S, B, O, R, i, ND
            if stripped and stripped[0] in "BCOSRILE*DS" and "/" in line:
                count += 1
        return count
    except Exception:
        return -1

def extract_ipv6_vpn(device, device_type) -> dict:
    if device_type == "switch_l2":
        return {"ipv6_vpn": "N/A (L2)", "vrfs": "—", "detalle": "—"}

    try:
        instances = device.get_network_instances()

        # ── mismo fix que IPv4: no filtrar por type=='L3VRF' ─────────────────
        vrfs = [
            n for n, d in instances.items()
            if n not in SKIP_VRFS
            and d.get("type", "") != "DEFAULT_INSTANCE"
        ]

        if not vrfs:
            return {"ipv6_vpn": "N/A (sin VRFs)", "vrfs": "—", "detalle": "—"}

        # ── comando por VRF en lugar de get_route_to('::/0', vrf=) ───────────
        detalle_parts = []
        total_rutas   = 0
        for vrf in vrfs:
            n = get_vrf_routes_v6(device, vrf)
            if n == -1:
                detalle_parts.append(f"{vrf}:ERR")
            else:
                detalle_parts.append(f"{vrf}:{n} rutas")
                total_rutas += n

        estado = " OK" if total_rutas > 0 else " VRFs sin rutas IPv6"
        return {
            "ipv6_vpn": estado,
            "vrfs":     ", ".join(vrfs),
            "detalle":  " | ".join(detalle_parts),
        }

    except Exception as e:
        return {"ipv6_vpn": " Error", "vrfs": str(e)[:40], "detalle": "—"}


def run_audit():
    results = []
    for name, info in INVENTORY.items():
        if info["type"] == "switch_l2":
            continue
        print(f"📡 [IPv6 VPN] {name} ({info['ip']})...")
        if not wait_for_ssh(info["ip"]):
            print(f"    SSH Timeout")
            results.append({"device": name, "ipv6_vpn": " SSH Timeout",
                            "vrfs": "—", "detalle": "—"})
            continue
        try:
            with napalm_session(name, info) as device:
                data = extract_ipv6_vpn(device, info["type"])
                data["device"] = name
                results.append(data)
            print(f"   {data['ipv6_vpn']}  →  {data['detalle']}")
        except Exception as e:
            print(f"    {name}: {str(e)[:50]}")
            results.append({"device": name, "ipv6_vpn": " Error",
                            "vrfs": str(e)[:30], "detalle": "—"})
    return results


if __name__ == "__main__":
    print("\n VERIFICACION IPv6 VPN — VRF STATUS\n")
    data = run_audit()
    headers = {
        "device":   "Dispositivo",
        "ipv6_vpn": "Estado VPN",
        "vrfs":     "VRFs detectadas",
        "detalle":  "Rutas IPv6 por VRF",
    }
    print(tabulate(data, headers=headers, tablefmt="fancy_grid", showindex=False))