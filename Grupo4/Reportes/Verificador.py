from napalm import get_network_driver
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align

console = Console()

# 1. DICCIONARIO DE INVENTARIO
inventario_ips = {
    "PE1": "clab-MPLS-PE1",
    "PE2": "clab-MPLS-PE2",
    "P1":  "clab-MPLS-P1",
    "P2":  "clab-MPLS-P2",
    "RR1": "clab-MPLS-RR1",
    "RR2": "clab-MPLS-RR2",
    "CPE-1": "clab-MPLS-CPE-1",
    "CPE-2": "clab-MPLS-CPE-2",
}

console.print("\n[bold cyan]--- Dashboard de Validación Integral MPLS L3VPN ---[/bold cyan]")
equipo_elegido = Prompt.ask(
    "Seleccione el dispositivo a auditar",
    choices=list(inventario_ips.keys()),
    default="PE1"
)
ip_objetivo = inventario_ips[equipo_elegido]

destino_ruta = Prompt.ask(
    "Ingresar una ruta para ser filtrada (ej. 10.0.0.0, o deje en blanco para omitir)",
    default=""
)

console.print(f"\n[yellow]Extrayendo información de {equipo_elegido} ({ip_objetivo})...[/yellow]")

driver = get_network_driver('ios')
dispositivo = driver(ip_objetivo, 'admin', 'admin')

try:
    dispositivo.open()
    
    # Comandos NAPALM estructurados:
    facts = dispositivo.get_facts()
    interfaces = dispositivo.get_interfaces()
    interfaces_ip = dispositivo.get_interfaces_ip()
    bgp_neighbors = dispositivo.get_bgp_neighbors()
    
    # Comandos CLI
    comandos_raw = dispositivo.cli(['show ip ospf neighbor', 'show ip route'])
    
    # Rutas (búsqueda específica):
    rutas = {}
    if destino_ruta:
        try:
            rutas = dispositivo.get_route_to(destination=destino_ruta)
        except Exception:
            rutas = {"Error": "No se encontró la ruta o el protocolo no está soportado."}
            
    try:
        entorno = dispositivo.get_environment()
    except:
        entorno = {}
        
    dispositivo.close()

    # Procesamiento de información y visualización:
    interfaces_activas = sum(1 for nombre, datos in interfaces.items() if datos.get('is_up'))
    estado_general = "[bold green]OK[/bold green]" if interfaces_activas > 0 else "[bold red]CRITICAL[/bold red]"

    # 1. Panel de resumen:
    texto_resumen = (
        f"[bold white]Router:[/bold white] {equipo_elegido} ({facts.get('model', 'N/A')})\n"
        f"[bold white]Hostname:[/bold white] {facts.get('hostname', equipo_elegido)}\n"
        f"[bold white]Interfaces activas:[/bold white] [green]{interfaces_activas}[/green] de {len(interfaces)}\n"
        f"[bold white]Estado Operativo:[/bold white] {estado_general}"
    )
    console.print("\n", Panel(Align.center(texto_resumen), title="[bold cyan]1. Información General (get_facts)[/bold cyan]", border_style="cyan"))

    # 2. Tabla de direccionamiento IP:
    tabla_ip = Table(title="2. Direccionamiento IP (get_interfaces_ip)", title_style="bold green", expand=True)
    tabla_ip.add_column("Interfaz", style="bold white")
    tabla_ip.add_column("IPv4", style="cyan")
    tabla_ip.add_column("Máscara (CIDR)", justify="center")
    tabla_ip.add_column("IPv6", style="magenta")

    for intf, datos_ip in interfaces_ip.items():
        ipv4_lista = [f"{ip}" for ip, data in datos_ip.get('ipv4', {}).items()]
        ipv4_cidr = [str(data.get('prefix_length')) for ip, data in datos_ip.get('ipv4', {}).items()]
        ipv6_lista = [f"{ip}/{data.get('prefix_length')}" for ip, data in datos_ip.get('ipv6', {}).items()]
        
        str_ipv4 = "\n".join(ipv4_lista) if ipv4_lista else "Sin IPv4"
        str_cidr = "\n".join(ipv4_cidr) if ipv4_cidr else "-"
        str_ipv6 = "\n".join(ipv6_lista) if ipv6_lista else "Sin IPv6"
        
        tabla_ip.add_row(intf, str_ipv4, f"/{str_cidr}", str_ipv6)
    console.print(tabla_ip)

    # 3. Tabla de vecinos BGP:
    tabla_bgp = Table(title="3. Sesiones BGP (get_bgp_neighbors)", title_style="bold magenta", expand=True)
    tabla_bgp.add_column("VRF", style="dim")
    tabla_bgp.add_column("Peer IP", style="bold white")
    tabla_bgp.add_column("AS Remoto", justify="center")
    tabla_bgp.add_column("Estado", justify="center")

    if bgp_neighbors:
        for vrf, datos_vrf in bgp_neighbors.items():
            for peer_ip, peer_data in datos_vrf.get('peers', {}).items():
                estado = "[bold green]UP[/bold green]" if peer_data.get('is_up') else "[bold red]DOWN[/bold red]"
                tabla_bgp.add_row(vrf, peer_ip, str(peer_data.get('remote_as', '-')), estado)
    else:
        tabla_bgp.add_row("-", "Sin BGP configurado", "-", "-")
    console.print("\n", tabla_bgp)

    # 4. Tabla de rutas (Búsqueda específica):
    if destino_ruta:
        tabla_rutas = Table(title=f"4. Tabla de Rutas hacia: {destino_ruta} (get_route_to)", title_style="bold yellow", expand=True)
        tabla_rutas.add_column("Protocolo", style="bold white")
        tabla_rutas.add_column("Preferencia (AD)", justify="center")
        tabla_rutas.add_column("Siguiente Salto (Next-Hop)", style="cyan")
        tabla_rutas.add_column("Interfaz de salida", style="magenta")

        if "Error" not in rutas and rutas:
            for prefijo, detalles_rutas in rutas.items():
                for camino in detalles_rutas:
                    tabla_rutas.add_row(
                        str(camino.get('protocol', 'N/A')),
                        str(camino.get('preference', 'N/A')),
                        str(camino.get('next_hop', 'N/A')),
                        str(camino.get('outgoing_interface', 'N/A'))
                    )
        else:
            tabla_rutas.add_row("-", "No se encontró ruta", "-", "-")
        console.print("\n", tabla_rutas)

    # 5. Estado de hardware
    tabla_env = Table(title="5. Estado de Hardware (get_environment)", title_style="bold blue", expand=True)
    tabla_env.add_column("Componente", style="bold white")
    tabla_env.add_column("Estado / Uso", justify="center")

    if entorno:
        cpu = entorno.get('cpu', {})
        memoria = entorno.get('memory', {})
        uso_cpu = sum(core.get('%usage', 0) for core in cpu.values()) / len(cpu) if cpu else 0
        ram_libre = memoria.get('available_ram', 0) / 1024 / 1024
        
        tabla_env.add_row("CPU Global", f"{uso_cpu:.1f}% Uso")
        tabla_env.add_row("Memoria RAM", f"{ram_libre:.1f} MB Disponibles")
    else:
        tabla_env.add_row("Sensores", "No soportados por este dispositivo virtual (IOL/vIOS)")
    console.print("\n", tabla_env)

    # 6. Tabla de OSPF
    tabla_ospf = Table(title="6. Vecindades OSPF (CLI crudo de NAPALM)", title_style="bold orange1", expand=True)
    tabla_ospf.add_column("Salida del comando 'show ip ospf neighbor'", style="green")
    
    resultado_ospf = comandos_raw.get('show ip ospf neighbor', '')
    
    if not resultado_ospf.strip():
        tabla_ospf.add_row("Sin procesos OSPF activos o sin vecinos configurados.")
    else:
        tabla_ospf.add_row(resultado_ospf)
        
    console.print("\n", tabla_ospf)
    
    # 7. Tabla de Enrutamiento Completa
    tabla_rutas_completa = Table(title="7. Tabla de Enrutamiento Completa (show ip route)", title_style="bold green", expand=True)
    tabla_rutas_completa.add_column("Salida del comando 'show ip route'", style="white")
    
    resultado_rutas = comandos_raw.get('show ip route', '')
    
    if not resultado_rutas.strip():
        tabla_rutas_completa.add_row("Tabla de rutas vacía.")
    else:
        tabla_rutas_completa.add_row(resultado_rutas)
        
    console.print("\n", tabla_rutas_completa)
    
    console.print("\n[bold green]=== Auditoría Finalizada ===[/bold green]\n")

except Exception as e:
    console.print(f"\n[bold red]Error fatal procesando equipo:[/bold red] {e}\n")