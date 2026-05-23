COMANDOS_SUP = {
    
    "CPE-HQ": [
        "show ip interface brief",
        "show crypto isakmp sa",
        "show crypto ipsec sa",
        "show ip ospf neighbor",
        "show ip ospf interface Tunnel1",
        "show ip ospf database router",
        "show ip route ospf",
        "show ip cef 192.168.25.2",
        "show ip cef exact-route 172.16.10.1 192.168.25.2",
        "ping 192.168.25.2",
        "traceroute 192.168.25.2",
        "ping 172.16.10.4",
        "traceroute 172.16.10.4",
    ],
    
    "M3": [
        "show ip interface brief",
        "show ip ospf neighbor",
        "show ip ospf database",
        "show ip route static",
        "show ip route 180.0.0.0",
        "show ip cef 192.168.25.2",
        "ping 10.0.0.73",
    ],
    
    "CPE-BRANCH2": [
        "show ip interface brief",
        "show crypto isakmp sa",
        "show crypto ipsec sa",
        "show ip ospf neighbor",
        "show ip ospf interface Tunnel1",
        "show ip ospf database router",
        "show ip route ospf",
        "show ip route",
        "show ip nat statistics",
        "show ip interface brief",
        "show run interface Ethernet0/2.25",
        "ping 172.16.10.1",
        "traceroute 172.16.10.1",
    ],
    
    "SW2-R-PISO1": [
        "show vlan brief",
        "show interfaces trunk",
        "show mac address-table vlan 25",
        "show interfaces status",
    ]

}