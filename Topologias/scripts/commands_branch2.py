#!/usr/bin/env python3
# -- coding: utf-8 --
import os
import sys

try:
    from dotenv import dotenv_values
    _USAR_DOTENV = True
except ImportError:
    _USAR_DOTENV = False


# =============================================================================
# 1. CARGA DEL .env
# =============================================================================

def cargar_env(ruta=".env"):
    if not os.path.exists(ruta):
        sys.exit(f"[ERROR] No se encontro el archivo .env en: {ruta}")

    if _USAR_DOTENV:
        return {k: v for k, v in dotenv_values(ruta).items() if v is not None}

    env = {}
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            env[clave.strip()] = valor.strip()
    return env


# =============================================================================
# 2. HELPERS DE LECTURA
# =============================================================================

class EnvRouter:
    def __init__(self, env, prefijo):
        self.env = env
        self.prefijo = prefijo

    def get(self, nombre, por_defecto=None):
        return self.env.get(self.prefijo + nombre, por_defecto)

    def existe(self, nombre):
        return (self.prefijo + nombre) in self.env

    def bool(self, nombre, por_defecto=False):
        valor = self.get(nombre)
        if valor is None:
            return por_defecto
        return valor.strip().lower() == "true"

    def lista(self, nombre):
        valor = self.get(nombre)
        if not valor:
            return []
        return [x.strip() for x in valor.split(",") if x.strip()]

    def par(self, valor, sep="/"):
        izq, der = valor.split(sep, 1)
        return izq.strip(), der.strip()


# =============================================================================
# 3. FUNCIONES QUE ARMAN CADA BLOQUE
# =============================================================================

def build_tracks(r):
    lineas = []
    if not r.bool("MODULE_ROUTING_TRACKING"):
        return lineas
    for track_id in r.lista("VRRP_TRACK_IDS"):
        valor = r.get(f"TRACK_{track_id}")
        if not valor:
            continue
        red, mascara = r.par(valor)
        lineas.append(f"track {track_id} ip route {red} {mascara} reachability")
    return lineas


def build_loopback(r):
    return [
        "interface Loopback0",
        f" ip address {r.get('LOOPBACK_IP')} 255.255.255.255",
        " no shutdown",
        "exit",
    ]


def build_wan(r):
    return [
        f"interface {r.get('WAN_IFACE')}",
        f" ip address {r.get('WAN_IP')} {r.get('WAN_MASK')}",
        " ip nat outside",
        " no shutdown",
        "exit",
    ]


def build_lan_fisica(r):
    return [
        f"interface {r.get('LAN_IFACE')}",
        " no ip address",
        " no shutdown",
        "exit",
    ]


def descubrir_subifs(r):
    indices = []
    i = 1
    while r.existe(f"SUBIF_{i}_VLAN"):
        indices.append(i)
        i += 1
    return indices


def build_subinterfaces(r):
    lineas = []
    rol = (r.get("VRRP_ROLE") or "master").lower()
    preempt = r.bool("VRRP_PREEMPT")
    track_ids = r.lista("VRRP_TRACK_IDS")
    usa_tracking = r.bool("MODULE_ROUTING_TRACKING")
    lan_iface = r.get("LAN_IFACE")

    for i in descubrir_subifs(r):
        vlan = r.get(f"SUBIF_{i}_VLAN")
        ip = r.get(f"SUBIF_{i}_IP")
        mask = r.get(f"SUBIF_{i}_MASK")
        vip = r.get(f"SUBIF_{i}_VRRP_VIP")
        prioridad = r.get(f"SUBIF_{i}_VRRP_PRIORITY")

        lineas.append(f"interface {lan_iface}.{vlan}")
        lineas.append(f" encapsulation dot1q {vlan}")
        lineas.append(f" ip address {ip} {mask}")
        lineas.append(" ip nat inside")
        lineas.append(f" vrrp {vlan} ip {vip}")

        if prioridad:
            lineas.append(f" vrrp {vlan} priority {prioridad}")
        if preempt:
            lineas.append(f" vrrp {vlan} preempt")
        if rol == "master" and usa_tracking:
            for track_id in track_ids:
                lineas.append(f" vrrp {vlan} track {track_id}")

        lineas.append(" no shutdown")
        lineas.append("exit")   
    return lineas


def build_tunnel(r):
    if r.get("MODULE_TUNNEL") != "tunnel_spoke":
        return []
    return [
        f"interface Tunnel{r.get('TUNNEL_ID')}",
        f" ip address {r.get('TUNNEL_IP')} {r.get('TUNNEL_MASK')}",
        f" ip nhrp authentication {r.get('NHRP_AUTH')}",
        f" ip nhrp map {r.get('NHRP_NHS_IP')} {r.get('NHRP_NHS_NBMA')}",
        f" ip nhrp map multicast {r.get('NHRP_NHS_NBMA')}",
        f" ip nhrp network-id {r.get('NHRP_NET_ID')}",
        f" ip nhrp nhs {r.get('NHRP_NHS_IP')}",
        f" tunnel source {r.get('TUNNEL_SOURCE')}",
        " tunnel mode gre multipoint",
        " no shutdown",
        "exit",
    ]


def build_eigrp(r):
    if not r.bool("MODULE_ROUTING_EIGRP"):
        return []
    lan_iface = r.get("LAN_IFACE")
    lineas = [
        f"router eigrp {r.get('EIGRP_AS')}",
        f" router-id {r.get('EIGRP_ROUTER_ID')}",
    ]
    for i in descubrir_subifs(r):
        vlan = r.get(f"SUBIF_{i}_VLAN")
        lineas.append(f" passive-interface {lan_iface}.{vlan}")
    for entrada in r.lista("EIGRP_NETWORKS"):
        red, wildcard = r.par(entrada)
        lineas.append(f" network {red} {wildcard}")
    lineas.append(" no auto-summary")
    lineas.append("exit")
    return lineas


def build_default_route(r):
    if not r.bool("MODULE_ROUTING_STATIC"):
        return []
    gw = r.get("WAN_GW")
    if not gw:
        gw = _gateway_p2p(r.get("WAN_IP"))
    return [
        f"ip route 0.0.0.0 0.0.0.0 {gw}",
    ]


def _gateway_p2p(wan_ip):
    octetos = wan_ip.split(".")
    ultimo = int(octetos[3])
    vecino = ultimo - 1 if ultimo % 2 == 0 else ultimo + 1
    octetos[3] = str(vecino)
    return ".".join(octetos)


def build_nat(r):
    if not r.bool("MODULE_ROUTING_NAT"):
        return []
    acl_num = "10"
    lineas = [
        f"no ip access-list standard {acl_num}",
        f"ip access-list standard {acl_num}",
    ]
    secuencia = 10
    for entrada in r.lista("NAT_ACL_PERMITS"):
        red, wildcard = r.par(entrada)
        lineas.append(f" {secuencia} permit {red} {wildcard}")
        secuencia += 10
    lineas.append("exit")
    pool = r.get("NAT_POOL_NAME")
    lineas.append(
        f"ip nat pool {pool} {r.get('NAT_POOL_START')} {r.get('NAT_POOL_END')} "
        f"prefix-length {r.get('NAT_POOL_PREFIX')}"
    )
    lineas.append(f"ip nat inside source list {acl_num} pool {pool} overload")
    return lineas


# =============================================================================
# 4. ENSAMBLADO COMPLETO
# =============================================================================

def build_cpe_config(r):
    config = []
    config += build_tracks(r)
    config += build_loopback(r)
    config += build_wan(r)
    config += build_lan_fisica(r)
    config += build_subinterfaces(r)
    config += build_tunnel(r)
    config += build_eigrp(r)
    config += build_default_route(r)
    config += build_nat(r)
    return config


# =============================================================================
# 5. DEVICES y CONFIG_MAP — para deploy.py
# =============================================================================

_env = cargar_env(".env")

_PREFIJOS = [("B2_", ), ("B2BK_", )]

DEVICES = [
    {
        "host":     _env.get(f"{p}HOST"),
        "hostname": _env.get(f"{p}HOSTNAME"),
        "username": _env.get("NET_USER"),
        "password": _env.get("NET_PASS"),
    }
    for (p,) in _PREFIJOS
]

CONFIG_MAP = {
    _env.get(f"{p}HOSTNAME"): build_cpe_config(EnvRouter(_env, p))
    for (p,) in _PREFIJOS
}


# =============================================================================
# 6. MAIN
# =============================================================================

if __name__ == "__main__":
    for hostname, cmds in CONFIG_MAP.items():
        print(f"\n=== {hostname} ===")
        for cmd in cmds:
            print(f"  {cmd}")
