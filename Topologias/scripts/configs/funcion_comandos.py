import json

GLOBAL_DMVPN = {
    "isakmp_key" : "TLN03",
    "ts_name"    : "TS-DMVPN",
    "ts_enc"     : "esp-aes",
    "ts_hash"    : "esp-sha-hmac",
    "pf_name"    : "PF-DMVPN",
    "nhrp_key"   : "DMVPNKEY",
    "ospf_pid"   : 10,
    "ospf_area"  : 0,
    "ospf_hello" : 5,
    "ospf_dead"  : 20,
    "ospf_prio"  : 255,          # HUB siempre DR → priority máximo
    "tunnel_mask": "255.255.255.0",
    "tunnel_wc"  : "0.0.0.255",
}
 
# ── Parámetros únicos por HUB ─────────────────────────────────────────────────
HUB_PARAMS = {
    "CPE-HQ": {
        "old_key"      : "190.0.0.1",        # key vieja point-to-point a borrar
        "old_pf"       : "PF-TO-BRANCH",     # profile viejo a borrar
        "old_ts"       : "TS-TO-BRANCH",     # transform-set viejo a borrar
        "tunnel_iface" : "Tunnel1",
        "tunnel_ip"    : "172.16.10.1",
        "nhrp_net_id"  : 100,
        "ospf_cost"    : 10,                 # primario → costo bajo
        "tunnel_net"   : "172.16.10.0",
        "old_net_wc"   : "0.0.0.3",          # wildcard red vieja /30
    },
    "CPE-HQ-BK": {
        "old_key"      : "200.0.1.1",        # key vieja point-to-point a borrar
        "old_pf"       : "PF-TO-BRANCH",
        "old_ts"       : "TS-TO-BRANCH",
        "tunnel_iface" : "Tunnel2",
        "tunnel_ip"    : "172.16.20.1",
        "nhrp_net_id"  : 200,
        "ospf_cost"    : 100,                # backup → costo alto
        "tunnel_net"   : "172.16.20.0",
        "old_net_wc"   : "0.0.0.3",
    },
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
        "",
        f"no crypto isakmp key {g['isakmp_key']} address {h['old_key']}",
        f"crypto isakmp key {g['isakmp_key']} address 0.0.0.0",
        f"no interface {h['tunnel_iface']}",
        f"no crypto ipsec profile {h['old_pf']}",
        f"no crypto ipsec transform-set {h['old_ts']}",
        "",
        f"crypto ipsec transform-set {g['ts_name']} {g['ts_enc']} {g['ts_hash']}",
        " mode transport",
        "exit",
        f"crypto ipsec profile {g['pf_name']}",
        f" set transform-set {g['ts_name']}",
        "exit",
        "",
        f"interface {h['tunnel_iface']}",
        f" ip address {h['tunnel_ip']} {g['tunnel_mask']}",
        " no ip redirects",                   # evita que el hub redirija paquetes spoke→spoke
        f" ip nhrp network-id {h['nhrp_net_id']}",
        f" ip nhrp authentication {g['nhrp_key']}",
        " ip nhrp map multicast dynamic",     # aprender multicast de los spokes dinámicamente
        " ip nhrp redirect",                  # DMVPN fase 3: hub redirige spoke→spoke directo
        " tunnel source Loopback0",
        " tunnel mode gre multipoint",        # mGRE: un túnel para N spokes
        f" tunnel protection ipsec profile {g['pf_name']}",
        f" ip ospf priority {g['ospf_prio']}", # 255 → siempre DR en el segmento DMVPN
        f" ip ospf cost {h['ospf_cost']}",
        f" ip ospf hello-interval {g['ospf_hello']}",
        f" ip ospf dead-interval {g['ospf_dead']}",
        "exit",
        "",
        f"router ospf {g['ospf_pid']}",
        f" no network {h['tunnel_net']} {h['old_net_wc']} area {g['ospf_area']}",
        f" network {h['tunnel_net']} {g['tunnel_wc']} area {g['ospf_area']}",
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


 