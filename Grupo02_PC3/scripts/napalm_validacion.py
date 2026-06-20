"""
Parte 3 - Validacion del estado operativo de la red MPLS L3VPN con NAPALM.
Lee el inventario generado en la Parte 1 y para cada dispositivo ejecuta los getters NAPALM
requeridos por la guia:

    get_facts()
    get_interfaces()
    get_interfaces_ip()
    get_route_to()
    get_bgp_neighbors()
    get_environment()*

Genera un reporte en texto plano por consola y lo guarda en reportes/.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path

try:
    from napalm import get_network_driver
except ImportError:
    print("Falta instalar napalm: pip install napalm")
    sys.exit(1)

# Configuracion de roles: que getters pedirle a cada dispositivo
ROLES = {
    "PE1": "pe", "PE2": "pe",
    "P1": "p", "P2": "p",
    "RR1": "rr", "RR2": "rr",
    "CPE-1": "cpe", "CPE-2": "cpe",
    "SW-1": "switch", "SW-2": "switch",
    "SW-LAN-1": "switch", "SW-LAN-2": "switch",
}

CON_BGP = {"pe", "p", "rr"}            # roles que corren BGP
CON_IP = {"pe", "p", "rr", "cpe"}      # roles con IP de capa 3 

# Chequeo de conectividad entre sedes 
RUTA_REMOTA_CPE = {
    "CPE-1": "192.168.20.0",   # LAN de la sede 2, vista desde CPE-1
    "CPE-2": "192.168.10.0",   # LAN de la sede 1, vista desde CPE-2
}
VRF_REMOTA_PE = {
    "PE1": ("A", "192.168.20.0"),
    "PE2": ("A", "192.168.10.0"),
}

NOMBRES_INVENTARIO_CANDIDATOS = ["inventory.ini"]

# Inventario
def cargar_inventario(path: Path, grupo: str = "MPLS_update") -> list[str]:
    """Lee un inventario estilo Ansible INI y devuelve los hosts de 'grupo'."""
    hosts: list[str] = []
    dentro_del_grupo = False
    with open(path, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if linea.startswith("["):
                dentro_del_grupo = (linea == f"[{grupo}]")
                continue
            if dentro_del_grupo and "=" not in linea:
                hosts.append(linea)
    return hosts

def localizar_inventario(nombres_archivo: list[str] = NOMBRES_INVENTARIO_CANDIDATOS,
                          max_niveles_arriba: int = 4) -> Path | None:
    """
    Busca el inventario sin que el usuario indique la ruta, probando varios
    nombres posibles.
    Parte de la carpeta donde vive este script y, si no lo encuentra ahi,
    sube hasta 'max_niveles_arriba' carpetas, recorriendo cada nivel de
    forma recursiva.
    """
    inicio = Path(__file__).resolve().parent
    candidato = inicio
    for _ in range(max_niveles_arriba + 1):
        for root, _dirs, files in os.walk(candidato):
            # Evita perderse en carpetas pesadas o irrelevantes
            _dirs[:] = [d for d in _dirs if d not in (".git", "__pycache__", "node_modules")]
            for nombre in nombres_archivo:
                if nombre in files:
                    return Path(root) / nombre
        if candidato.parent == candidato:
            break
        candidato = candidato.parent
    return None

def nombre_corto(hostname: str) -> str:
    """clab-MPLS-PE1 -> PE1 / clab-MPLS-SW-LAN-1 -> SW-LAN-1"""
    return hostname.replace("clab-MPLS-", "")

# Validacion por dispositivo
def conectar(hostname: str, user: str, passwd: str, timeout: int = 15):
    driver = get_network_driver("ios")
    device = driver(
        hostname=hostname,
        username=user,
        password=passwd,
        timeout=timeout,
        optional_args={"port": 22},
    )
    device.open()
    return device

def obtener_entorno_basico(device) -> dict:
    """
    Reemplazo simplificado de get_environment() para evitar el bug conocido
    de NAPALM con cisco_iol (UnboundLocalError al parsear 'show processes memory').
    Extrae solo CPU usando 'show processes cpu' directamente via CLI.
    """
    entorno = {}
    try:
        salida = device.cli(["show processes cpu"])
        texto = list(salida.values())[0] if salida else ""
        for linea in texto.splitlines():
            if "CPU utilization" in linea:
                entorno["cpu_resumen"] = linea.strip()
                break
    except Exception as e:
        entorno["error"] = str(e)
    return entorno

def validar_dispositivo(hostname: str, user: str, passwd: str) -> dict:
    nombre = nombre_corto(hostname)
    rol = ROLES.get(nombre, "desconocido")

    resultado = {
        "router": nombre,
        "hostname": hostname,
        "rol": rol,
        "estado": "OK",
        "errores": [],
        "notas": [],
        "facts": {},
        "interfaces_activas": 0,
        "interfaces_total": 0,
        "bgp_vecinos": None,
        "rutas": {},
        "ip_resumen": None,
        "loopback_ip": None,
    }

    try:
        device = conectar(hostname, user, passwd)
    except Exception as e:
        resultado["estado"] = "FAIL"
        resultado["errores"].append(f"No se pudo conectar: {e}")
        return resultado

    # get_facts
    try:
        resultado["facts"] = device.get_facts()
    except Exception as e:
        resultado["errores"].append(f"get_facts(): {e}")

    # get_interfaces
    try:
        interfaces = device.get_interfaces()
        resultado["interfaces_total"] = len(interfaces)
        resultado["interfaces_activas"] = sum(
            1 for i in interfaces.values() if i.get("is_up")
        )
    except Exception as e:
        resultado["errores"].append(f"get_interfaces(): {e}")

    # get_interfaces_ip (solo dispositivos con IP de capa 3)
    if rol in CON_IP:
        try:
            ips = device.get_interfaces_ip()
            total_ipv4 = sum(len(datos.get("ipv4", {})) for datos in ips.values())
            total_ipv6 = sum(len(datos.get("ipv6", {})) for datos in ips.values())
            resultado["ip_resumen"] = (
                f"{total_ipv4} IPv4 / {total_ipv6} IPv6 en {len(ips)} interfaces"
            )
            for iface, datos in ips.items():
                if "loopback" in iface.lower():
                    ipv4_addrs = datos.get("ipv4", {})
                    if ipv4_addrs:
                        resultado["loopback_ip"] = next(iter(ipv4_addrs))
                    break
        except Exception as e:
            resultado["errores"].append(f"get_interfaces_ip(): {e}")

    # get_bgp_neighbors (solo P, PE y RR)
    if rol in CON_BGP:
        try:
            bgp = device.get_bgp_neighbors()
            peers = bgp.get("global", {}).get("peers", {})
            resultado["bgp_vecinos"] = len(peers)
        except Exception as e:
            resultado["errores"].append(f"get_bgp_neighbors(): {e}")

    # get_route_to (evidencia extra para conectividad entre sedes)
    try:
        if nombre in RUTA_REMOTA_CPE:
            destino = RUTA_REMOTA_CPE[nombre]
            rutas = device.get_route_to(destination=destino, protocol="static")
            resultado["rutas"][destino] = bool(rutas)
        elif nombre in VRF_REMOTA_PE:
            vrf, destino = VRF_REMOTA_PE[nombre]
            try:
                rutas = device.get_route_to(destination=destino, vrf=vrf)
                resultado["rutas"][f"vrf {vrf} -> {destino}"] = bool(rutas)
            except TypeError:
                # El driver 'ios' de NAPALM no siempre soporta kwarg 'vrf'
                salida = device.cli([f"show ip route vrf {vrf} {destino}"])
                texto = list(salida.values())[0] if salida else ""
                resultado["rutas"][f"vrf {vrf} -> {destino}"] = (
                    "Routing entry" in texto or "via" in texto
                )
    except Exception as e:
        resultado["errores"].append(f"get_route_to(): {e}")

    # get_environment (reemplazado por chequeo manual via CLI, evita bug NAPALM/cisco_iol)
    try:
        entorno = obtener_entorno_basico(device)
        if entorno.get("cpu_resumen"):
            resultado["notas"].append(f"Entorno: {entorno['cpu_resumen']}")
        elif entorno.get("error"):
            resultado["notas"].append(
                f"get_environment(): no se pudo obtener via CLI alterna ({entorno['error']})"
            )
    except Exception as e:
        resultado["errores"].append(f"get_environment() (alterna): {e}")

    try:
        device.close()
    except Exception:
        pass

    if resultado["errores"]:
        resultado["estado"] = "WARN"

    return resultado

def siguiente_numero_reporte(carpeta: Path) -> int:
    """Busca el número más alto usado en reportes/napalm_reporte_NNN_*.txt y devuelve el siguiente."""
    carpeta.mkdir(parents=True, exist_ok=True)
    numeros = []
    for f in carpeta.glob("napalm_reporte_*.txt"):
        try:
            numeros.append(int(f.stem.split("_")[2]))
        except (IndexError, ValueError):
            continue
    return max(numeros, default=0) + 1

# Reporte
def formatear_reporte(resultados: list[dict]) -> str:
    lineas = []
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineas.append("=" * 64)
    lineas.append("REPORTE DE VALIDACION NAPALM - RED MPLS L3VPN")
    lineas.append(f"Generado: {ahora}")
    lineas.append("=" * 64)

    for r in resultados:
        lineas.append("")
        lineas.append(f"Router: {r['router']}")
        lineas.append(f"Hostname: {r['hostname']}")
        lineas.append(f"Rol: {r['rol']}")
        lineas.append(
            f"Interfaces activas: {r['interfaces_activas']}/{r['interfaces_total']}"
        )
        if r["bgp_vecinos"] is not None:
            lineas.append(f"Vecinos BGP: {r['bgp_vecinos']}")
        else:
            lineas.append("Vecinos BGP: N/A (no corre BGP)")
        if r["facts"]:
            f_ = r["facts"]
            lineas.append(
                f"Modelo: {f_.get('model', '?')} | "
                f"OS: {f_.get('os_version', '?')} | "
                f"Uptime: {f_.get('uptime', '?')}s"
            )
        if r.get("ip_resumen"):
            lineas.append(f"Direccionamiento IP: {r['ip_resumen']}")
        if r.get("loopback_ip"):
            lineas.append(f"  Loopback: {r['loopback_ip']}")
        for destino, encontrada in r["rutas"].items():
            estado_ruta = "ENCONTRADA" if encontrada else "NO ENCONTRADA"
            lineas.append(f"Ruta hacia {destino}: {estado_ruta}")
        lineas.append(f"Estado: {r['estado']}")
        for err in r["errores"]:
            lineas.append(f"  ! {err}")
        for nota in r["notas"]:
            lineas.append(f"  i {nota}")

    total = len(resultados)
    ok = sum(1 for r in resultados if r["estado"] == "OK")
    warn = sum(1 for r in resultados if r["estado"] == "WARN")
    fail = sum(1 for r in resultados if r["estado"] == "FAIL")

    lineas.append("")
    lineas.append("=" * 64)
    lineas.append(f"Resumen: {total} dispositivos | OK: {ok} | WARN: {warn} | FAIL: {fail}")
    lineas.append("=" * 64)

    return "\n".join(lineas)

# Main
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validacion NAPALM de la red MPLS L3VPN"
    )
    parser.add_argument(
        "--inventario", type=Path, default=None,
        help="Ruta al inventory.ini. Si se omite, el script intenta "
             "ubicarlo automaticamente cerca de si mismo.",
    )
    parser.add_argument(
        "--grupo", default="MPLS_update",
        help="Nombre del grupo dentro del inventario a validar",
    )
    parser.add_argument(
        "--reportes", type=Path, default=Path("reportes"),
        help="Carpeta donde guardar el reporte .txt",
    )
    args = parser.parse_args()

    user = input("Usuario SSH: ")
    passwd = getpass("Password: ")

    if args.inventario is not None:
        ruta_inventario = args.inventario
        if not ruta_inventario.exists():
            print(f"No se encontro el inventario en la ruta indicada: {ruta_inventario}")
            sys.exit(1)
    else:
        ruta_inventario = None
        for nombre in NOMBRES_INVENTARIO_CANDIDATOS:
            candidato_cwd = Path(nombre)
            if candidato_cwd.exists():
                ruta_inventario = candidato_cwd
                break
        if ruta_inventario is None:
            encontrado = localizar_inventario(NOMBRES_INVENTARIO_CANDIDATOS)
            if encontrado is None:
                nombres = " / ".join(NOMBRES_INVENTARIO_CANDIDATOS)
                print(f"No se pudo ubicar el inventario automaticamente (probé: {nombres}).")
                print("Indica la ruta manualmente con: --inventario <ruta>")
                sys.exit(1)
            print(f"Inventario detectado automaticamente en: {encontrado}")
            ruta_inventario = encontrado

    hosts = cargar_inventario(ruta_inventario, args.grupo)
    if not hosts:
        print(f"No se encontraron hosts en el grupo [{args.grupo}] de {ruta_inventario}")
        sys.exit(1)

    print(f"Validando {len(hosts)} dispositivos: {', '.join(hosts)}")
    resultados = []
    for host in hosts:
        print(f"  -> {host}")
        resultados.append(validar_dispositivo(host, user, passwd))

    reporte = formatear_reporte(resultados)
    print()
    print(reporte)

    args.reportes.mkdir(parents=True, exist_ok=True)
    numero = siguiente_numero_reporte(args.reportes)
    nombre_archivo = f"napalm_reporte_{numero:03d}_{datetime.now().strftime('%m%d')}.txt"
    out_file = args.reportes / nombre_archivo
    out_file.write_text(reporte, encoding="utf-8")
    print(f"\nReporte guardado en: {out_file}")

if __name__ == "__main__":
    main()