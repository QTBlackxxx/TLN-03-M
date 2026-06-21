"""
Módulo central: Inventario, credenciales, conexión y utilidades compartidas.
"""
from napalm import get_network_driver
from contextlib import contextmanager
import time
import socket

# ==========================================
# INVENTARIO Y CREDENCIALES
# ==========================================
INVENTORY = {
    "P1": {"ip": "clab-MPLS-P1", "type": "router"}, 
    "P2": {"ip": "clab-MPLS-P2", "type": "router"},
    "PE1": {"ip": "clab-MPLS-PE1", "type": "router"}, 
    "PE2": {"ip": "clab-MPLS-PE2", "type": "router"},
    "RR1": {"ip": "clab-MPLS-RR1", "type": "router"}, 
    "RR2": {"ip": "clab-MPLS-RR2", "type": "router"},
    "CPE-1": {"ip": "clab-MPLS-CPE-1", "type": "router", "platform": "ios"}, 
    "CPE-2": {"ip": "clab-MPLS-CPE-2", "type": "router", "platform": "ios"},
    "SW-1": {"ip": "clab-MPLS-SW-1", "type": "switch_l2"}, 
    "SW-2": {"ip": "clab-MPLS-SW-2", "type": "switch_l2"},
    "SW-LAN-1": {"ip": "clab-MPLS-SW-LAN-1", "type": "switch_l2"}, 
    "SW-LAN-2": {"ip": "clab-MPLS-SW-LAN-2", "type": "switch_l2"},
}

CREDS = {"username": "admin", "password": "admin", "platform": "ios"}

NAPALM_OPTIONS = {
    'secret': CREDS['password'],
    'dest_file_system': 'flash:',
    'global_delay_factor': 5,
    'fast_cli': False,
    'timeout': 60,
    'session_timeout': 60,
    'auth_timeout': 60,
    'banner_timeout': 60
}

# ==========================================
# UTILIDADES COMPARTIDAS
# ==========================================
def wait_for_ssh(ip, port=22, timeout=15):
    """Espera a que el puerto SSH esté disponible."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                if sock.connect_ex((ip, port)) == 0:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

@contextmanager
def napalm_session(name, info):
    """
    Context Manager: Abre la sesión NAPALM y garantiza el cierre automático.
    Uso: with napalm_session(name, info) as device: ...
    """
    platform = info.get('platform', CREDS['platform'])
    driver = get_network_driver(platform)
    device = driver(
        hostname=info['ip'],
        username=CREDS['username'],
        password=CREDS['password'],
        optional_args=NAPALM_OPTIONS
    )
    try:
        device.open()
        yield device
    finally:
        try:
            device.close()
        except Exception:
            pass

def format_uptime(seconds):
    """Convierte segundos de uptime a formato legible."""
    if not isinstance(seconds, (int, float)):
        return "N/A"
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}d {hours}h {minutes}m"