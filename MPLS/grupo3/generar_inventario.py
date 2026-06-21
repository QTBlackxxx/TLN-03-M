#!/usr/bin/env python3
"""
generar_inventario.py

Genera automaticamente un inventario de hardware/software de la red MPLS
(corriendo en containerlab) usando Ansible y el modulo cisco.ios.ios_facts,
y exporta el resultado en formato CSV o TXT.

Flujo:
    1. Ejecuta gather_facts.yml contra el inventory.ini (via ansible-playbook).
    2. El playbook deja un JSON por host en una carpeta temporal.
    3. Este script lee todos los JSON, arma una tabla y la exporta.

Uso basico:
    python3 generar_inventario.py
    python3 generar_inventario.py --formato txt
    python3 generar_inventario.py --formato csv --salida reportes/inventario.csv
    python3 generar_inventario.py --grupo PE_routers
    python3 generar_inventario.py --inventory mi_inventory.ini --playbook mi_playbook.yml

Requisitos:
    - ansible-core instalado y en PATH (ansible-playbook)
    - coleccion cisco.ios instalada:  ansible-galaxy collection install cisco.ios
    - coleccion ansible.netcommon instalada (dependencia de cisco.ios)
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------------------
# Configuracion por defecto (se puede sobreescribir por linea de comandos)
# ----------------------------------------------------------------------------

DEFAULT_INVENTORY = "inventory.ini"
DEFAULT_PLAYBOOK = "playbooks/gather_facts.yml"
DEFAULT_OUTPUT_DIR = "reportes"

# Columnas del reporte, en el orden en que se quieren mostrar.
# Deben coincidir con las claves que el playbook escribe en cada JSON.
CAMPOS_REPORTE = [
    "hostname",
    "grupos",
    "host_conexion",
    "modelo",
    "tipo_ios",
    "version_ios",
    "serial",
    "uptime",
    "memoria_total_mb",
    "memoria_libre_mb",
    "estado",
]


def ejecutar_playbook(inventory_path, playbook_path, output_dir, grupo, verbose):
    """
    Ejecuta ansible-playbook contra el inventory dado, pasando output_dir
    como extra-var para que el playbook sepa donde dejar los JSON.
    """
    if not Path(inventory_path).is_file():
        sys.exit(f"[ERROR] No se encontro el archivo de inventario: {inventory_path}")

    if not Path(playbook_path).is_file():
        sys.exit(f"[ERROR] No se encontro el playbook: {playbook_path}")

    if shutil.which("ansible-playbook") is None:
        sys.exit(
            "[ERROR] No se encontro 'ansible-playbook' en el PATH.\n"
            "        Instala ansible-core (pip install ansible-core) y la "
            "coleccion cisco.ios:\n"
            "        ansible-galaxy collection install cisco.ios ansible.netcommon"
        )

    cmd = [
        "ansible-playbook",
        "-i", inventory_path,
        playbook_path,
        "--extra-vars", f"output_dir={output_dir}",
    ]

    # Si el usuario quiere limitar a un grupo/host especifico (ej: PE_routers)
    if grupo:
        cmd += ["--limit", grupo]

    if verbose:
        cmd.append("-v")

    print(f"[INFO] Ejecutando: {' '.join(cmd)}")
    resultado = subprocess.run(cmd, capture_output=not verbose, text=True)

    if resultado.returncode != 0:
        print("[ADVERTENCIA] ansible-playbook termino con errores en algunos hosts.")
        if not verbose and resultado.stdout:
            print(resultado.stdout[-3000:])  # ultimas lineas, por si ayuda a debuggear
        if not verbose and resultado.stderr:
            print(resultado.stderr[-2000:])
        # No abortamos: puede que algunos hosts si hayan respondido y haya
        # JSON validos para reportar. El bloque rescue del playbook ya marca
        # los fallidos como "INALCANZABLE".
    else:
        print("[INFO] Playbook ejecutado correctamente.")


def leer_resultados(output_dir):
    """
    Lee todos los .json generados por el playbook en output_dir y los
    devuelve como una lista de diccionarios, ordenados por hostname.
    """
    carpeta = Path(output_dir)
    if not carpeta.is_dir():
        sys.exit(f"[ERROR] No se genero la carpeta de resultados: {output_dir}")

    archivos_json = sorted(carpeta.glob("*.json"))
    if not archivos_json:
        sys.exit(f"[ERROR] No se encontraron archivos JSON en: {output_dir}")

    filas = []
    for archivo in archivos_json:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[ADVERTENCIA] No se pudo leer {archivo}: {exc}")
            continue

        # Normalizamos el campo 'grupos' (lista) a texto separado por '|'
        if isinstance(datos.get("grupos"), list):
            datos["grupos"] = "|".join(datos["grupos"])

        filas.append(datos)

    filas.sort(key=lambda d: d.get("hostname", ""))
    return filas


def exportar_csv(filas, ruta_salida):
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_REPORTE, extrasaction="ignore")
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
    print(f"[OK] Reporte CSV generado: {ruta_salida}")


def exportar_txt(filas, ruta_salida):
    """
    Genera un reporte TXT legible, en formato tabla de ancho fijo,
    con un encabezado de fecha/hora y separadores.
    """
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)

    anchos = {campo: max(len(campo), 12) for campo in CAMPOS_REPORTE}
    for fila in filas:
        for campo in CAMPOS_REPORTE:
            valor = str(fila.get(campo, "N/A"))
            anchos[campo] = max(anchos[campo], len(valor))

    def formatear_fila(valores):
        return " | ".join(
            str(valores.get(campo, "N/A")).ljust(anchos[campo]) for campo in CAMPOS_REPORTE
        )

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("REPORTE DE INVENTARIO - RED MPLS (containerlab)\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de dispositivos: {len(filas)}\n")
        f.write("=" * 80 + "\n\n")

        encabezado = formatear_fila({campo: campo for campo in CAMPOS_REPORTE})
        f.write(encabezado + "\n")
        f.write("-" * len(encabezado) + "\n")

        for fila in filas:
            f.write(formatear_fila(fila) + "\n")

        # Resumen final: cuantos OK vs INALCANZABLE
        ok = sum(1 for fila in filas if fila.get("estado") == "OK")
        falla = len(filas) - ok
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Dispositivos OK: {ok}   |   Inalcanzables: {falla}\n")

    print(f"[OK] Reporte TXT generado: {ruta_salida}")


def main():
    parser = argparse.ArgumentParser(
        description="Genera un inventario de la red MPLS (containerlab) via "
                    "Ansible (cisco.ios.ios_facts) y lo exporta a CSV o TXT."
    )
    parser.add_argument(
        "--inventory", default=DEFAULT_INVENTORY,
        help=f"Ruta al inventory.ini (default: {DEFAULT_INVENTORY})",
    )
    parser.add_argument(
        "--playbook", default=DEFAULT_PLAYBOOK,
        help=f"Ruta al playbook de recoleccion (default: {DEFAULT_PLAYBOOK})",
    )
    parser.add_argument(
        "--grupo", default=None,
        help="Limitar la ejecucion a un grupo/host de Ansible (ej: PE_routers, MPLS_core)",
    )
    parser.add_argument(
        "--formato", choices=["csv", "txt", "ambos"], default="csv",
        help="Formato del reporte de salida (default: csv)",
    )
    parser.add_argument(
        "--salida", default=None,
        help="Ruta del archivo de salida. Si no se especifica, se genera "
             "automaticamente en la carpeta 'reportes/' con timestamp.",
    )
    parser.add_argument(
        "--mantener-json", action="store_true",
        help="No borrar la carpeta temporal con los JSON intermedios al finalizar.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Mostrar la salida completa de ansible-playbook en pantalla.",
    )

    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Carpeta temporal donde el playbook va a dejar el JSON de cada host
    output_dir_json = tempfile.mkdtemp(prefix="ansible_facts_")

    try:
        ejecutar_playbook(
            inventory_path=args.inventory,
            playbook_path=args.playbook,
            output_dir=output_dir_json,
            grupo=args.grupo,
            verbose=args.verbose,
        )

        filas = leer_resultados(output_dir_json)
        print(f"[INFO] Dispositivos procesados: {len(filas)}")

        formatos = ["csv", "txt"] if args.formato == "ambos" else [args.formato]

        for formato in formatos:
            if args.salida:
                ruta = args.salida
            else:
                ruta = os.path.join(DEFAULT_OUTPUT_DIR, f"inventario_{timestamp}.{formato}")

            if formato == "csv":
                exportar_csv(filas, ruta)
            else:
                exportar_txt(filas, ruta)

    finally:
        if not args.mantener_json:
            shutil.rmtree(output_dir_json, ignore_errors=True)
        else:
            print(f"[INFO] JSON intermedios conservados en: {output_dir_json}")


if __name__ == "__main__":
    main()