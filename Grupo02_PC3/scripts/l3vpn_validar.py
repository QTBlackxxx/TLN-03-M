"""
Parte 4 - Validacion de servicios MPLS L3VPN.

Demuestra, sobre la red ya configurada:
    - BGP: sesiones establecidas
    - OSPF: vecindades FULL
    - IPv4 VPN: conectividad entre sedes (ping + ruta)
    - IPv6 VPN: conectividad entre sedes (ping)

Reutiliza la conexion y el inventario ya resueltos en la Parte 3
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path

try:
    from napalm_validacion import (
        NOMBRES_INVENTARIO_CANDIDATOS,
        cargar_inventario,
        conectar,
        localizar_inventario,
        nombre_corto,
    )
except ImportError:
    print(
        "No se encontro napalm_validacion.py. "
        "Debe estar en la misma carpeta que validar_l3vpn.py."
    )
    sys.exit(1)

# Alcance de la validacion
CORE_OSPF_BGP = {"PE1", "PE2", "P1", "P2", "RR1", "RR2"}
CPE_HOSTS = {"CPE-1", "CPE-2"}
# Solo PE y RR participan de BGP VPNv4 (P1/P2 son transito puro,
# nunca deben tener rutas VPNv4 -- si aparecieran, seria mala señal)
VPNV4_HOSTS = {"PE1", "PE2", "RR1", "RR2"}

DESTINO_IPV4 = {
    "CPE-1": "192.168.20.10",
    "CPE-2": "192.168.10.10",
}
DESTINO_IPV6 = {
    "CPE-1": "2001:192:168:20::10",
    "CPE-2": "2001:192:168:10::10",
}
DESTINO_IPV4_GW = {
    "CPE-1": "192.168.20.1",
    "CPE-2": "192.168.10.1",
}
DESTINO_IPV6_GW = {
    "CPE-1": "2001:192:168:20::1",
    "CPE-2": "2001:192:168:10::1",
}
ORIGEN_IPV4 = {
    "CPE-1": "192.168.10.1",
    "CPE-2": "192.168.20.1",
}
ORIGEN_IPV6 = {
    "CPE-1": "2001:192:168:10::1",
    "CPE-2": "2001:192:168:20::1",
}
RUTA_IPV4_REMOTA = {
    "CPE-1": "192.168.20.0",
    "CPE-2": "192.168.10.0",
}

def parsear_ping(salida: str) -> dict:
    match = re.search(r"Success rate is (\d+) percent", salida)
    porcentaje = int(match.group(1)) if match else 0
    return {"exitoso": porcentaje > 0, "porcentaje": porcentaje}

def parsear_ospf_neighbors(salida: str) -> list[dict]:
    vecinos = []
    for linea in salida.splitlines():
        partes = linea.split()
        if len(partes) >= 5 and re.match(r"^\d+\.\d+\.\d+\.\d+$", partes[0]):
            vecinos.append({
                "neighbor_id": partes[0],
                "estado": partes[2],
                "interface": partes[-1],
            })
    return vecinos

def parsear_bgp_vpnv4_summary(salida: str) -> list[dict]:
    """
    Parsea 'show bgp vpnv4 unicast all summary'. La columna State/PfxRcd
    trae un numero si la sesion esta Established (cantidad de prefijos
    VPNv4 recibidos), o una palabra (Idle/Active/Connect/...) si no.
    """
    peers = []
    for linea in salida.splitlines():
        partes = linea.split()
        if not partes or not re.match(r"^\d+\.\d+\.\d+\.\d+$", partes[0]):
            continue
        ultimo = partes[-1]
        establecido = ultimo.isdigit()
        peers.append({
            "peer": partes[0],
            "establecido": establecido,
            "pfx_recibidos": int(ultimo) if establecido else 0,
            "estado_texto": "Established" if establecido else ultimo,
        })
    return peers

def validar_bgp(device) -> dict:
    resultado = {"ok": True, "peers": [], "error": None}
    try:
        bgp = device.get_bgp_neighbors()
        peers = bgp.get("global", {}).get("peers", {})
        for ip, datos in peers.items():
            up = bool(datos.get("is_up"))
            resultado["peers"].append(
                {"peer": ip, "is_up": up, "remote_as": datos.get("remote_as")}
            )
            if not up:
                resultado["ok"] = False
        if not peers:
            resultado["ok"] = False
    except Exception as e:
        resultado["ok"] = False
        resultado["error"] = str(e)
    return resultado

def validar_ospf(device) -> dict:
    resultado = {"ok": True, "vecinos": [], "error": None}
    try:
        salida = device.cli(["show ip ospf neighbor"])
        texto = list(salida.values())[0] if salida else ""
        vecinos = parsear_ospf_neighbors(texto)
        resultado["vecinos"] = vecinos
        if not vecinos:
            resultado["ok"] = False
        for v in vecinos:
            if not v["estado"].startswith("FULL"):
                resultado["ok"] = False
    except Exception as e:
        resultado["ok"] = False
        resultado["error"] = str(e)
    return resultado

def validar_bgp_vpnv4(device) -> dict:
    """
    Confirma que la sesion BGP intercambia rutas VPNv4 (el address-family
    que realmente lleva el trafico del cliente), no solo que la sesion
    IPv4 unicast generica este Established.
    """
    resultado = {"ok": True, "peers": [], "error": None}
    try:
        salida = device.cli(["show bgp vpnv4 unicast all summary"])
        texto = list(salida.values())[0] if salida else ""
        peers = parsear_bgp_vpnv4_summary(texto)
        resultado["peers"] = peers
        if not peers:
            resultado["ok"] = False
        for p in peers:
            if not p["establecido"]:
                resultado["ok"] = False
    except Exception as e:
        resultado["ok"] = False
        resultado["error"] = str(e)
    return resultado

def validar_conectividad_cpe(device, nombre: str) -> dict:
    resultado = {"ipv4": None, "ipv6": None, "ipv4_gw": None, "ipv6_gw": None, "ruta_ipv4": None}
    origen_v4 = ORIGEN_IPV4.get(nombre)
    origen_v6 = ORIGEN_IPV6.get(nombre)
    try:
        destino_v4 = DESTINO_IPV4[nombre]
        salida = device.cli([f"ping {destino_v4} source {origen_v4}"])
        texto = list(salida.values())[0] if salida else ""
        resultado["ipv4"] = parsear_ping(texto)
        resultado["ipv4"]["destino"] = destino_v4
    except Exception as e:
        resultado["ipv4"] = {"exitoso": False, "porcentaje": 0, "destino": DESTINO_IPV4.get(nombre, "?"), "error": str(e)}

    try:
        destino_v6 = DESTINO_IPV6[nombre]
        salida = device.cli([f"ping ipv6 {destino_v6} source {origen_v6}"])
        texto = list(salida.values())[0] if salida else ""
        resultado["ipv6"] = parsear_ping(texto)
        resultado["ipv6"]["destino"] = destino_v6
    except Exception as e:
        resultado["ipv6"] = {"exitoso": False, "porcentaje": 0, "destino": DESTINO_IPV6.get(nombre, "?"), "error": str(e)}

    try:
        destino_v4_gw = DESTINO_IPV4_GW[nombre]
        salida = device.cli([f"ping {destino_v4_gw} source {origen_v4}"])
        texto = list(salida.values())[0] if salida else ""
        resultado["ipv4_gw"] = parsear_ping(texto)
        resultado["ipv4_gw"]["destino"] = destino_v4_gw
    except Exception as e:
        resultado["ipv4_gw"] = {"exitoso": False, "porcentaje": 0, "destino": DESTINO_IPV4_GW.get(nombre, "?"), "error": str(e)}

    try:
        destino_v6_gw = DESTINO_IPV6_GW[nombre]
        salida = device.cli([f"ping ipv6 {destino_v6_gw} source {origen_v6}"])
        texto = list(salida.values())[0] if salida else ""
        resultado["ipv6_gw"] = parsear_ping(texto)
        resultado["ipv6_gw"]["destino"] = destino_v6_gw
    except Exception as e:
        resultado["ipv6_gw"] = {"exitoso": False, "porcentaje": 0, "destino": DESTINO_IPV6_GW.get(nombre, "?"), "error": str(e)}

    try:
        destino_ruta = RUTA_IPV4_REMOTA[nombre]
        rutas = device.get_route_to(destination=destino_ruta, protocol="static")
        resultado["ruta_ipv4"] = bool(rutas)
    except Exception:
        resultado["ruta_ipv4"] = False

    return resultado

def siguiente_numero_reporte_l3vpn(carpeta: Path) -> int:
    carpeta.mkdir(parents=True, exist_ok=True)
    numeros = []
    for f in carpeta.glob("l3vpn_reporte_*.txt"):
        try:
            numeros.append(int(f.stem.split("_")[2]))
        except (IndexError, ValueError):
            continue
    return max(numeros, default=0) + 1

def formatear_reporte(resultados_bgp: dict, resultados_bgp_vpnv4: dict,
                       resultados_ospf: dict, resultados_conectividad: dict) -> str:
    lineas = []
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineas.append("=" * 64)
    lineas.append("VALIDACION DE SERVICIOS MPLS L3VPN")
    lineas.append(f"Generado: {ahora}")
    lineas.append("=" * 64)

    lineas.append("")
    lineas.append("--- BGP: Sesiones establecidas ---")
    bgp_global_ok = True
    for router in sorted(resultados_bgp):
        r = resultados_bgp[router]
        if r["error"]:
            lineas.append(f"{router}: ERROR ({r['error']})")
            bgp_global_ok = False
            continue
        ups = sum(1 for p in r["peers"] if p["is_up"])
        total = len(r["peers"])
        estado = "OK" if r["ok"] else "FALLA"
        if not r["ok"]:
            bgp_global_ok = False
        detalle = ", ".join(
            f"{p['peer']} (AS{p['remote_as']}) {'UP' if p['is_up'] else 'DOWN'}"
            for p in r["peers"]
        )
        lineas.append(f"{router}: {ups}/{total} sesiones UP -> {estado}")
        if detalle:
            lineas.append(f"    {detalle}")
    lineas.append(f"Resultado BGP: {'OK' if bgp_global_ok else 'REVISAR'}")

    lineas.append("")
    lineas.append("--- BGP VPNv4: Intercambio de rutas del cliente ---")
    vpnv4_global_ok = True
    for router in sorted(resultados_bgp_vpnv4):
        r = resultados_bgp_vpnv4[router]
        if r["error"]:
            lineas.append(f"{router}: ERROR ({r['error']})")
            vpnv4_global_ok = False
            continue
        estado = "OK" if r["ok"] else "FALLA"
        if not r["ok"]:
            vpnv4_global_ok = False
        detalle = ", ".join(
            f"{p['peer']} ({p['estado_texto']}, {p['pfx_recibidos']} pfx)"
            for p in r["peers"]
        )
        lineas.append(f"{router}: {len(r['peers'])} vecinos VPNv4 -> {estado}")
        if detalle:
            lineas.append(f"    {detalle}")
    lineas.append(f"Resultado BGP VPNv4: {'OK' if vpnv4_global_ok else 'REVISAR'}")

    lineas.append("")
    lineas.append("--- OSPF: Vecindades FULL ---")
    ospf_global_ok = True
    for router in sorted(resultados_ospf):
        r = resultados_ospf[router]
        if r["error"]:
            lineas.append(f"{router}: ERROR ({r['error']})")
            ospf_global_ok = False
            continue
        full = sum(1 for v in r["vecinos"] if v["estado"].startswith("FULL"))
        total = len(r["vecinos"])
        estado = "OK" if r["ok"] else "FALLA"
        if not r["ok"]:
            ospf_global_ok = False
        detalle = ", ".join(f"{v['neighbor_id']}:{v['estado']}" for v in r["vecinos"])
        lineas.append(f"{router}: {full}/{total} vecinos FULL -> {estado}")
        if detalle:
            lineas.append(f"    {detalle}")
    lineas.append(f"Resultado OSPF: {'OK' if ospf_global_ok else 'REVISAR'}")

    lineas.append("")
    lineas.append("--- IPv4 VPN: Conectividad entre sedes ---")
    ipv4_red_ok = True
    ipv4_host_ok = True
    for router in sorted(resultados_conectividad):
        r = resultados_conectividad[router]
        origen = ORIGEN_IPV4.get(router, "?")
        gw = r["ipv4_gw"]
        ok_gw = gw.get("exitoso", False)
        if not ok_gw:
            ipv4_red_ok = False
        lineas.append(
            f"{router} (origen {origen}) -> {gw.get('destino','?')} "
            f"(interfaz del CPE remoto, red L3VPN pura): "
            f"ping {gw.get('porcentaje',0)}% -> {'OK' if ok_gw else 'FALLA'}"
        )
        host = r["ipv4"]
        ok_host = host.get("exitoso", False) and r.get("ruta_ipv4", False)
        if not ok_host:
            ipv4_host_ok = False
        lineas.append(
            f"{router} (origen {origen}) -> {host.get('destino','?')} "
            f"(host cliente, depende de PC-LAN): "
            f"ping {host.get('porcentaje',0)}% | "
            f"ruta {'presente' if r.get('ruta_ipv4') else 'NO presente'} -> "
            f"{'OK' if ok_host else 'FALLA'}"
        )
    lineas.append(f"Resultado IPv4 VPN (red L3VPN): {'OK' if ipv4_red_ok else 'REVISAR'}")
    lineas.append(f"Resultado IPv4 host cliente (PC-LAN): {'OK' if ipv4_host_ok else 'REVISAR'}")

    lineas.append("")
    lineas.append("--- IPv6 VPN: Conectividad entre sedes ---")
    ipv6_red_ok = True
    ipv6_host_ok = True
    for router in sorted(resultados_conectividad):
        r = resultados_conectividad[router]
        origen6 = ORIGEN_IPV6.get(router, "?")
        gw = r["ipv6_gw"]
        ok_gw = gw.get("exitoso", False)
        if not ok_gw:
            ipv6_red_ok = False
        lineas.append(
            f"{router} (origen {origen6}) -> {gw.get('destino','?')} "
            f"(interfaz del CPE remoto): "
            f"ping {gw.get('porcentaje',0)}% -> {'OK' if ok_gw else 'FALLA'}"
        )
        host = r["ipv6"]
        ok_host = host.get("exitoso", False)
        if not ok_host:
            ipv6_host_ok = False
        lineas.append(
            f"{router} (origen {origen6}) -> {host.get('destino','?')} "
            f"(host cliente): "
            f"ping {host.get('porcentaje',0)}% -> {'OK' if ok_host else 'FALLA'}"
        )
    lineas.append(f"Resultado IPv6 VPN (red L3VPN): {'OK' if ipv6_red_ok else 'REVISAR'}")
    lineas.append(f"Resultado IPv6 host cliente (PC-LAN): {'OK' if ipv6_host_ok else 'REVISAR'}")

    lineas.append("")
    lineas.append("=" * 64)
    lineas.append(
        f"RESUMEN PARTE 4: "
        f"BGP {'OK' if bgp_global_ok else 'REVISAR'} | "
        f"BGP VPNv4 {'OK' if vpnv4_global_ok else 'REVISAR'} | "
        f"OSPF {'OK' if ospf_global_ok else 'REVISAR'} | "
        f"IPv4 L3VPN {'OK' if ipv4_red_ok else 'REVISAR'} | "
        f"IPv4 PC-LAN {'OK' if ipv4_host_ok else 'REVISAR'} | "
        f"IPv6 L3VPN {'OK' if ipv6_red_ok else 'REVISAR'} | "
        f"IPv6 PC-LAN {'OK' if ipv6_host_ok else 'REVISAR'}"
    )
    lineas.append("=" * 64)

    return "\n".join(lineas)

def resolver_inventario() -> Path:
    for nombre in NOMBRES_INVENTARIO_CANDIDATOS:
        p = Path(nombre)
        if p.exists():
            return p
    encontrado = localizar_inventario(NOMBRES_INVENTARIO_CANDIDATOS)
    if encontrado is None:
        print("No se pudo ubicar el inventario automaticamente.")
        print("Verifica que funcione primero napalm_validacion.py (Parte 3).")
        sys.exit(1)
    return encontrado

def main() -> None:
    user = input("Usuario SSH: ")
    passwd = getpass("Password: ")

    ruta_inventario = resolver_inventario()
    print(f"Inventario: {ruta_inventario}")

    hosts = cargar_inventario(ruta_inventario)
    hosts_por_nombre = {nombre_corto(h): h for h in hosts}

    resultados_bgp: dict = {}
    resultados_bgp_vpnv4: dict = {}
    resultados_ospf: dict = {}
    resultados_conectividad: dict = {}

    for nombre in sorted(CORE_OSPF_BGP):
        host = hosts_por_nombre.get(nombre)
        if not host:
            print(f"Aviso: {nombre} no esta en el inventario, se omite.")
            continue
        print(f"  -> BGP/OSPF en {nombre}")
        try:
            device = conectar(host, user, passwd)
        except Exception as e:
            resultados_bgp[nombre] = {"ok": False, "peers": [], "error": f"conexion: {e}"}
            resultados_ospf[nombre] = {"ok": False, "vecinos": [], "error": f"conexion: {e}"}
            if nombre in VPNV4_HOSTS:
                resultados_bgp_vpnv4[nombre] = {"ok": False, "peers": [], "error": f"conexion: {e}"}
            continue
        resultados_bgp[nombre] = validar_bgp(device)
        resultados_ospf[nombre] = validar_ospf(device)
        if nombre in VPNV4_HOSTS:
            resultados_bgp_vpnv4[nombre] = validar_bgp_vpnv4(device)
        try:
            device.close()
        except Exception:
            pass

    for nombre in sorted(CPE_HOSTS):
        host = hosts_por_nombre.get(nombre)
        if not host:
            print(f"Aviso: {nombre} no esta en el inventario, se omite.")
            continue
        print(f"  -> Conectividad entre sedes desde {nombre}")
        try:
            device = conectar(host, user, passwd)
        except Exception as e:
            resultados_conectividad[nombre] = {
                "ipv4": {"exitoso": False, "porcentaje": 0, "destino": DESTINO_IPV4.get(nombre, "?"), "error": str(e)},
                "ipv6": {"exitoso": False, "porcentaje": 0, "destino": DESTINO_IPV6.get(nombre, "?"), "error": str(e)},
                "ruta_ipv4": False,
            }
            continue
        resultados_conectividad[nombre] = validar_conectividad_cpe(device, nombre)
        try:
            device.close()
        except Exception:
            pass

    reporte = formatear_reporte(resultados_bgp, resultados_bgp_vpnv4, resultados_ospf, resultados_conectividad)
    print()
    print(reporte)

    out_dir = Path("reportes")
    out_dir.mkdir(parents=True, exist_ok=True)
    numero = siguiente_numero_reporte_l3vpn(out_dir)
    nombre_archivo = f"l3vpn_reporte_{numero:03d}_{datetime.now().strftime('%m%d')}.txt"
    out_file = out_dir / nombre_archivo
    out_file.write_text(reporte, encoding="utf-8")
    print(f"\nReporte guardado en: {out_file}")

if __name__ == "__main__":
    main()