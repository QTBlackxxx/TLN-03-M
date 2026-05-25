# commands_hq.py
# Script 1: Lado HUB y Transporte
# Lee parámetros desde el archivo .env del equipo

from dotenv import dotenv_values

# ──────────────────────────────────────────────────────────────
# CARGAR ARCHIVO DE CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────
cfg = dotenv_values(".env")

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def net(cidr):
    """Separa '172.16.10.0/0.0.0.7' en (network, wildcard)"""
    return cidr.split("/")

def build_tunnel(prefix, modo="hub"):
    """Genera comandos de tunnel para HUB o SPOKE"""
    tid      = cfg[f"{prefix}_TUNNEL_ID"]
    tip      = cfg[f"{prefix}_TUNNEL_IP"]
    tmask    = cfg[f"{prefix}_TUNNEL_MASK"]
    tsource  = cfg[f"{prefix}_TUNNEL_SOURCE"]
    nhrp_auth= cfg[f"{prefix}_NHRP_AUTH"]
    nhrp_id  = cfg[f"{prefix}_NHRP_NET_ID"]

    cmds = [
        f"interface Tunnel{tid}",
        f" ip address {tip} {tmask}",
        f" ip nhrp authentication {nhrp_auth}",
    ]

    if modo == "hub":
        cmds.append(" ip nhrp map multicast dynamic")
    else:
        nhs_ip   = cfg[f"{prefix}_NHRP_NHS_IP"]
        nhs_nbma = cfg[f"{prefix}_NHRP_NHS_NBMA"]
        cmds.append(f" ip nhrp map {nhs_ip} {nhs_nbma}")
        cmds.append(f" ip nhrp map multicast {nhs_nbma}")
        cmds.append(f" ip nhrp nhs {nhs_ip}")

    cmds += [
        f" ip nhrp network-id {nhrp_id}",
        f" tunnel source {tsource}",
        " tunnel mode gre multipoint",
    ]

    if modo == "hub":
        if cfg.get(f"{prefix}_TUNNEL_NO_SPLIT_HORIZON") == "true":
            cmds.append(f" no ip split-horizon eigrp {cfg[f'{prefix}_EIGRP_AS']}")
        if cfg.get(f"{prefix}_TUNNEL_NO_NEXT_HOP_SELF") == "true":
            cmds.append(f" no ip next-hop-self eigrp {cfg[f'{prefix}_EIGRP_AS']}")

    cmds += [" no shutdown", "exit"]
    return cmds

def build_eigrp(prefix):
    """Genera comandos EIGRP"""
    as_num   = cfg[f"{prefix}_EIGRP_AS"]
    rid      = cfg[f"{prefix}_EIGRP_ROUTER_ID"]
    networks = cfg[f"{prefix}_EIGRP_NETWORKS"].split(",")
    passives = cfg.get(f"{prefix}_EIGRP_PASSIVE", "").split(",")

    cmds = [
        f"router eigrp {as_num}",
        f" router-id {rid}",
    ]
    for iface in passives:
        if iface:
            cmds.append(f" passive-interface {iface}")
    for net_entry in networks:
        n, w = net(net_entry)
        cmds.append(f" network {n} {w}")
    cmds += [" no auto-summary", "exit"]
    return cmds

def build_wan_iface(prefix):
    """Genera comandos de interfaz WAN simple"""
    iface = cfg[f"{prefix}_WAN_IFACE"]
    ip    = cfg[f"{prefix}_WAN_IP"]
    mask  = cfg[f"{prefix}_WAN_MASK"]
    return [
        f"interface {iface}",
        f" ip address {ip} {mask}",
        " no shutdown",
        "exit",
    ]

def build_static_route(prefix):
    """Genera ruta estática"""
    dst  = cfg[f"{prefix}_STATIC_DST"]
    mask = cfg[f"{prefix}_STATIC_MASK"]
    nh   = cfg[f"{prefix}_STATIC_NH"]
    return [f"ip route {dst} {mask} {nh}"]

def build_prefix_list(prefix):
    """Genera prefix-list"""
    name   = cfg[f"{prefix}_PREFIX_LIST_NAME"]
    seq    = cfg[f"{prefix}_PREFIX_LIST_SEQ"]
    permit = cfg[f"{prefix}_PREFIX_LIST_PERMIT"]
    return [f"ip prefix-list {name} seq {seq} permit {permit}"]


# ──────────────────────────────────────────────────────────────
# CONSTRUIR CONFIG_MAP DINÁMICAMENTE
# ──────────────────────────────────────────────────────────────
CONFIG_MAP = {

    cfg["HQ_HOSTNAME"]: (
        build_tunnel("HQ", modo="hub") +
        build_eigrp("HQ")
    ),

    cfg["HQBK_HOSTNAME"]: (
        build_tunnel("HQBK", modo="hub") +
        build_eigrp("HQBK")
    ),

    cfg["BR_HOSTNAME"]: (
        build_tunnel("BR", modo="spoke") +
        build_eigrp("BR")
    ),

    cfg["BRBK_HOSTNAME"]: (
        build_tunnel("BRBK", modo="spoke") +
        build_eigrp("BRBK")
    ),

    cfg["M3_HOSTNAME"]: (
        build_wan_iface("M3") +
        build_static_route("M3")
    ),

    cfg["C5_HOSTNAME"]: (
        build_wan_iface("C5") +
        build_static_route("C5")
    ),

    cfg["M2_HOSTNAME"]: (
        build_prefix_list("M2")
    ),

    cfg["C2_HOSTNAME"]: (
        build_prefix_list("C2")
    ),
}

# ──────────────────────────────────────────────────────────────
# DEVICES
# ──────────────────────────────────────────────────────────────
DEVICES = [
    {"host": cfg["HQ_HOST"],   "hostname": cfg["HQ_HOSTNAME"],   "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["HQBK_HOST"], "hostname": cfg["HQBK_HOSTNAME"], "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["BR_HOST"],   "hostname": cfg["BR_HOSTNAME"],   "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["BRBK_HOST"], "hostname": cfg["BRBK_HOSTNAME"], "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["M3_HOST"],   "hostname": cfg["M3_HOSTNAME"],   "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["C5_HOST"],   "hostname": cfg["C5_HOSTNAME"],   "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["M2_HOST"],   "hostname": cfg["M2_HOSTNAME"],   "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
    {"host": cfg["C2_HOST"],   "hostname": cfg["C2_HOSTNAME"],   "username": cfg["NET_USER"], "password": cfg["NET_PASS"]},
]
