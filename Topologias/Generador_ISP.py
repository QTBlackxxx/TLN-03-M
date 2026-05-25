import os
from jinja2 import Environment, FileSystemLoader

# =====================================================================
# 1. DEFINICIÓN DE DATOS (EL INVENTARIO DEL ISP)
# =====================================================================
lista_routers_isp = [
    { 
        "hostname":"M2",
        # --- INTERFAZ WAN NUEVA ---
        "nueva_interfaz": "Ethernet1/2",
        "ip_wan": "10.0.0.101",        
        "mask_wan": "255.255.255.252",
        # ---  RUTEO ADICIONAL ---
        "pool_destino": "200.0.2.0",
        "mask_pool": "255.255.255.248",
        "ip_wan_destino": "10.0.0.102",
        "id_tag": "290",
        "nombre_route": "BRANCH2-M2",
        "id_bgp": "100",
        # ---  ACTUALIZACIÓN DE FILTROS ---
        "seq_deny": 12,
        "seq_permit": 15,
        "ISP":"MOVISTAR",
        "pool_publico": "200.0.2.0",   
        "cidr_pool": "29"
    },
    {
        "hostname":"C2",
        # ---  INTERFAZ WAN NUEVA ---
        "nueva_interfaz": "Ethernet1/2",
        "ip_wan": "10.0.0.105",        
        "mask_wan": "255.255.255.252",
        # ---  RUTEO ADICIONAL ---
        "pool_destino": "200.0.3.0",
        "mask_pool": "255.255.255.248",
        "ip_wan_destino": "10.0.0.106",
        "id_tag": "390",
        "nombre_route": "BRANCHBK2-C2",
        "id_bgp": "200",
        # ---  ACTUALIZACIÓN DE FILTROS ---
        "seq_deny": 12,
        "seq_permit": 15,
        "ISP": "CLARO",
        "pool_publico": "200.0.3.0",  
        "cidr_pool": "29"
    }
]

# =====================================================================
# 2. MOTOR DE GENERACIÓN (JINJA2)
# =====================================================================

env = Environment(loader=FileSystemLoader('.'))

try:
    # Asegúrate de que el nombre coincida con tu archivo .txt
    template = env.get_template('plantilla_isp.txt') 
except Exception as e:
    print(f"Error al cargar la plantilla: {e}")
    exit()

carpeta_salida = "configuraciones"
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

print("Generando configuraciones para el ISP...")
for router in lista_routers_isp:
    configuracion_final = template.render(router)
    
    nombre_archivo = f"{carpeta_salida}/{router['hostname']}.txt"
    
    with open(nombre_archivo, 'w') as f:
        f.write(configuracion_final)
        
    print(f"[EXITO] Archivo generado: {nombre_archivo}")

print("\n¡Listo! Configuración generada.")