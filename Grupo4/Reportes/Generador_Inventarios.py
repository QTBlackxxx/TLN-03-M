import yaml
import os
import re
import sys
from collections import defaultdict

def generar_inventario(archivo_entrada):
    dir_inv = "nuevos inventarios"
    archivo_inv = os.path.join(dir_inv, "nuevo_inventario.ini")

    if not os.path.exists(dir_inv):
        os.makedirs(dir_inv)

    try:
        with open(archivo_entrada, "r") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado ({archivo_entrada}).")
        sys.exit(1)

    nombre_lab = data.get("name", "lab")
    nodos = data.get("topology", {}).get("nodes", {})
    grupos = defaultdict(list)

    for nodo, config in nodos.items():
        if config.get("kind") == "linux":
            continue
            
        match = re.match(r'^([A-Za-z]+)', nodo)
        grupo = match.group(1).upper() if match else "OTROS"
        
        grupos[grupo].append(f"{nodo} ansible_host=clab-{nombre_lab}-{nodo}")

    with open(archivo_inv, "w") as f:
        for grupo, lista in grupos.items():
            f.write(f"[{grupo}]\n")
            f.write("\n".join(lista) + "\n\n")

        f.write("[all:vars]\n")
        f.write("ansible_user=admin\n")
        f.write("ansible_password=admin\n")
        f.write("ansible_network_os=cisco.ios\n")
        f.write("ansible_connection=network_cli\n")
        
    print(f"Inventario generado en: {archivo_inv}")

if __name__ == "__main__":
    archivo = input("Ingresa el archivo [Enter para 'topologia.yml']: ").strip() or "topologia.yml"
    generar_inventario(archivo)