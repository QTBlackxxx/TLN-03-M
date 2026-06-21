"""
config_auditor.py - Parte 5: Automatización Python
Busca comandos especificos en configuraciones de routers MPLS L3VPN
y genera reportes en CSV y TXT.

Requiere: pip install netmiko
"""

import re
import csv
import os
import json
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


# ─── Inventario de dispositivos (espejo del inventory.ini de Ansible) ──────────

DEVICES = [
    # ── MPLS Core ─────────────────────────────────────────────────────────
    {"name": "PE1", "host": "clab-MPLS-PE1", "device_type": "cisco_ios", "username": "admin", "password": "admin"},
    {"name": "PE2", "host": "clab-MPLS-PE2", "device_type": "cisco_ios", "username": "admin", "password": "admin"},
    {"name": "P1",  "host": "clab-MPLS-P1",  "device_type": "cisco_ios", "username": "admin", "password": "admin"},
    {"name": "P2",  "host": "clab-MPLS-P2",  "device_type": "cisco_ios", "username": "admin", "password": "admin"},
    {"name": "RR1", "host": "clab-MPLS-RR1", "device_type": "cisco_ios", "username": "admin", "password": "admin"},
    {"name": "RR2", "host": "clab-MPLS-RR2", "device_type": "cisco_ios", "username": "admin", "password": "admin"},

    # ── CPEs ──────────────────────────────────────────────────────────────
    {"name": "CPE1", "host": "clab-MPLS-CPE-1", "device_type": "cisco_ios", "username": "admin", "password": "admin"},
    {"name": "CPE2", "host": "clab-MPLS-CPE-2", "device_type": "cisco_ios", "username": "admin", "password": "admin"},
]

# ─── Patrones que buscamos en cada configuracion ────────────────────────────────

SEARCH_PATTERNS = {
    "interfaces_loopback": r"^interface Loopback\d+",
    "ospf_process":        r"^router ospf \d+",
    "ospf_network":        r"^\s+network .+ area \S+",
    "mpls_ldp":            r"^mpls ldp router-id|^\s+mpls ip",
    "bgp_process":         r"^router bgp \d+",
    "bgp_neighbor":        r"^\s+neighbor \S+ remote-as \d+",
    "vrf_definition":      r"^vrf definition \S+|^ip vrf \S+",
    "vpnv4_family":        r"address-family vpnv4",
    "vpnv6_family":        r"address-family vpnv6",
    "route_distinguisher": r"rd \S+:\S+",
    "route_target":        r"route-target (import|export) \S+",
}

OUTPUT_DIR = "reportes"


def get_device_config(device: dict) -> str | None:
    """Conecta al router via SSH y obtiene 'show running-config'."""
    conn_params = {
        "device_type": device["device_type"],
        "host":        device["host"],
        "username":    device["username"],
        "password":    device["password"],
        "timeout":     15,
    }
    try:
        print(f"  Conectando a {device['name']} ({device['host']})...")
        with ConnectHandler(**conn_params) as conn:
            config = conn.send_command("show running-config", read_timeout=60)
        print(f"  OK - {device['name']}: configuracion obtenida ({len(config)} chars)")
        return config
    except NetmikoTimeoutException:
        print(f"  ERROR - {device['name']}: timeout de conexion")
        return None
    except NetmikoAuthenticationException:
        print(f"  ERROR - {device['name']}: fallo de autenticacion")
        return None
    except Exception as e:
        print(f"  ERROR - {device['name']}: {e}")
        return None


def search_patterns_in_config(config: str, device_name: str) -> dict:
    """Busca todos los patrones definidos en la configuracion de un dispositivo."""
    results = {"device": device_name, "timestamp": datetime.now().isoformat()}

    for pattern_name, regex in SEARCH_PATTERNS.items():
        matches = re.findall(regex, config, re.MULTILINE)
        results[pattern_name] = {
            "count":   len(matches),
            "matches": matches[:10],  # max 10 ejemplos por patron
        }

    # Metricas adicionales derivadas
    results["total_interfaces"] = len(re.findall(r"^interface \S+", config, re.MULTILINE))
    results["total_vrfs"]       = len(re.findall(r"^(vrf definition|ip vrf) \S+", config, re.MULTILINE))
    results["mpls_enabled"]     = bool(re.search(r"mpls ip|mpls label protocol", config, re.MULTILINE))
    results["ldp_enabled"]      = bool(re.search(r"mpls ldp", config, re.MULTILINE))

    return results


def determine_device_role(results: dict) -> str:
    """Infiere el rol del dispositivo segun su configuracion."""
    has_vrf    = results["total_vrfs"] > 0
    has_vpnv4  = results["vpnv4_family"]["count"] > 0
    has_bgp    = results["bgp_process"]["count"] > 0
    has_rr     = bool  # se detecta por route-reflector-client en vecinos

    if has_vrf and has_vpnv4:
        return "PE (Provider Edge)"
    elif has_bgp and not has_vrf:
        return "RR (Route Reflector)"
    elif results["mpls_enabled"] and not has_bgp:
        return "P (Provider Core)"
    else:
        return "Desconocido"


def generate_txt_report(all_results: list, filepath: str):
    """Genera reporte detallado en formato TXT."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("   REPORTE DE AUDITORIA - RED MPLS L3VPN\n")
        f.write(f"   Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        for r in all_results:
            if "error" in r:
                f.write(f"[{r['device']}] ERROR: {r['error']}\n\n")
                continue

            rol = determine_device_role(r)
            f.write(f"{'─' * 60}\n")
            f.write(f"Router : {r['device']}\n")
            f.write(f"Rol     : {rol}\n")
            f.write(f"Fecha   : {r['timestamp']}\n")
            f.write(f"{'─' * 60}\n")

            f.write(f"  Interfaces totales   : {r['total_interfaces']}\n")
            f.write(f"  Loopbacks            : {r['interfaces_loopback']['count']}\n")
            f.write(f"  VRFs configurados    : {r['total_vrfs']}\n")
            f.write(f"  MPLS habilitado      : {'Si' if r['mpls_enabled'] else 'No'}\n")
            f.write(f"  LDP habilitado       : {'Si' if r['ldp_enabled'] else 'No'}\n")
            f.write(f"  Proceso OSPF         : {'Si' if r['ospf_process']['count'] else 'No'}\n")
            f.write(f"  Redes OSPF           : {r['ospf_network']['count']}\n")
            f.write(f"  Proceso BGP          : {'Si' if r['bgp_process']['count'] else 'No'}\n")
            f.write(f"  Vecinos BGP          : {r['bgp_neighbor']['count']}\n")
            f.write(f"  Familia VPNv4        : {'Si' if r['vpnv4_family']['count'] else 'No'}\n")
            f.write(f"  Familia VPNv6        : {'Si' if r['vpnv6_family']['count'] else 'No'}\n")
            f.write(f"  Route Distinguishers : {r['route_distinguisher']['count']}\n")
            f.write(f"  Route Targets        : {r['route_target']['count']}\n")

            # Mostrar ejemplos de VRFs encontrados
            if r["vrf_definition"]["matches"]:
                f.write("\n  VRFs encontrados:\n")
                for vrf in r["vrf_definition"]["matches"]:
                    f.write(f"    - {vrf.strip()}\n")

            # Mostrar vecinos BGP encontrados
            if r["bgp_neighbor"]["matches"]:
                f.write("\n  Vecinos BGP encontrados:\n")
                for neighbor in r["bgp_neighbor"]["matches"]:
                    f.write(f"    - {neighbor.strip()}\n")

            f.write("\n")

        # Resumen global
        f.write("=" * 70 + "\n")
        f.write("RESUMEN GLOBAL\n")
        f.write("=" * 70 + "\n")
        ok = [r for r in all_results if "error" not in r]
        f.write(f"  Dispositivos auditados : {len(all_results)}\n")
        f.write(f"  Exitosos               : {len(ok)}\n")
        f.write(f"  Con error              : {len(all_results) - len(ok)}\n")
        total_vrfs = sum(r["total_vrfs"] for r in ok)
        total_bgp  = sum(r["bgp_neighbor"]["count"] for r in ok)
        f.write(f"  Total VRFs en la red   : {total_vrfs}\n")
        f.write(f"  Total vecinos BGP      : {total_bgp}\n")

    print(f"  Reporte TXT generado: {filepath}")


def generate_csv_report(all_results: list, filepath: str):
    """Genera reporte resumido en formato CSV (una fila por dispositivo)."""
    campos = [
        "device", "rol", "timestamp",
        "total_interfaces", "loopbacks", "total_vrfs",
        "mpls_enabled", "ldp_enabled",
        "ospf_process", "ospf_networks",
        "bgp_process", "bgp_neighbors",
        "vpnv4", "vpnv6",
        "route_distinguishers", "route_targets",
        "estado",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

        for r in all_results:
            if "error" in r:
                writer.writerow({"device": r["device"], "estado": f"ERROR: {r['error']}"})
                continue

            writer.writerow({
                "device":             r["device"],
                "rol":                determine_device_role(r),
                "timestamp":          r["timestamp"],
                "total_interfaces":   r["total_interfaces"],
                "loopbacks":          r["interfaces_loopback"]["count"],
                "total_vrfs":         r["total_vrfs"],
                "mpls_enabled":       r["mpls_enabled"],
                "ldp_enabled":        r["ldp_enabled"],
                "ospf_process":       r["ospf_process"]["count"] > 0,
                "ospf_networks":      r["ospf_network"]["count"],
                "bgp_process":        r["bgp_process"]["count"] > 0,
                "bgp_neighbors":      r["bgp_neighbor"]["count"],
                "vpnv4":              r["vpnv4_family"]["count"] > 0,
                "vpnv6":              r["vpnv6_family"]["count"] > 0,
                "route_distinguishers": r["route_distinguisher"]["count"],
                "route_targets":      r["route_target"]["count"],
                "estado":             "OK",
            })

    print(f"  Reporte CSV generado: {filepath}")


def generate_json_report(all_results: list, filepath: str):
    """Guarda todos los datos crudos en JSON (util para integracion con otras herramientas)."""
    serializable = []
    for r in all_results:
        entry = {k: v for k, v in r.items()}
        serializable.append(entry)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    print(f"  Reporte JSON generado: {filepath}")


def main():
    print("\n" + "=" * 60)
    print("  CONFIG AUDITOR - Red MPLS L3VPN")
    print("  Parte 5: Script Python adicional")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_results = []

    for device in DEVICES:
        print(f"\n[{device['name']}]")
        config = get_device_config(device)

        if config is None:
            all_results.append({"device": device["name"], "error": "No se pudo conectar"})
            continue

        results = search_patterns_in_config(config, device["name"])
        all_results.append(results)

        # Resumen rapido por pantalla
        rol = determine_device_role(results)
        print(f"  Rol detectado   : {rol}")
        print(f"  Interfaces      : {results['total_interfaces']}")
        print(f"  VRFs            : {results['total_vrfs']}")
        print(f"  Vecinos BGP     : {results['bgp_neighbor']['count']}")

    # Generar reportes
    print("\n[Generando reportes...]")
    generate_txt_report(all_results, f"{OUTPUT_DIR}/auditoria_{timestamp_str}.txt")
    generate_csv_report(all_results, f"{OUTPUT_DIR}/auditoria_{timestamp_str}.csv")
    generate_json_report(all_results, f"{OUTPUT_DIR}/auditoria_{timestamp_str}.json")

    print("\n" + "=" * 60)
    print(f"  Auditoria completada. Reportes en: ./{OUTPUT_DIR}/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()