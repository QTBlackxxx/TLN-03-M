# network_automation_suite.py
"""
AUTOMATIZACIÓN Y PROGRAMABILIDAD DE REDES - TLN03
Solución integrada para gestión de topología MPLS L3VPN

Autor: Antonio
Descripción: Script que automatiza tareas de operación de red
  - Opción A: Generar inventarios automáticamente
  - Opción B: Comparar configuraciones PRE vs POST
  - Opción C: Buscar comandos específicos
  - Opción D: Generar reportes en formato TXT (INTEGRADO)

FLUJO DEL SCRIPT:
  1. Genera inventario (OPCIÓN A)
  2. Captura PRE-despliegue (OPCIÓN B - FASE 1)
  3. Espera ejecución de playbooks Ansible
  4. Captura POST-despliegue y compara (OPCIÓN B - FASE 2)
  5. Busca comandos específicos (OPCIÓN C)
  6. Genera reporte integrado (OPCIÓN D)

SALIDA:
  - master_report.txt (en /Escritorio/.../reportes) - Reporte integrado completo
  - inventory_automatic.ini (en /Escritorio/.../inventory) - Inventario para Ansible

Uso:
    python network_automation_suite.py
"""

import yaml
from netmiko import ConnectHandler
from getpass import getpass
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# ============================================================
# DEFINICIÓN DE COLORES PARA TERMINAL
# ============================================================

class Colors:
    """Códigos de color ANSI para terminal"""
    # Colores básicos
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Colores brillantes
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Estilos
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    # Fondos
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'
    BG_BLUE = '\033[44m'
    BG_YELLOW = '\033[43m'
    BG_CYAN = '\033[46m'

def print_header(text: str):
    """Imprime encabezado en color"""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{'=' * 80}{Colors.RESET}\n")

def print_section(text: str):
    """Imprime sección en color"""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}[{text}]{Colors.RESET}")

def print_step(step: int, text: str):
    """Imprime paso en color"""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_YELLOW}[PASO {step}] {text}{Colors.RESET}")

def print_success(text: str):
    """Imprime mensaje de éxito en verde"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Imprime mensaje de error en rojo"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Imprime mensaje de advertencia en amarillo"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """Imprime información en azul"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_highlight(text: str):
    """Imprime texto destacado"""
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}{text}{Colors.RESET}")

def print_device(hostname: str, device_type: str, status: str = ""):
    """Imprime información de dispositivo"""
    if status == "OK":
        status_color = Colors.GREEN
        status_symbol = "✓"
    elif status == "ERROR":
        status_color = Colors.RED
        status_symbol = "✗"
    else:
        status_color = Colors.YELLOW
        status_symbol = "⚠"
    
    print(f"  {status_color}{status_symbol}{Colors.RESET} {Colors.CYAN}{hostname:30}{Colors.RESET} ({device_type})")

def print_box(title: str, content: str):
    """Imprime contenido en un cuadro"""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}┌{'─' * 78}┐{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│ {title:<76} │{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}├{'─' * 78}┤{Colors.RESET}")
    for line in content.split('\n'):
        print(f"{Colors.BRIGHT_CYAN}│ {line:<76} │{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}└{'─' * 78}┘{Colors.RESET}\n")

# ============================================================
# CONFIGURACIÓN Y LOGGING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Ruta de topología
TOPOLOGY_FILE = BASE_DIR.parent.parent / "Grupo02_PC3" / "MPLS-IOU.yml"

# Ruta de inventario automático (separado)
INVENTORY_DIR = Path.home() / "Escritorio/TLN-03-M/Grupo02_PC3/inventory"
INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

# Ruta de reporte maestro (en directorio reportes)
REPORTS_DIR = Path.home() / "Escritorio/TLN-03-M/Grupo02_PC3/reportes"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Ruta de reporte maestro
MASTER_REPORT_FILE = REPORTS_DIR / "master_report.txt"

# Archivo de inventario automático
INVENTORY_AUTOMATIC_FILE = INVENTORY_DIR / "inventory_automatic.ini"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Comandos a buscar por tipo de dispositivo
ROUTER_COMMANDS = [
    "router ospf",
    "router bgp",
    "mpls ip",
    "ip cef",
    "mpls ldp",
    "vrf"
]

SWITCH_COMMANDS = [
    "spanning-tree mode",
    "vlan",
    "switchport mode",
    "switchport access vlan",
    "switchport mode trunk"
]


# ============================================================
# CLASE: GESTOR DE TOPOLOGÍA
# ============================================================

class TopologyManager:
    """Gestiona la lectura y procesamiento de topología YAML"""
    
    def __init__(self, topology_file: str):
        self.topology_file = topology_file
        self.topology = None
        self.devices = []
        self.lab_name = None
        
    def load_topology(self) -> bool:
        """Carga la topología desde archivo YAML"""
        try:
            with open(self.topology_file, "r") as file:
                self.topology = yaml.safe_load(file)
            self.lab_name = self.topology["name"]
            logger.info(f"✓ Topología cargada: {self.lab_name}")
            print_success(f"Topología cargada: {self.lab_name}")
            return True
        except Exception as e:
            logger.error(f"✗ Error al cargar topología: {e}")
            print_error(f"Error al cargar topología: {e}")
            return False
    
    def get_devices(self, device_type: str = "all") -> List[Dict]:
        """
        Retorna lista de dispositivos desde la topología
        
        Args:
            device_type: "all", "cisco_iol", "linux"
        
        Returns:
            Lista de diccionarios con información de dispositivos
        """
        if not self.topology:
            logger.error("Topología no cargada")
            print_error("Topología no cargada")
            return []
        
        nodes = self.topology["topology"]["nodes"]
        devices = []
        
        for node_name, node_data in nodes.items():
            if device_type == "all" or node_data.get("kind") == device_type:
                device_info = {
                    "name": node_name,
                    "hostname": f"clab-{self.lab_name}-{node_name}",
                    "kind": node_data.get("kind"),
                    "image": node_data.get("image", "N/A"),
                    "type": node_data.get("type", "router")
                }
                devices.append(device_info)
        
        # Ordenar alfabéticamente
        devices.sort(key=lambda d: d["hostname"])
        return devices
    
    def get_cisco_devices(self) -> List[Dict]:
        """Retorna solo dispositivos Cisco IOS con tipo especificado"""
        devices = self.get_devices("cisco_iol")
        for dev in devices:
            if dev["type"] == "l2":
                dev["device_type"] = "switch"
            else:
                dev["device_type"] = "router"
        return devices


# ============================================================
# CLASE: CONECTOR DE DISPOSITIVOS
# ============================================================

class DeviceConnector:
    """Gestiona conexiones SSH a dispositivos de red"""
    
    def __init__(self, username: str, password: str, timeout: int = 10):
        self.username = username
        self.password = password
        self.timeout = timeout
    
    def connect(self, hostname: str, device_type: str = "cisco_ios") -> Optional[ConnectHandler]:
        """
        Establece conexión con un dispositivo
        
        Args:
            hostname: IP o nombre del dispositivo
            device_type: Tipo de dispositivo (cisco_ios por defecto)
        
        Returns:
            Objeto ConnectHandler o None si falla
        """
        try:
            connection = ConnectHandler(
                device_type=device_type,
                host=hostname,
                username=self.username,
                password=self.password,
                timeout=self.timeout
            )
            logger.info(f"✓ Conectado a {hostname}")
            print_device(hostname, device_type, "OK")
            return connection
        except Exception as e:
            logger.error(f"✗ Error conectando a {hostname}: {str(e)}")
            print_device(hostname, device_type, "ERROR")
            return None
    
    def get_running_config(self, connection: ConnectHandler) -> Optional[str]:
        """Obtiene running-config del dispositivo"""
        try:
            config = connection.send_command("show running-config")
            return config
        except Exception as e:
            logger.error(f"Error obteniendo config: {e}")
            return None
    
    def disconnect(self, connection: ConnectHandler):
        """Cierra conexión con dispositivo"""
        try:
            connection.disconnect()
        except Exception as e:
            logger.error(f"Error desconectando: {e}")


# ============================================================
# CLASE: ANALIZADOR DE CONFIGURACIONES
# ============================================================

class ConfigAnalyzer:
    """Analiza y compara configuraciones de dispositivos"""
    
    @staticmethod
    def compare_configs(pre_config: str, post_config: str) -> Dict:
        """
        Compara dos configuraciones
        
        Args:
            pre_config: Configuración previa
            post_config: Configuración posterior
        
        Returns:
            Diccionario con líneas agregadas/removidas
        """
        pre_lines = set(pre_config.split("\n"))
        post_lines = set(post_config.split("\n"))
        
        added_lines = sorted(post_lines - pre_lines)
        removed_lines = sorted(pre_lines - post_lines)
        
        # Filtrar líneas vacías y comentarios
        added_lines = [l.strip() for l in added_lines 
                      if l.strip() and not l.startswith("!")]
        removed_lines = [l.strip() for l in removed_lines 
                        if l.strip() and not l.startswith("!")]
        
        return {
            "added": added_lines,
            "removed": removed_lines,
            "total_changes": len(added_lines) + len(removed_lines),
            "pre_lines": len(pre_lines),
            "post_lines": len(post_lines)
        }
    
    @staticmethod
    def search_commands(config: str, commands: List[str]) -> Dict:
        """
        Busca comandos específicos en configuración
        
        Args:
            config: Contenido de running-config
            commands: Lista de comandos a buscar
        
        Returns:
            Diccionario con resultados de búsqueda
        """
        results = {
            "found": [],
            "not_found": [],
            "total_found": 0
        }
        
        for command in commands:
            if command in config:
                results["found"].append(command)
                results["total_found"] += 1
            else:
                results["not_found"].append(command)
        
        return results


# ============================================================
# CLASE: GENERADOR DE REPORTES
# ============================================================

class ReportGenerator:
    """Genera reportes en formato TXT"""
    
    def __init__(self, master_report_file: Path):
        self.master_report = master_report_file
        self.report_content = []
    
    def add_section(self, title: str, content: str = "", separator: str = "="):
        """Agrega una sección al reporte"""
        self.report_content.append(f"{separator * 80}")
        self.report_content.append(title)
        self.report_content.append(f"{separator * 80}")
        if content:
            self.report_content.append(content)
        self.report_content.append("")
    
    def add_subsection(self, title: str, separator: str = "-"):
        """Agrega una subsección"""
        self.report_content.append(f"{separator * 80}")
        self.report_content.append(title)
        self.report_content.append(f"{separator * 80}")
        self.report_content.append("")
    
    def add_content(self, content: str):
        """Agrega contenido al reporte"""
        self.report_content.append(content)
        self.report_content.append("")
    
    def generate_inventory_section(self, devices: List[Dict]) -> str:
        """Genera sección de inventario"""
        content = []
        content.append(f"Total de dispositivos: {len(devices)}\n")
        
        content.append("LISTADO DE DISPOSITIVOS:")
        content.append("-" * 80)
        
        routers = [d for d in devices if d.get("device_type") == "router"]
        switches = [d for d in devices if d.get("device_type") == "switch"]
        
        content.append(f"\nROUTERS ({len(routers)}):")
        for router in routers:
            content.append(f"  • {router['hostname']:30} | Imagen: {router['image']}")
        
        content.append(f"\nSWITCHES ({len(switches)}):")
        for switch in switches:
            content.append(f"  • {switch['hostname']:30} | Imagen: {switch['image']}")
        
        return "\n".join(content)
    
    def save_master_report(self):
        """Guarda el reporte maestro"""
        try:
            with open(self.master_report, "w") as f:
                f.write("\n".join(self.report_content))
            logger.info(f"✓ Reporte maestro guardado: {self.master_report}")
            print_success(f"Reporte maestro guardado")
            return True
        except Exception as e:
            logger.error(f"✗ Error guardando reporte: {e}")
            print_error(f"Error guardando reporte: {e}")
            return False


# ============================================================
# FUNCIÓN: GENERAR INVENTARIO AUTOMÁTICO
# ============================================================

def generate_inventory_automatic(devices: List[Dict]) -> bool:
    """
    Genera archivo inventory_automatic.ini en formato Ansible
    """
    try:
        with open(INVENTORY_AUTOMATIC_FILE, "w") as inv:
            inv.write("[network_devices]\n")
            
            for device in devices:
                inv.write(f"{device['hostname']}\n")
            
            inv.write("\n[network_devices:vars]\n")
            inv.write("ansible_user=admin\n")
            inv.write("ansible_password=admin\n")
            inv.write("ansible_network_os=cisco.ios.ios\n")
            inv.write("ansible_connection=ansible.netcommon.network_cli\n")
            inv.write("ansible_paramiko_look_for_keys=False\n")
        
        logger.info(f"✓ Inventario automático generado: {INVENTORY_AUTOMATIC_FILE}")
        print_success(f"Inventario automático generado")
        return True
    except Exception as e:
        logger.error(f"✗ Error generando inventario: {e}")
        print_error(f"Error generando inventario: {e}")
        return False


# ============================================================
# OPCIÓN A: GENERAR INVENTARIO
# ============================================================

def option_a_generate_inventory(topology_manager: TopologyManager) -> List[Dict]:
    """
    OPCIÓN A: Genera inventario automáticamente desde topología
    """
    print_section("OPCIÓN A: GENERAR INVENTARIO AUTOMÁTICAMENTE")
    
    try:
        devices = topology_manager.get_cisco_devices()
        
        # Generar inventario Ansible
        if not generate_inventory_automatic(devices):
            return []
        
        print(f"\n{Colors.BRIGHT_YELLOW}Dispositivos encontrados: {len(devices)}{Colors.RESET}\n")
        
        routers = [d for d in devices if d.get("device_type") == "router"]
        switches = [d for d in devices if d.get("device_type") == "switch"]
        
        print(f"{Colors.BRIGHT_CYAN}ROUTERS ({len(routers)}):{Colors.RESET}")
        for router in routers:
            print_device(router['hostname'], router['device_type'])
        
        print(f"\n{Colors.BRIGHT_CYAN}SWITCHES ({len(switches)}):{Colors.RESET}")
        for switch in switches:
            print_device(switch['hostname'], switch['device_type'])
        
        return devices
        
    except Exception as e:
        print_error(f"{e}")
        return []


# ============================================================
# OPCIÓN B - FASE 1: CAPTURA PRE-DESPLIEGUE
# ============================================================

def option_b_phase1_capture_pre(devices: List[Dict], 
                               connector: DeviceConnector) -> Dict:
    """
    OPCIÓN B - FASE 1: Captura configuraciones PRE-despliegue
    """
    print_section("OPCIÓN B - FASE 1: CAPTURA PRE-DESPLIEGUE")
    
    pre_configs = {}
    
    for device in devices:
        hostname = device["hostname"]
        
        connection = connector.connect(hostname)
        if connection:
            config = connector.get_running_config(connection)
            connector.disconnect(connection)
            
            if config:
                pre_configs[hostname] = {
                    "timestamp": datetime.now().isoformat(),
                    "running_config": config,
                    "status": "OK"
                }
            else:
                pre_configs[hostname] = {
                    "timestamp": datetime.now().isoformat(),
                    "running_config": None,
                    "status": "ERROR: No se pudo obtener config"
                }
        else:
            pre_configs[hostname] = {
                "timestamp": datetime.now().isoformat(),
                "running_config": None,
                "status": "ERROR: Conexión fallida"
            }
    
    print(f"\n{Colors.GREEN}✓ Configuraciones PRE capturadas en memoria{Colors.RESET}\n")
    return pre_configs


# ============================================================
# OPCIÓN B - FASE 2: CAPTURA Y COMPARACIÓN POST-DESPLIEGUE
# ============================================================

def option_b_phase2_capture_and_compare(devices: List[Dict],
                                       connector: DeviceConnector,
                                       pre_configs: Dict,
                                       analyzer: ConfigAnalyzer) -> Dict:
    """
    OPCIÓN B - FASE 2: Captura configuraciones POST-despliegue y compara
    """
    print_section("OPCIÓN B - FASE 2: CAPTURA POST-DESPLIEGUE Y COMPARACIÓN")
    
    post_configs = {}
    
    print(f"{Colors.BRIGHT_CYAN}Capturando configuraciones POST...{Colors.RESET}\n")
    
    for device in devices:
        hostname = device["hostname"]
        
        connection = connector.connect(hostname)
        if connection:
            config = connector.get_running_config(connection)
            connector.disconnect(connection)
            
            if config:
                post_configs[hostname] = {
                    "timestamp": datetime.now().isoformat(),
                    "running_config": config,
                    "status": "OK"
                }
            else:
                post_configs[hostname] = {
                    "timestamp": datetime.now().isoformat(),
                    "running_config": None,
                    "status": "ERROR: No se pudo obtener config"
                }
        else:
            post_configs[hostname] = {
                "timestamp": datetime.now().isoformat(),
                "running_config": None,
                "status": "ERROR: Conexión fallida"
            }
    
    print(f"\n{Colors.GREEN}✓ Configuraciones POST capturadas en memoria{Colors.RESET}\n")
    
    # ========== COMPARACIÓN ==========
    print(f"{Colors.BRIGHT_CYAN}Analizando diferencias entre PRE y POST...{Colors.RESET}\n")
    
    comparison_results = {}
    
    for device in devices:
        hostname = device["hostname"]
        
        pre_config = pre_configs.get(hostname, {}).get("running_config", "")
        post_config = post_configs.get(hostname, {}).get("running_config", "")
        pre_status = pre_configs.get(hostname, {}).get("status", "UNKNOWN")
        post_status = post_configs.get(hostname, {}).get("status", "UNKNOWN")
        
        if pre_status != "OK" or post_status != "OK":
            comparison_results[hostname] = {
                "status": "ERROR",
                "pre_status": pre_status,
                "post_status": post_status,
                "comparison": None
            }
            print_device(hostname, "N/A", "ERROR")
            continue
        
        comparison = analyzer.compare_configs(pre_config, post_config)
        comparison_results[hostname] = {
            "status": "OK",
            "pre_status": pre_status,
            "post_status": post_status,
            "comparison": comparison
        }
        
        changes_text = f"{comparison['total_changes']} cambios"
        print(f"  {Colors.GREEN}✓{Colors.RESET} {Colors.CYAN}{hostname:30}{Colors.RESET} - {Colors.YELLOW}{changes_text}{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}✓ Análisis de comparación completado{Colors.RESET}\n")
    return comparison_results


# ============================================================
# OPCIÓN C: BUSCAR COMANDOS ESPECÍFICOS
# ============================================================

def option_c_search_commands(devices: List[Dict],
                            post_configs: Dict,
                            analyzer: ConfigAnalyzer) -> Dict:
    """
    OPCIÓN C: Busca comandos específicos en configuraciones POST-despliegue
    """
    print_section("OPCIÓN C: BUSCAR COMANDOS ESPECÍFICOS")
    
    search_results = {}
    
    print(f"{Colors.BRIGHT_CYAN}Buscando comandos en configuraciones...{Colors.RESET}\n")
    
    for device in devices:
        hostname = device["hostname"]
        device_type = device["device_type"]
        
        config = post_configs.get(hostname, {}).get("running_config", "")
        config_status = post_configs.get(hostname, {}).get("status", "UNKNOWN")
        
        if config_status != "OK" or not config:
            search_results[hostname] = {
                "device_type": device_type,
                "status": "ERROR",
                "search": None
            }
            print_device(hostname, device_type, "ERROR")
            continue
        
        # Seleccionar comandos según tipo de dispositivo
        commands = ROUTER_COMMANDS if device_type == "router" else SWITCH_COMMANDS
        
        search = analyzer.search_commands(config, commands)
        search_results[hostname] = {
            "device_type": device_type,
            "status": "OK",
            "search": search
        }
        
        found_text = f"{search['total_found']}/{len(commands)} comandos"
        print(f"  {Colors.GREEN}✓{Colors.RESET} {Colors.CYAN}{hostname:30}{Colors.RESET} ({device_type}) - {Colors.YELLOW}{found_text}{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}✓ Búsqueda de comandos completada{Colors.RESET}\n")
    return search_results


# ============================================================
# OPCIÓN D: GENERAR REPORTE INTEGRADO EN TXT
# ============================================================

def option_d_generate_integrated_report(devices: List[Dict],
                                       comparison_results: Dict,
                                       search_results: Dict) -> str:
    """
    OPCIÓN D: Genera reporte integrado en TXT
    """
    print_section("OPCIÓN D: GENERAR REPORTE INTEGRADO EN TXT")
    
    report_gen = ReportGenerator(MASTER_REPORT_FILE)
    
    # ========== ENCABEZADO GENERAL ==========
    report_gen.add_section(
        "LABORATORIO DE AUTOMATIZACIÓN Y PROGRAMABILIDAD DE REDES - TLN03",
        f"Reporte Integrado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    # ========== SECCIÓN 1: INVENTARIO ==========
    print(f"{Colors.BRIGHT_CYAN}Generando sección de Inventario...{Colors.RESET}")
    inventory_content = report_gen.generate_inventory_section(devices)
    report_gen.add_section("1. INVENTARIO DE DISPOSITIVOS", inventory_content)
    
    routers = [d for d in devices if d.get("device_type") == "router"]
    switches = [d for d in devices if d.get("device_type") == "switch"]
    
    stats = []
    stats.append(f"Total de dispositivos: {len(devices)}")
    stats.append(f"Routers: {len(routers)}")
    stats.append(f"Switches: {len(switches)}")
    stats.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    report_gen.add_section("1.1. ESTADÍSTICAS GENERALES", "\n".join(stats))
    
    # ========== SECCIÓN 2: COMPARACIÓN PRE vs POST ==========
    if comparison_results:
        print(f"{Colors.BRIGHT_CYAN}Generando sección de Comparación PRE vs POST...{Colors.RESET}")
        
        total_changes = sum(
            r.get("comparison", {}).get("total_changes", 0) 
            for r in comparison_results.values() 
            if r["status"] == "OK"
        )
        
        report_gen.add_section(
            "2. COMPARACIÓN DE CONFIGURACIONES PRE vs POST DESPLIEGUE",
            f"Dispositivos analizados: {len(comparison_results)}\nTotal de cambios: {total_changes}"
        )
        
        for hostname, result in sorted(comparison_results.items()):
            report_gen.add_subsection(f"Dispositivo: {hostname}")
            
            content = []
            content.append(f"Estado Pre-Despliegue: {result['pre_status']}")
            content.append(f"Estado Post-Despliegue: {result['post_status']}")
            
            if result["status"] == "ERROR":
                content.append("Estado General: ERROR - No se pudieron capturar configuraciones")
            else:
                comparison = result["comparison"]
                content.append(f"Líneas Pre-Despliegue: {comparison['pre_lines']}")
                content.append(f"Líneas Post-Despliegue: {comparison['post_lines']}")
                content.append(f"Total de cambios: {comparison['total_changes']}\n")
                
                if comparison["added"]:
                    content.append("LÍNEAS AGREGADAS:")
                    for line in comparison["added"][:30]:
                        content.append(f"  + {line}")
                    if len(comparison["added"]) > 30:
                        content.append(f"  ... y {len(comparison['added']) - 30} líneas más")
                else:
                    content.append("LÍNEAS AGREGADAS: Ninguna")
                
                content.append("")
                
                if comparison["removed"]:
                    content.append("LÍNEAS REMOVIDAS:")
                    for line in comparison["removed"][:30]:
                        content.append(f"  - {line}")
                    if len(comparison["removed"]) > 30:
                        content.append(f"  ... y {len(comparison['removed']) - 30} líneas más")
                else:
                    content.append("LÍNEAS REMOVIDAS: Ninguna")
            
            report_gen.add_content("\n".join(content))
    
    # ========== SECCIÓN 3: BÚSQUEDA DE COMANDOS ==========
    if search_results:
        print(f"{Colors.BRIGHT_CYAN}Generando sección de Búsqueda de Comandos...{Colors.RESET}")
        
        total_found = sum(
            r.get("search", {}).get("total_found", 0) 
            for r in search_results.values() 
            if r["status"] == "OK"
        )
        
        report_gen.add_section(
            "3. BÚSQUEDA DE COMANDOS ESPECÍFICOS",
            f"Dispositivos analizados: {len(search_results)}\nTotal de comandos encontrados: {total_found}"
        )
        
        for hostname, result in sorted(search_results.items()):
            report_gen.add_subsection(f"Dispositivo: {hostname} ({result['device_type']})")
            
            content = []
            
            if result["status"] == "ERROR":
                content.append("Estado: ERROR - No se pudo acceder a la configuración")
            else:
                search = result["search"]
                total_commands = len(search["found"]) + len(search["not_found"])
                
                content.append(f"Total de comandos buscados: {total_commands}")
                content.append(f"Comandos encontrados: {search['total_found']}")
                content.append(f"Comandos no encontrados: {len(search['not_found'])}\n")
                
                if search["found"]:
                    content.append("COMANDOS ENCONTRADOS [OK]:")
                    for cmd in search["found"]:
                        content.append(f"  ✓ {cmd}")
                else:
                    content.append("COMANDOS ENCONTRADOS [OK]: Ninguno")
                
                content.append("")
                
                if search["not_found"]:
                    content.append("COMANDOS NO ENCONTRADOS [X]:")
                    for cmd in search["not_found"]:
                        content.append(f"  ✗ {cmd}")
                else:
                    content.append("COMANDOS NO ENCONTRADOS [X]: Ninguno")
            
            report_gen.add_content("\n".join(content))
    
    # ========== SECCIÓN 4: RESUMEN FINAL ==========
    print(f"{Colors.BRIGHT_CYAN}Generando sección de Resumen Final...{Colors.RESET}")
    
    summary = []
    summary.append(f"Fecha y hora de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append(f"Total de dispositivos procesados: {len(devices)}")
    summary.append(f"Topología utilizada: {TOPOLOGY_FILE}")
    summary.append("")
    summary.append("ARCHIVOS GENERADOS:")
    summary.append(f"  1. {MASTER_REPORT_FILE.name}")
    summary.append(f"     Ubicación: {MASTER_REPORT_FILE}")
    summary.append(f"     Contenido: Reporte integrado completo (Inventario + Comparaciones + Búsquedas)")
    summary.append("")
    summary.append(f"  2. {INVENTORY_AUTOMATIC_FILE.name}")
    summary.append(f"     Ubicación: {INVENTORY_AUTOMATIC_FILE}")
    summary.append(f"     Contenido: Inventario automático en formato Ansible .ini")
    summary.append("")
    summary.append("PRÓXIMOS PASOS:")
    summary.append("  • Revisar este reporte completo")
    summary.append("  • Validar los cambios aplicados con NAPALM")
    summary.append("  • Ejecutar playbooks de validación")
    summary.append("  • Documentar resultados en presentación")
    
    report_gen.add_section("4. RESUMEN FINAL Y EVIDENCIAS", "\n".join(summary))
    
    # Guardar reporte
    report_gen.save_master_report()
    
    return str(MASTER_REPORT_FILE)


# ============================================================
# FUNCIÓN PRINCIPAL - ORQUESTADOR
# ============================================================

def main():
    """Orquesta el flujo completo del script"""
    
    # Banner principal
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "AUTOMATIZACIÓN Y PROGRAMABILIDAD DE REDES - LABORATORIO MPLS L3VPN".center(78) + "║")
    print("║" + "SUITE DE AUTOMATIZACIÓN INTEGRADA - OPCIÓN D (REPORTE TXT)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print(f"{Colors.RESET}\n")
    
    # ========== PASO 0: Cargar topología ==========
    print_step(0, "Cargando topología YAML")
    print(f"{Colors.BLUE}  Ruta: {TOPOLOGY_FILE}{Colors.RESET}\n")
    
    topology_manager = TopologyManager(str(TOPOLOGY_FILE))
    if not topology_manager.load_topology():
        print_error("Abortando debido a error en topología")
        return
    
    # ========== PASO 1: OPCIÓN A - Generar Inventario ==========
    print_step(1, "Ejecutando OPCIÓN A")
    devices = option_a_generate_inventory(topology_manager)
    
    if not devices:
        print_error("No se encontraron dispositivos")
        return
    
    # ========== PASO 2: Obtener credenciales ==========
    print_step(2, "Configurando credenciales SSH")
    print(f"{Colors.BRIGHT_YELLOW}[CREDENCIALES] Ingrese credenciales SSH para conectarse a dispositivos:{Colors.RESET}")
    username = input(f"{Colors.BLUE}  Usuario SSH: {Colors.RESET}")
    password = getpass(f"{Colors.BLUE}  Contraseña SSH: {Colors.RESET}")
    print()
    
    connector = DeviceConnector(username, password)
    analyzer = ConfigAnalyzer()
    
    # ========== PASO 3: OPCIÓN B - FASE 1 - Capturar PRE ==========
    print_step(3, "Ejecutando OPCIÓN B - FASE 1")
    pre_configs = option_b_phase1_capture_pre(devices, connector)
    
    # ========== PASO 4: PAUSA - Esperar playbooks Ansible ==========
    print_header("⚠  PAUSA: EJECUTAR PLAYBOOKS DE ANSIBLE")
    
    print(f"{Colors.BRIGHT_YELLOW}Ahora debe ejecutar los playbooks de Ansible de sus compañeros:{Colors.RESET}\n")
    print(f"  {Colors.BRIGHT_CYAN}• interfaces.yml{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}• ospf.yml{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}• mpls.yml{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}• bgp.yml{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}• vpn.yml{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}Puede usar el inventario generado en:{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}{INVENTORY_AUTOMATIC_FILE}{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}Ejemplo:{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}ansible-playbook -i {INVENTORY_AUTOMATIC_FILE} playbooks/interfaces.yml{Colors.RESET}")
    
    input(f"\n{Colors.BRIGHT_YELLOW}➤ Presione ENTER una vez que haya ejecutado TODOS los playbooks...{Colors.RESET}")
    print()
    
    # ========== PASO 5: OPCIÓN B - FASE 2 - Capturar POST y Comparar ==========
    print_step(5, "Ejecutando OPCIÓN B - FASE 2")
    comparison_results = option_b_phase2_capture_and_compare(
        devices, connector, pre_configs, analyzer
    )
    
    # ========== PASO 6: OPCIÓN C - Buscar comandos ==========
    print_step(6, "Ejecutando OPCIÓN C")
    search_results = option_c_search_commands(devices, pre_configs, analyzer)
    
    # ========== PASO 7: OPCIÓN D - Generar Reporte Integrado ==========
    print_step(7, "Ejecutando OPCIÓN D")
    master_report = option_d_generate_integrated_report(
        devices,
        comparison_results,
        search_results
    )
    
    # ========== RESUMEN FINAL ==========
    print_header("✓ PROCESO COMPLETADO EXITOSAMENTE")
    
    print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}ARCHIVOS GENERADOS:{Colors.RESET}\n")
    
    print(f"{Colors.BRIGHT_CYAN}📄 REPORTE INTEGRADO:{Colors.RESET}")
    print(f"   {Colors.BLUE}Ubicación:{Colors.RESET} {MASTER_REPORT_FILE}")
    print(f"   {Colors.BLUE}Contenido:{Colors.RESET} Inventario + Comparación PRE/POST + Búsqueda de comandos\n")
    
    print(f"{Colors.BRIGHT_CYAN}📋 INVENTARIO AUTOMÁTICO:{Colors.RESET}")
    print(f"   {Colors.BLUE}Ubicación:{Colors.RESET} {INVENTORY_AUTOMATIC_FILE}")
    print(f"   {Colors.BLUE}Formato:{Colors.RESET} .ini (compatible con Ansible)\n")
    
    print(f"{Colors.BRIGHT_YELLOW}📊 PRÓXIMOS PASOS:{Colors.RESET}")
    print(f"   {Colors.CYAN}• Revisar el reporte: {MASTER_REPORT_FILE}{Colors.RESET}")
    print(f"   {Colors.CYAN}• Usar inventario para ejecutar playbooks{Colors.RESET}")
    print(f"   {Colors.CYAN}• Validar con NAPALM{Colors.RESET}")
    print(f"   {Colors.CYAN}• Incluir en la presentación{Colors.RESET}")
    print(f"\n{Colors.RESET}")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}✗ Proceso interrumpido por el usuario{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Error inesperado: {e}{Colors.RESET}")
        logger.exception("Excepción no manejada")
        sys.exit(1)
