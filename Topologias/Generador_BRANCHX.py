import os
from jinja2 import Environment, FileSystemLoader

# =====================================================================
# 1. DEFINICIÓN DE DATOS (EL INVENTARIO)
# =====================================================================

lista_routers = [
    {
        # --- CPE-BRANCH2 (MASTER) ---
        "hostname": "CPE-BRANCH2",
        
        # Interfaces Físicas y Transporte
        "interfaz_wan": "Ethernet0/1",
        "ip_wan": "10.0.0.102",
        "mask_wan": "255.255.255.252",
        "gateway_isp": "10.0.0.101",
        
        # IP Pública de Servicio (Loopback)
        "ip_publica_loopback": "200.0.2.1",
        
        # Datos del Pool NAT
        "ip_pool_inicio": "200.0.2.2",
        "ip_pool_fin": "200.0.2.6",
        "mascara_pool": "29",
        
        # Redes para la ACL de NAT Exemption
        "red_lan_sucursal": "192.168.0.0",
        "wildcard_sucursal": "0.0.255.255",
        "red_lan_hq": "10.0.0.0", 
        "wildcard_hq": "0.255.255.255",
        
        # Datos DMVPN y Criptografía
        "clave_vpn": "CISCO",
        "id_tunnel": "0",
        "ip_tunnel_local": "172.16.30.4",
        "ip_tunnel_hub": "172.16.30.1",   
        "ip_publica_hub": "200.0.0.1",    
        "red_tunnel": "172.16.30.0",

        
        "id_tunnel_2":"1",
        "ip_tunnel_local_2": "172.16.40.4",
        "ip_tunnel_hub_2": "172.16.40.1",      
        "ip_publica_hub_2": "190.0.1.1",         
        "red_tunnel_2": "172.16.40.0",


        #LANS para EIGRP

        "lan1": "192.168.50.0",
        "lan2": "192.168.150.0",
        
        # Configuración LAN y VRRP
        "interfaz_lan": "Ethernet0/2",
        "vlans": [
            {
                "id" : 5,
                "ip_fisica": "192.168.50.2",
                "mask_lan": "255.255.255.0",
                "ip_virtual": "192.168.50.1",
                "prioridad": 100, # Master
                
            },
            {
                "id": 15,
                "ip_fisica": "192.168.150.2",
                "mask_lan": "255.255.255.0",
                "ip_virtual": "192.168.150.1",
                "prioridad": 100, # Master
                
            }
        ]
    },
    {
        # --- CPE-BRANCH2-BK (BACKUP) ---
        "hostname": "CPE-BRANCH2-BK",
        
        # Interfaces Físicas y Transporte (Distinto enlace)
        "interfaz_wan": "Ethernet0/1",
        "ip_wan": "10.0.0.106", 
        "mask_wan": "255.255.255.252",
        "gateway_isp": "10.0.0.105",
        
        # IP Pública de Servicio (Loopback diferente)
        "ip_publica_loopback": "200.0.3.1",
        
        # Datos del Pool NAT (Distinto pool)
        "ip_pool_inicio": "200.0.3.2",
        "ip_pool_fin": "200.0.3.6",
        "mascara_pool": "29",
        
        # Redes para la ACL (Igual que el Master)
        "red_lan_sucursal": "192.168.0.0",
        "wildcard_sucursal": "0.0.255.255",
        "red_lan_hq": "10.0.0.0",
        "wildcard_hq": "0.255.255.255",
        
        # Datos DMVPN 
        "clave_vpn": "CISCO",
        "id_tunnel": "0",
        "ip_tunnel_local": "172.16.30.5", 
        "ip_tunnel_hub": "172.16.30.1",
        "ip_publica_hub": "200.0.0.1",
        "red_tunnel": "172.16.30.0",

        "id_tunnel_2":"1",
        "ip_tunnel_local_2": "172.16.40.5",
        "ip_tunnel_hub_2": "172.16.40.1",      
        "ip_publica_hub_2": "190.0.1.1",        
        "red_tunnel_2": "172.16.40.0",

        #LANS para EIGRP

        "lan1": "192.168.50.0",
        "lan2": "192.168.150.0",
        
        # Configuración LAN y VRRP
        "interfaz_lan": "Ethernet0/2",
        "vlans": [
            {
                "id": 5,
                "ip_fisica": "192.168.50.3", 
                "mask_lan": "255.255.255.0",
                "ip_virtual": "192.168.50.1",
                "prioridad": 95, # Backup (prioridad menor a 100)

            },
            {
                "id": 15,
                "ip_fisica": "192.168.150.3", # IP física .3
                "mask_lan": "255.255.255.0",
                "ip_virtual": "192.168.150.1",
                "prioridad": 95, # Backup
            }
        ]
    }
]

# =====================================================================
# 2. MOTOR DE GENERACIÓN (JINJA2)
# =====================================================================

# Configurar Jinja2 para que busque archivos en la carpeta actual 
env = Environment(loader=FileSystemLoader('.'))

# Cargar la plantilla 
try:
    template = env.get_template('plantilla_branch2.txt')
except Exception as e:
    print(f"Error al cargar la plantilla: {e}")
    print("Asegúrate de que 'plantilla_branch2.txt' esté en la misma carpeta.")
    exit()

# Crear una carpeta para guardar los resultados y mantener el orden
carpeta_salida = "configuraciones"
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Bucle : iterar sobre cada router, generar su config y guardarla
print(f"Generando configuraciones...")
for router in lista_routers:
    # Renderizar inyectando el diccionario actual
    configuracion_final = template.render(router)
    
    # Definir el nombre del archivo 
    nombre_archivo = f"{carpeta_salida}/{router['hostname']}.txt"
    
    # Guardar en disco
    with open(nombre_archivo, 'w') as f:
        f.write(configuracion_final)
        
    print(f"[EXITO] Archivo generado: {nombre_archivo}")

print("\n¡Proceso terminado exitosamente!")