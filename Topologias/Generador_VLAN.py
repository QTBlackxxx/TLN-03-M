import os
from jinja2 import Environment, FileSystemLoader

# =====================================================================
# 1. DEFINICIÓN DE DATOS (INVENTARIO DE SWITCHES)
# =====================================================================
lista_switches = [
    {
        "hostname": "SW",
        "interface_master": "Ethernet1/1",
        "interface_backup": "Ethernet0/1",
        "lista_vlans": [
            {"id": 5, "nombre": "VLAN5"},
            {"id": 15, "nombre": "VLAN15"}
        ],
        "puertos_acceso": [
            {"nombre": "Ethernet1/0", "vlan": 5},
            {"nombre": "Ethernet0/3", "vlan": 5},
            {"nombre": "Ethernet1/2", "vlan": 15},
            {"nombre": "Ethernet0/2", "vlan": 15}
        ]
    }

]

# =====================================================================
# 2. MOTOR DE GENERACIÓN (JINJA2)
# =====================================================================

# Configurar el cargador para leer la plantilla desde el directorio actual
env = Environment(loader=FileSystemLoader('.'))

# Intentar cargar la plantilla 
try:
    template = env.get_template('plantilla_sw.txt')
except Exception as e:
    print(f"Error al cargar la plantilla: {e}")
    exit()

# Carpeta de salida para los archivos generados
carpeta_salida = "configuraciones"
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

print("[*] Generando configuraciones de Switch...")

for sw in lista_switches:
    # Generamos el archivo renderizando los datos del switch actual
    configuracion_final = template.render(sw)
    nombre_archivo = f"{carpeta_salida}/{sw['hostname']}.txt"
    
    with open(nombre_archivo, 'w') as f:
        f.write(configuracion_final)
        
    print(f"[+] Configuración generada para: {nombre_archivo}")

print("\n¡Listo! Todos los archivos de configuración han sido creados.")