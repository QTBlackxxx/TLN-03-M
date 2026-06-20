# MPLS L3VPN - Automatización de Red

Automatización y validación de una red **MPLS L3VPN** (IPv4/IPv6) desplegada sobre **containerlab**, usando **Ansible** para la configuración de los dispositivos y **Python** para tareas de operación complementarias.

## Topología de red

![Topologia](docs/Topologia%pc3.png)

La red está compuesta por los siguientes roles, todos desplegados como contenedores `clab-MPLS-*` mediante containerlab:

| Grupo Ansible | Dispositivos | Rol |
|---|---|---|
| `PE_routers` | PE1, PE2 | Provider Edge - frontera con clientes, MP-BGP VPNv4/VPNv6 |
| `P_routers` | P1, P2 | Provider - core MPLS, conmutación de etiquetas |
| `RR_routers` | RR1, RR2 | Route Reflectors - distribución de rutas MP-BGP |
| `CPEs` | CPE-1, CPE-2 | Customer Premises Equipment - equipos de cliente |
| `Switches` | SW-1, SW-2 | Conectividad de acceso |

## Estructura del proyecto

```
grupo3/
├── ansible.cfg              # Configuración de Ansible (interpreter, host key checking, etc.)
├── inventory.ini            # Inventario de dispositivos y grupos
├── generar_inventario.py    # Script Python - genera inventario CSV/TXT vía Ansible
│
├── host_vars/                  # Variables específicas por dispositivo
│   ├── clab-MPLS-CPE-1.yml
│   ├── clab-MPLS-CPE-2.yml
│   ├── clab-MPLS-P1.yml
│   ├── clab-MPLS-P2.yml
│   ├── clab-MPLS-PE1.yml
│   ├── clab-MPLS-PE2.yml
│   ├── clab-MPLS-RR1.yml
│   ├── clab-MPLS-RR2.yml
│   ├── clab-MPLS-SW-1.yml
│   └── clab-MPLS-SW-2.yml
│
├── playbooks/                  # Playbooks de configuración y validación
│   ├── interfaces.yml          # Configuración de interfaces
│   ├── ospf.yml                # Configuración IGP (OSPF)
│   ├── mpls.yml                # Configuración MPLS
│   ├── validate.yml            # Validación del estado de la red
│   └── gather_facts.yml        # Recolección de inventario (cisco.ios.ios_facts)
│
└── reportes/                # Salida de generar_inventario.py (CSV/TXT)
```

## Requisitos previos

- [containerlab](https://containerlab.dev/) con el laboratorio MPLS desplegado y los contenedores `clab-MPLS-*` corriendo.
- Python 3.10+
- Ansible:
  ```bash
  pip install ansible
  ansible-galaxy collection install cisco.ios
  ```

## Inventario Ansible

El inventario (`inventory.ini`) organiza los dispositivos por rol funcional, con subgrupos reutilizables para los playbooks:

```ini
[MPLS_routers]
clab-MPLS-PE1
clab-MPLS-PE2
clab-MPLS-P1
clab-MPLS-P2
clab-MPLS-RR1
clab-MPLS-RR2

[CPEs]
clab-MPLS-CPE-1
clab-MPLS-CPE-2

[Switches]
clab-MPLS-SW-1
clab-MPLS-SW-2

[PE_routers]
clab-MPLS-PE1
clab-MPLS-PE2

[P_routers]
clab-MPLS-P1
clab-MPLS-P2

[RR_routers]
clab-MPLS-RR1
clab-MPLS-RR2

[MPLS_core:children]
PE_routers
P_routers
RR_routers

[all:vars]
ansible_user=admin
ansible_password=admin
ansible_network_os=cisco.ios.ios
ansible_connection=ansible.netcommon.network_cli
ansible_paramiko_look_for_keys=False
```

El grupo `MPLS_core` agrupa PE, P y RR para poder apuntar playbooks de core (MPLS, OSPF) a todos ellos en un solo `hosts:`.

## Automatización con Ansible

Los playbooks viven en `playbooks/` y se ejecutan con `ansible-playbook -i inventory.ini playbooks/<playbook>.yml`.

| Playbook | Función |
|---|---|
| `interfaces.yml` | Configuración de interfaces de los dispositivos |
| `ospf.yml` | Configuración del IGP (OSPF) |
| `mpls.yml` | Configuración MPLS (label switching) |
| `validate.yml` | Validación del estado operativo posterior a la configuración |
| `gather_facts.yml` | Recolecta hardware/software de cada dispositivo con `cisco.ios.ios_facts` (usado por `generar_inventario.py`) |

Ejemplo de ejecución:

```bash
ansible-playbook -i inventory.ini playbooks/interfaces.yml
ansible-playbook -i inventory.ini playbooks/ospf.yml
ansible-playbook -i inventory.ini playbooks/mpls.yml
ansible-playbook -i inventory.ini playbooks/validate.yml
```

> Los playbooks de BGP y VPNv4/VPNv6, así como la validación con NAPALM, están planificados para una siguiente iteración del proyecto.

## Script Python adicional

**`generar_inventario.py`** — Genera automáticamente un inventario de hardware/software de todos los dispositivos de la red, ejecutando `playbooks/gather_facts.yml` (que usa `cisco.ios.ios_facts`) y exportando el resultado a **CSV** o **TXT**.

### Uso

```bash
# Inventario completo en CSV (reportes/inventario_<timestamp>.csv)
python3 generar_inventario.py

# En formato TXT
python3 generar_inventario.py --formato txt

# Ambos formatos a la vez
python3 generar_inventario.py --formato ambos

# Limitar a un grupo específico (ej: solo los PE)
python3 generar_inventario.py --grupo PE_routers

# Ruta de salida personalizada
python3 generar_inventario.py --salida reportes/inventario_pre_cambio.csv

# Ver el detalle de la ejecución de Ansible (debug)
python3 generar_inventario.py -v
```

### Datos que recolecta

| Campo | Descripción |
|---|---|
| `hostname` | Hostname configurado en el dispositivo |
| `grupos` | Grupos de Ansible a los que pertenece |
| `host_conexion` | Nombre usado en el inventario para conectarse |
| `modelo` | Imagen/plataforma del dispositivo (`ansible_net_image`) |
| `tipo_ios` | Tipo de IOS (`ansible_net_iostype`) |
| `version_ios` | Versión de IOS |
| `serial` | Número de serie |
| `uptime` | Tiempo de actividad |
| `memoria_total_mb` / `memoria_libre_mb` | Memoria del dispositivo |
| `estado` | `OK` si se pudo conectar y recolectar datos, `INALCANZABLE` si no |

Si un dispositivo no responde, el playbook lo registra igualmente con estado `INALCANZABLE` en vez de detener la ejecución completa (manejo de errores con `block/rescue`).
