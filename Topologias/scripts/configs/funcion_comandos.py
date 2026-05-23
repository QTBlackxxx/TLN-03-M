import json

GLOBAL_DMVPN = {
     # ── ISAKMP / IPSEC ────────────────────────────────
    "isakmp_key" : "TLN03",
    "ts_name"    : "TS-DMVPN",
    "ts_enc"     : "esp-aes",
    "ts_hash"    : "esp-sha-hmac",
    "pf_name"    : "PF-DMVPN",
    # ── DMVPN ─────────────────────────────────────────
    "nhrp_key"   : "DMVPNKEY",
    "mtu"        : 1400,
    "mss"        : 1360,
    # ── OSPF ──────────────────────────────────────────
    "ospf_pid"   : 10,
    "ospf_area"  : 0,
    "ospf_hello" : 5,
    "ospf_dead"  : 20,
    # point-to-multipoint → NO DR/BDR
    "ospf_net_type" : "point-to-multipoint",
    # ── Tunnel ────────────────────────────────────────
    "tunnel_mask": "255.255.255.0",
    "tunnel_wc"  : "0.0.0.255",
}

# ── Parámetros únicos por HUB ─────────────────────────────────────────────────
HUB_PARAMS = {

    "CPE-HQ": {

        # Limpieza config vieja
        "old_key"      : "190.0.0.1",
        "old_pf"       : "PF-TO-BRANCH",
        "old_ts"       : "TS-TO-BRANCH",

        # Tunnel
        "tunnel_iface" : "Tunnel1",
        "tunnel_ip"    : "172.16.10.1",

        "tunnel_key"   : 100,

        "nhrp_net_id"  : 100,

        # OSPF
        "ospf_cost"    : 10,

        # Red DMVPN
        "tunnel_net"   : "172.16.10.0",

        # Cleanup red vieja
        "old_net_wc"   : "0.0.0.3",
    },

    "CPE-HQ-BK": {

        "old_key"      : "200.0.1.1",
        "old_pf"       : "PF-TO-BRANCH",
        "old_ts"       : "TS-TO-BRANCH",

        "tunnel_iface" : "Tunnel2",
        "tunnel_ip"    : "172.16.20.1",

        "tunnel_key"   : 200,

        "nhrp_net_id"  : 200,

        "ospf_cost"    : 100,

        "tunnel_net"   : "172.16.20.0",

        "old_net_wc"   : "0.0.0.3",
    },
}
 
SPOKE_PARAMS = {

    "CPE-BRANCH2": {

        # Limpieza config vieja
        "old_key" : "200.0.0.1",
        "old_pf"  : "PF-TO-HQ",
        "old_ts"  : "TS-TO-HQ",

        # Router ID
        "router_id" : "5.5.5.5",

        # Loopback
        "loopback_ip" : "180.0.0.1",

        # WAN
        "wan_iface" : "Ethernet0/1",
        "wan_ip"    : "10.0.0.73",
        "wan_mask"  : "255.255.255.252",
        "wan_gw"    : "10.0.0.74",

        # LAN
        "lan_iface" : "Ethernet0/2.25",
        "lan_ip"    : "192.168.25.2",
        "lan_mask"  : "255.255.255.0",

        # VRRP
        "vrrp_group"    : 25,
        "vrrp_virtual"  : "192.168.25.1",
        "vrrp_priority" : 110,

        # Tunnel HQ
        "tunnel_hq_iface" : "Tunnel1",
        "tunnel_hq_ip"    : "172.16.10.4",

        "hq_nhs"      : "172.16.10.1",
        "hq_nbma"     : "200.0.0.1",

        "hq_net_id"   : 100,
        "hq_tkey"     : 100,

        "hq_cost"     : 10,

        # Tunnel BK
        "tunnel_bk_iface" : "Tunnel2",
        "tunnel_bk_ip"    : "172.16.20.4",

        "bk_nhs"      : "172.16.20.1",
        "bk_nbma"     : "190.0.1.1",

        "bk_net_id"   : 200,
        "bk_tkey"     : 200,

        "bk_cost"     : 100,
    },



    "CPE-BRANCH2-BK": {

        "old_key" : "190.0.1.1",
        "old_pf"  : "PF-TO-HQ",
        "old_ts"  : "TS-TO-HQ",

        "router_id" : "6.6.6.6",

        "loopback_ip" : "180.0.1.1",

        "wan_iface" : "Ethernet0/1",
        "wan_ip"    : "10.0.0.77",
        "wan_mask"  : "255.255.255.252",
        "wan_gw"    : "10.0.0.78",

        "lan_iface" : "Ethernet0/2.25",
        "lan_ip"    : "192.168.25.3",
        "lan_mask"  : "255.255.255.0",

        "vrrp_group"    : 25,
        "vrrp_virtual"  : "192.168.25.1",
        "vrrp_priority" : 100,

        "tunnel_hq_iface" : "Tunnel1",
        "tunnel_hq_ip"    : "172.16.10.5",

        "hq_nhs"      : "172.16.10.1",
        "hq_nbma"     : "200.0.0.1",

        "hq_net_id"   : 100,
        "hq_tkey"     : 100,

        "hq_cost"     : 10,

        "tunnel_bk_iface" : "Tunnel2",
        "tunnel_bk_ip"    : "172.16.20.5",

        "bk_nhs"      : "172.16.20.1",
        "bk_nbma"     : "190.0.1.1",

        "bk_net_id"   : 200,
        "bk_tkey"     : 200,

        "bk_cost"     : 100,
    }
}



 
# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN: Genera el bloque completo del HUB
# ─────────────────────────────────────────────────────────────────────────────

comandos_generados = "configs/comandos_generados.json"

def config_hub(nombre_comando: str, device_name: str, g: dict, hubs: dict) -> list[str]:
    comandos_generados = "configs/comandos_generados.json"  

    
    """
    Genera los comandos IOS para un router HUB DMVPN.
 
    Pasos que genera:
      1. Limpieza config vieja (point-to-point → DMVPN)
      2. Crypto: isakmp key wildcard + transform-set + profile
      3. Interface Tunnel: NHS, NHRP multicast dynamic, redirect, mGRE, IPsec
      4. OSPF: reemplaza red /30 vieja por /24 nueva
 
    Args:
        nombre_comando: nombre del comando a ejecutar
        device_name : "CPE-HQ" o "CPE-HQ-BK"
        g           : diccionario GLOBAL_DMVPN
        hubs        : diccionario HUB_PARAMS
 
    Returns:
        Lista de strings con comandos IOS listos para enviar.
    """
    h = hubs[device_name]
 
    comando = [

        "conf terminal",

        # ─────────────────────────────────────────────
        # LIMPIEZA CONFIG VIEJA
        # ─────────────────────────────────────────────

        f"no crypto isakmp key {g['isakmp_key']} address {h['old_key']}",

        "no interface tunnel1",

        f"no crypto ipsec profile {h['old_pf']}",

        f"no crypto ipsec transform-set {h['old_ts']}",

        "",

        # ─────────────────────────────────────────────
        # ISAKMP
        # ─────────────────────────────────────────────

        "crypto isakmp policy 10",

        " encr aes",

        " authentication pre-share",

        " group 14",

        " lifetime 1000",

        "exit",

        f"crypto isakmp key {g['isakmp_key']} address 0.0.0.0",

        "",

        # ─────────────────────────────────────────────
        # IPSEC
        # ─────────────────────────────────────────────

        f"crypto ipsec transform-set {g['ts_name']} "
        f"{g['ts_enc']} {g['ts_hash']}",

        " mode transport",

        "exit",

        f"crypto ipsec profile {g['pf_name']}",

        f" set transform-set {g['ts_name']}",

        "exit",

        "",

        # ─────────────────────────────────────────────
        # DMVPN HUB
        # ─────────────────────────────────────────────

        f"interface {h['tunnel_iface']}",

        f" ip address {h['tunnel_ip']} {g['tunnel_mask']}",

        " no ip redirects",

        f" ip mtu {g['mtu']}",

        f" ip tcp adjust-mss {g['mss']}",

        f" ip nhrp authentication {g['nhrp_key']}",

        f" ip nhrp network-id {h['nhrp_net_id']}",

        " ip nhrp map multicast dynamic",

        # DMVPN Phase 3
        " ip nhrp redirect",

        # OSPF
        f" ip ospf network {g['ospf_net_type']}",

        f" ip ospf cost {h['ospf_cost']}",

        f" ip ospf hello-interval {g['ospf_hello']}",

        f" ip ospf dead-interval {g['ospf_dead']}",

        # Tunnel
        " tunnel source Loopback0",

        " tunnel mode gre multipoint",

        f" tunnel key {h['tunnel_key']}",

        f" tunnel protection ipsec profile {g['pf_name']}",

        " no shutdown",

        "exit",

        "",

        # ─────────────────────────────────────────────
        # OSPF
        # ─────────────────────────────────────────────

        f"router ospf {g['ospf_pid']}",

        f" no network {h['tunnel_net']} "
        f"{h['old_net_wc']} area {g['ospf_area']}",

        f" network {h['tunnel_net']} "
        f"{g['tunnel_wc']} area {g['ospf_area']}",

        "exit",

        "",

        "end",
    ]
    # Guardar comandos generados en un archivo JSON

    with open(comandos_generados, "r") as f:
        comandos = json.load(f)

    comandos[nombre_comando] = comando

    with open(comandos_generados, "w") as f:
        json.dump(comandos, f, indent=4)

    print(f"Configuración '{nombre_comando}' guardada.")

    return comandos_generados

def config_spoke(nombre_comando: str,device_name: str,g: dict,spokes: dict) -> list[str]:
    comandos_generados = "configs/comandos_generados.json"
    s = spokes[device_name]

    comando = [

        "conf terminal",

        # ─────────────────────────────────────
        # LIMPIEZA
        # ─────────────────────────────────────

        f"no crypto isakmp key {g['isakmp_key']} address {s['old_key']}",

        "no interface Tunnel1",

        f"no crypto ipsec profile {s['old_pf']}",

        f"no crypto ipsec transform-set {s['old_ts']}",

        "",

        # ─────────────────────────────────────
        # ISAKMP
        # ─────────────────────────────────────

        "crypto isakmp policy 10",

        " encr aes",

        " authentication pre-share",

        " group 14",

        " lifetime 1000",

        "exit",

        f"crypto isakmp key {g['isakmp_key']} address 0.0.0.0",

        "",

        # ─────────────────────────────────────
        # IPSEC
        # ─────────────────────────────────────

        f"crypto ipsec transform-set {g['ts_name']} "
        f"{g['ts_enc']} {g['ts_hash']}",

        " mode transport",

        "exit",

        f"crypto ipsec profile {g['pf_name']}",

        f" set transform-set {g['ts_name']}",

        "exit",

        "",

        # ─────────────────────────────────────
        # LOOPBACK
        # ─────────────────────────────────────

        "interface Loopback0",

        f" ip address {s['loopback_ip']} 255.255.255.255",

        " no shutdown",

        "exit",

        "",

        # ─────────────────────────────────────
        # TUNNEL HQ
        # ─────────────────────────────────────

        f"interface {s['tunnel_hq_iface']}",

        f" ip address {s['tunnel_hq_ip']} {g['tunnel_mask']}",

        f" ip mtu {g['mtu']}",

        f" ip tcp adjust-mss {g['mss']}",

        f" ip nhrp authentication {g['nhrp_key']}",

        f" ip nhrp network-id {s['hq_net_id']}",

        f" ip nhrp nhs {s['hq_nhs']}",

        f" ip nhrp map {s['hq_nhs']} {s['hq_nbma']}",

        f" ip nhrp map multicast {s['hq_nbma']}",

        " ip nhrp shortcut",

        f" ip ospf network {g['ospf_net_type']}",

        f" ip ospf cost {s['hq_cost']}",

        " tunnel source Loopback0",

        " tunnel mode gre multipoint",

        f" tunnel key {s['hq_tkey']}",

        f" tunnel protection ipsec profile {g['pf_name']} shared",

        " no shutdown",

        "exit",

        "",

        # ─────────────────────────────────────
        # TUNNEL BK
        # ─────────────────────────────────────

        f"interface {s['tunnel_bk_iface']}",

        f" ip address {s['tunnel_bk_ip']} {g['tunnel_mask']}",

        f" ip mtu {g['mtu']}",

        f" ip tcp adjust-mss {g['mss']}",

        f" ip nhrp authentication {g['nhrp_key']}",

        f" ip nhrp network-id {s['bk_net_id']}",

        f" ip nhrp nhs {s['bk_nhs']}",

        f" ip nhrp map {s['bk_nhs']} {s['bk_nbma']}",

        f" ip nhrp map multicast {s['bk_nbma']}",

        " ip nhrp shortcut",

        f" ip ospf network {g['ospf_net_type']}",

        f" ip ospf cost {s['bk_cost']}",

        " tunnel source Loopback0",

        " tunnel mode gre multipoint",

        f" tunnel key {s['bk_tkey']}",

        f" tunnel protection ipsec profile {g['pf_name']} shared",

        " no shutdown",

        "exit",

        "",

        # ─────────────────────────────────────
        # OSPF
        # ─────────────────────────────────────

        f"router ospf {g['ospf_pid']}",

        f" router-id {s['router_id']}",

        f" network 172.16.10.0 {g['tunnel_wc']} area {g['ospf_area']}",

        f" network 172.16.20.0 {g['tunnel_wc']} area {g['ospf_area']}",

        "exit",

        "",

        "end"
    ]

    with open(comandos_generados, "r") as f:
        comandos = json.load(f)

    comandos[nombre_comando] = comando

    with open(comandos_generados, "w") as f:
        json.dump(comandos, f, indent=4)

    print(f"Configuración '{nombre_comando}' guardada.")

    return comandos_generados