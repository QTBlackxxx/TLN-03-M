from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

# Destinos específicos por nodo según su rol en la topología
DESTINATIONS = {
    "P1":    ["172.16.1.1","172.16.1.2","172.16.1.5","172.16.1.6"],
    "P2":    ["172.16.1.1","172.16.1.2","172.16.1.5","172.16.1.6"],
    "PE1":   ["172.16.1.2","172.16.1.3","172.16.1.5","172.16.1.6",
               "192.168.10.0/24","192.168.20.0/24"],
    "PE2":   ["172.16.1.1","172.16.1.3","172.16.1.5","172.16.1.6",
               "192.168.10.0/24","192.168.20.0/24"],
    "RR1":   ["172.16.1.1","172.16.1.2","172.16.1.3","172.16.1.4"],
    "RR2":   ["172.16.1.1","172.16.1.2","172.16.1.3","172.16.1.4"],
    "CPE-1": ["0.0.0.0/0","10.0.1.1","192.168.10.0/24"],
    "CPE-2": ["0.0.0.0/0","10.0.3.1","192.168.20.0/24"],
}

# Protocolos válidos por nodo — cualquier otro es 
PROTO_ESPERADO = {
    "P1":    ["ospf"],
    "P2":    ["ospf"],
    "RR1":   ["ospf"],
    "RR2":   ["ospf"],
    "PE1":   ["ospf","bgp"],
    "PE2":   ["ospf","bgp"],
    "CPE-1": ["static","bgp","connected"],
    "CPE-2": ["static","bgp","connected"],
}

def audit_routes(device, name) -> list:
    rows, seen = [], set()
    for dest in DESTINATIONS.get(name, []):
        try:
            for prefix, paths in device.get_route_to(destination=dest).items():
                for path in paths:
                    key = (prefix, path.get("next_hop"), path.get("protocol"))
                    if key in seen: continue
                    seen.add(key)
                    proto = path.get("protocol","N/A").lower()
                    esperados = PROTO_ESPERADO.get(name, [])
                    estado = "OK" if proto in esperados else f" {proto.upper()}"
                    rows.append({
                        "device":   name,
                        "destino":  prefix,
                        "proto":    proto.upper(),
                        "next_hop": path.get("next_hop","N/A"),
                        "interfaz": path.get("outgoing_interface","N/A"),
                        "estado":   estado,
                    })
        except Exception:
            continue
    return rows

def run_audit():
    results = []
    for name, info in INVENTORY.items():
        if info["type"] == "switch_l2" or name not in DESTINATIONS:
            continue
        print(f"📡 {name} ({info['ip']}) — {len(DESTINATIONS[name])} destinos...")
        if not wait_for_ssh(info["ip"]):
            print(f"    SSH Timeout"); continue
        try:
            with napalm_session(name, info) as device:
                rows = audit_routes(device, name)
                results.extend(rows)
                ok   = sum(1 for r in rows if "OK" in r["estado"])
                warn = sum(1 for r in rows if "" in r["estado"])
                print(f"    {ok} OK    {warn} protocolo inesperado")
        except Exception as e:
            print(f"    {str(e)[:50]}")
    return results

if __name__ == "__main__":
    print("\n  VERIFICACION get_route_to() — MPLS OSPF+BGP\n")
    data = run_audit()
    headers = {"device":"Nodo","destino":"Destino","proto":"Protocolo",
               "next_hop":"Next Hop","interfaz":"Interfaz","estado":"Estado"}
    print(tabulate(data, headers=headers, tablefmt="fancy_grid", showindex=False))