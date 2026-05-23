import os
from jinja2 import Environment, FileSystemLoader

# =====================================================================
# 1. DEFINICIÓN DE DATOS (EL INVENTARIO DEL HUB: MASTER Y BACKUP)
# =====================================================================
lista_routers = [
    {
        # ==========================================
        # DATOS PARA HQ-MASTER (Ruta Principal)
        # ==========================================
        "hostname": "CPE-HQ",
        
        # --- SEGURIDAD IPSEC ---
        "clave_vpn": "CISCO",
        
        # --- TÚNEL DMVPN ---
        "id_tunnel": "0",
        "ip_tunnel_local": "172.16.30.1",
        "red_tunnel": "172.16.30.0",
        "net_id": "1",
        "key_id": "1",
        "lan1":"192.168.10.0",
        "lan2":"192.168.20.0",
        
    },
    {
        # ==========================================
        # DATOS PARA HQ-BK (Ruta de Respaldo)
        # ==========================================
        "hostname": "CPE-HQ-BK",
        
        # ---  SEGURIDAD IPSEC ---
        "clave_vpn": "CISCO",
            
        # ---  TÚNEL DMVPN ---
        "id_tunnel": "1",
        "net_id":"2",
        "ip_tunnel_local": "172.16.40.1", 
        "red_tunnel": "172.16.40.0",
        "key_id":"2",
        "lan1":"192.168.10.0",
        "lan2":"192.168.20.0",

    }
]

# =====================================================================
# 2. MOTOR DE GENERACIÓN (JINJA2)
# =====================================================================

# Configurar Jinja2 para que busque archivos en la carpeta actual
env = Environment(loader=FileSystemLoader('.'))

# Cargar la plantilla actualizadora
try:
    template = env.get_template('plantilla_hq.txt')
except Exception as e:
    print(f"Error al cargar la plantilla: {e}")
    exit()

# Crear una carpeta para guardar los resultados
carpeta_salida = "configuraciones"
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Generar la configuración adicional
print("[*] Generando scripts de actualización para el HQ...")
for router in lista_routers:
    configuracion_final = template.render(router)
    nombre_archivo = f"{carpeta_salida}/{router['hostname']}.txt"
    
    with open(nombre_archivo, 'w') as f:
        f.write(configuracion_final)
        
    print(f"[+] Archivo incremental generado exitosamente: {nombre_archivo}")

print("\n¡Listo! Configuraciones de Master y Backup generadas.")