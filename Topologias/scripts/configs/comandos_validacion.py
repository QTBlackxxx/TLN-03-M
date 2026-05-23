# Parte 4 - Validación de Túneles DMVPN

COMANDOS_SUP = {

    # ------------------------------------------------------------------
    # HUB PRINCIPAL - CPE-HQ
    # Valida: registro de spokes en NHRP, estado del túnel como HUB
    # Tunnel1 -> red DMVPN 172.16.10.0/24 
    "CPE-HQ": [
        "show dmvpn",
        "show dmvpn detail",
        "show ip nhrp",
        "show interfaces Tunnel1",
        "show ip ospf neighbor",
        "show ip route ospf",
    ],

    # ------------------------------------------------------------------
    # HUB BACKUP - CPE-HQ-BK
    # Valida: registro de spokes en NHRP, estado del túnel como HUB backup
    # Tunnel2 -> red DMVPN 172.16.20.0/24 
    "CPE-HQ-BK": [
        "show dmvpn",
        "show dmvpn detail",
        "show ip nhrp",
        "show interfaces Tunnel2",
        "show ip ospf neighbor",
        "show ip route ospf",
    ],

    # ------------------------------------------------------------------
    # SPOKE PRINCIPAL - CPE-BRANCH2
    # Valida: registro al HUB, estado de ambos túneles, VRRP activo
    # Tunnel1 (172.16.10.4) → HUB principal
    # Tunnel2 (172.16.20.4) → HUB backup
    "CPE-BRANCH2": [
        "show dmvpn",
        "show dmvpn detail",
        "show ip nhrp",
        "show interfaces Tunnel1",
        "show interfaces Tunnel2",
        "show vrrp brief",
        "show ip ospf neighbor",
        "show ip route ospf",
        "show ip interface brief",
    ],

    # ------------------------------------------------------------------
    # SPOKE BACKUP - CPE-BRANCH2-BK
    # Valida: registro al HUB, estado de ambos túneles, VRRP en standby
    # Tunnel1 (172.16.10.5) → HUB principal
    # Tunnel2 (172.16.20.5) → HUB backup
    "CPE-BRANCH2-BK": [
        "show dmvpn",
        "show dmvpn detail",
        "show ip nhrp",
        "show interfaces Tunnel1",
        "show interfaces Tunnel2",
        "show vrrp brief",
        "show ip ospf neighbor",
        "show ip route ospf",
        "show ip interface brief",
    ],
}