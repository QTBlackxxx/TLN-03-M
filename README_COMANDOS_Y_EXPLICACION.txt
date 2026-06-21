GUIA PRINCIPAL - PC1 TLN03

Archivo principal:
  Topologia-ISP-SOLUCION.yml

Carpeta de configuraciones:
  configs/

1) Levantar el laboratorio
  sudo containerlab deploy -t Topologia-ISP-SOLUCION.yml

2) Entrar a un router Cisco IOL
  docker exec -it clab-ISP-TDP-CLARO-IOL-CPE-HQ telnet 127.0.0.1 5000

3) Entrar a modo privilegiado
  enable

4) Revisar BGP
  show bgp ipv4 unicast summary
  show ip bgp
  show ip route bgp

5) Revisar OSPF
  show ip ospf neighbor
  show ip route ospf

6) Probar conectividad desde PCs
  docker exec -it clab-ISP-TDP-CLARO-IOL-PC1-VLAN10 ping 192.168.5.11
  docker exec -it clab-ISP-TDP-CLARO-IOL-PC1-VLAN10 ping 192.168.15.13
  docker exec -it clab-ISP-TDP-CLARO-IOL-PC1-VLAN10 ping 8.8.8.8

7) Revisar IPsec en CPE-HQ / CPE-BRANCH
  show crypto isakmp sa
  show crypto ipsec sa

8) Simular falla de Movistar desde CPE-HQ
  configure terminal
  interface Ethernet0/1
  shutdown
  end

9) Simular falla de Movistar desde CPE-BRANCH
  configure terminal
  interface Ethernet0/3
  shutdown
  end

10) Restaurar Movistar
  configure terminal
  interface Ethernet0/1
  no shutdown
  end

  En CPE-BRANCH:
  configure terminal
  interface Ethernet0/3
  no shutdown
  end

NOTA IMPORTANTE:
Si se inhabilita el puerto e0/1 del router CPE-HQ (lo que también desaparece el Tunel Gree IPsec). Por lo que el router vuelve a buscar la otra ruta redundante para enviar el tráfico lo que genera cierta demora.
