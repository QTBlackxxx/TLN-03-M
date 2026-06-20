import json

# =========================================================
# PARÁMETROS GLOBALES
# =========================================================

GLOBAL = {
    "isakmp_key": "TLN03",
    "transform_set": "TS-DMVPN",
    "transform_encryption": "esp-aes",
    "transform_hash": "esp-sha-hmac",
    "ipsec_profile": "PF-DMVPN",
    "nhrp_auth": "DMVPNKEY",
    "ospf_pid": 10,
    "ospf_hello": 5,
    "ospf_dead": 20,
    "ospf_network_type": "broadcast"
}

# =========================================================
# HUBS
# =========================================================

HUBS = {
    "CPE-HQ": {
        "old_key": "190.0.0.1",
        "old_profile": "PF-TO-BRANCH",
        "old_ts": "TS-TO-BRANCH",

        "tunnel_iface": "Tunnel1",
        "tunnel_ip": "172.16.10.1",
        "tunnel_mask": "255.255.255.0",

        "nhrp_network": 100,
        "tunnel_key": 100,

        "ospf_priority": 255,
        "ospf_cost": 10,

        "old_network": "172.16.10.0",
        "old_wc": "0.0.0.3",

        "new_network": "172.16.10.0",
        "new_wc": "0.0.0.255"
    },

    "CPE-HQ-BK": {
        "old_key": "200.0.1.1",
        "old_profile": "PF-TO-BRANCH",
        "old_ts": "TS-TO-BRANCH",

        "tunnel_iface": "Tunnel1",
        "tunnel_ip": "172.16.10.100",
        "tunnel_mask": "255.255.255.0",

        "nhrp_network": 100,
        "tunnel_key": 100,

        "ospf_priority": 254,
        "ospf_cost": 100,

        "old_network": "172.16.20.0",
        "old_wc": "0.0.0.3",

        "new_network": "172.16.10.0",
        "new_wc": "0.0.0.255"
    }
}

# =========================================================
# SPOKES BÁSICOS
# =========================================================

SPOKES = {
    "CPE-BRANCH": {
        "old_key": "200.0.0.1",
        "old_profile": "PF-TO-HQ",
        "old_ts": "TS-TO-HQ",

        "tunnel_iface": "Tunnel1",
        "tunnel_ip": "172.16.10.2",
        "tunnel_mask": "255.255.255.0",

        "nhrp_network": 100,
        "tunnel_key": 100,

        "ospf_priority": 0,
        "ospf_cost": 10,

        "old_network": "172.16.10.0",
        "old_wc": "0.0.0.3",

        "new_network": "172.16.10.0",
        "new_wc": "0.0.0.255",

        "nhs": [
            {
                "tunnel_ip": "172.16.10.1",
                "nbma": "200.0.0.1"
            },
            {
                "tunnel_ip": "172.16.10.100",
                "nbma": "190.0.1.1"
            }
        ]
    },

    "CPE-BRANCH-BK": {
        "old_key": "190.0.1.1",
        "old_profile": "PF-TO-HQ",
        "old_ts": "TS-TO-HQ",

        "tunnel_iface": "Tunnel1",
        "tunnel_ip": "172.16.10.3",
        "tunnel_mask": "255.255.255.0",

        "nhrp_network": 100,
        "tunnel_key": 100,

        "ospf_priority": 0,
        "ospf_cost": 10,

        "old_network": "172.16.20.0",
        "old_wc": "0.0.0.3",

        "new_network": "172.16.10.0",
        "new_wc": "0.0.0.255",

        "nhs": [
            {
                "tunnel_ip": "172.16.10.1",
                "nbma": "200.0.0.1"
            },
            {
                "tunnel_ip": "172.16.10.100",
                "nbma": "190.0.1.1"
            }
        ]
    }
}

# =========================================================
# FUNCIÓN HUB
# =========================================================

def generar_hub(nombre, g, h):

    comandos = [

        "conf terminal",

        f"no crypto isakmp key {g['isakmp_key']} address {h['old_key']}",
        f"no interface {h['tunnel_iface']}",
        f"no crypto ipsec profile {h['old_profile']}",
        f"no crypto ipsec transform-set {h['old_ts']}",

        f"crypto isakmp key {g['isakmp_key']} address 0.0.0.0",

        f"crypto ipsec transform-set {g['transform_set']} "
        f"{g['transform_encryption']} {g['transform_hash']}",

        "mode transport",
        "exit",

        f"crypto ipsec profile {g['ipsec_profile']}",
        f"set transform-set {g['transform_set']}",
        "exit",

        f"interface {h['tunnel_iface']}",
        f"ip address {h['tunnel_ip']} {h['tunnel_mask']}",
        "no ip redirects",

        f"ip nhrp network-id {h['nhrp_network']}",
        f"ip nhrp authentication {g['nhrp_auth']}",

        "ip nhrp map multicast dynamic",
        "ip nhrp redirect",

        "tunnel source Loopback0",
        "tunnel mode gre multipoint",

        f"tunnel protection ipsec profile {g['ipsec_profile']}",
        f"tunnel key {h['tunnel_key']}",

        f"ip ospf priority {h['ospf_priority']}",
        f"ip ospf cost {h['ospf_cost']}",

        f"ip ospf hello-interval {g['ospf_hello']}",
        f"ip ospf dead-interval {g['ospf_dead']}",
        f"ip ospf network {g['ospf_network_type']}",

        "exit",

        f"router ospf {g['ospf_pid']}",

        f"no network {h['old_network']} "
        f"{h['old_wc']} area 0",

        f"network {h['new_network']} "
        f"{h['new_wc']} area 0",

        "exit",
        "end"
    ]

    return comandos

# =========================================================
# FUNCIÓN SPOKE
# =========================================================

def generar_spoke(nombre, g, s):

    comandos = [

        "conf terminal",

        f"no crypto isakmp key {g['isakmp_key']} address {s['old_key']}",

        f"crypto isakmp key {g['isakmp_key']} address 0.0.0.0",

        f"no interface {s['tunnel_iface']}",

        f"no crypto ipsec profile {s['old_profile']}",
        f"no crypto ipsec transform-set {s['old_ts']}",

        f"crypto ipsec transform-set {g['transform_set']} "
        f"{g['transform_encryption']} {g['transform_hash']}",

        "mode transport",
        "exit",

        f"crypto ipsec profile {g['ipsec_profile']}",
        f"set transform-set {g['transform_set']}",
        "exit",

        f"interface {s['tunnel_iface']}",

        f"ip address {s['tunnel_ip']} {s['tunnel_mask']}",

        f"ip nhrp network-id {s['nhrp_network']}",
        f"ip nhrp authentication {g['nhrp_auth']}"
    ]

    for nhs in s["nhs"]:

        comandos.append(
            f"ip nhrp nhs {nhs['tunnel_ip']} "
            f"nbma {nhs['nbma']} multicast"
        )

    comandos.extend([

        "ip nhrp shortcut",

        "tunnel source Loopback0",
        "tunnel mode gre multipoint",

        f"tunnel protection ipsec profile "
        f"{g['ipsec_profile']} shared",

        f"tunnel key {s['tunnel_key']}",

        f"ip ospf cost {s['ospf_cost']}",
        f"ip ospf priority {s['ospf_priority']}",

        f"ip ospf hello-interval {g['ospf_hello']}",
        f"ip ospf dead-interval {g['ospf_dead']}",

        f"ip ospf network {g['ospf_network_type']}",

        "exit",

        f"router ospf {g['ospf_pid']}",

        f"no network {s['old_network']} "
        f"{s['old_wc']} area 0",

        f"network {s['new_network']} "
        f"{s['new_wc']} area 0",

        "exit",
        "end"
    ])

    return comandos

# =========================================================
# GENERAR JSON FINAL
# =========================================================

COMANDOS = {}

# HUBS
for nombre, datos in HUBS.items():
    COMANDOS[nombre] = generar_hub(nombre, GLOBAL, datos)

# SPOKES
for nombre, datos in SPOKES.items():
    COMANDOS[nombre] = generar_spoke(nombre, GLOBAL, datos)

# =========================================================
# EXPORTAR JSON
# =========================================================

with open("comandos_generados.json", "w") as archivo:
    json.dump(COMANDOS, archivo, indent=4)

print("Archivo comandos_generados.json creado correctamente")