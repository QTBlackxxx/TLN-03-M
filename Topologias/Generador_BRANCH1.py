import os
from jinja2 import Environment, FileSystemLoader

# =====================================================================
# 1. DEFINICIÓN DE DATOS (EL INVENTARIO DE SPOKES)
# =====================================================================
lista_spokes = [
    {
        # --- CPE-BRANCH1 ---
        "hostname": "CPE-BRANCH1",
        
        # Datos DMVPN y Criptografía
        "clave_vpn": "CISCO",
        "id_tunnel": "0",
        "ip_tunnel_local": "172.16.30.2",    
        "ip_tunnel_hub": "172.16.30.1",      
        "ip_publica_hub": "200.0.0.1",         
        "red_tunnel": "172.16.30.0",

        "id_tunnel_2":"1",
        "ip_tunnel_local_2": "172.16.40.2",
        "ip_tunnel_hub_2": "172.16.40.1",      
        "ip_publica_hub_2": "190.0.1.1",         
        "red_tunnel_2": "172.16.40.0",
        
        # Redes LAN internas a inyectar en EIGRP/OSPF
        "lan1": "192.168.5.0",
        "lan2": "192.168.15.0"
    },
    {
        # --- CPE-BRANCHBK ---
        "hostname": "CPE-BRANCH1-BK",
        
        # Datos DMVPN y Criptografía
        "clave_vpn": "CISCO",
        "id_tunnel": "0",                    
        "ip_tunnel_local": "172.16.30.3",    
        "ip_tunnel_hub": "172.16.30.1",
        "ip_publica_hub": "200.0.0.1",
        "red_tunnel": "172.16.30.0",
        
        "id_tunnel_2":"1",
        "ip_tunnel_local_2": "172.16.40.3",
        "ip_tunnel_hub_2": "172.16.40.1",      
        "ip_publica_hub_2": "190.0.1.1",        
        "red_tunnel_2": "172.16.40.0",
        
        # Redes LAN internas a inyectar en EIGRP
        "lan1": "192.168.5.0",
        "lan2": "192.168.15.0"
    }
]

# =====================================================================
# 2. MOTOR DE GENERACIÓN (JINJA2)
# =====================================================================

# Configurar Jinja2 para que busque archivos en la carpeta actual 
env = Environment(loader=FileSystemLoader('.'))

# Cargar la plantilla 
try:
    
    template = env.get_template('plantilla_branch1.txt')
except Exception as e:
    print(f"Error al cargar la plantilla: {e}")
    print("Asegúrate de que 'plantilla_dmvpn_spoke.txt' esté en la misma carpeta.")
    exit()

# Crear una carpeta para guardar los resultados y mantener el orden
carpeta_salida = "configuraciones"
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

#  iterar sobre cada router, generar su config y guardarla
print("[*] Generando configuraciones de túneles DMVPN...")
for router in lista_spokes:
    # Renderizar inyectando el diccionario actual
    configuracion_final = template.render(router)
    
    # Definir el nombre del archivo 
    nombre_archivo = f"{carpeta_salida}/{router['hostname']}.txt"
    
    # Guardar en disco
    with open(nombre_archivo, 'w') as f:
        f.write(configuracion_final)
        
    print(f"[EXITO] Archivo generado: {nombre_archivo}")

print("\n¡Proceso de generación terminado exitosamente!")