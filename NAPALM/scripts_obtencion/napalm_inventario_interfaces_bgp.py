import napalm
from tabulate import tabulate         

def main(): # Crea la función main, sin argumentos para poder invocarla

        driver_ios = napalm.get_network_driver("ios")

        lista_dispositivos = [["clab-Branch-CISCO","ios", "router"],
                              ["clab-Branch-INTERNET","ios", "router"],
                              ["clab-Branch-SW1","ios", "switch"],
                              ["clab-Branch-SW2","ios", "switch"],
                              ["clab-Branch-SW3","ios", "switch"],
                              ["clab-Branch-SW4","ios", "switch"]
                              ]
        
        dispositivos_red = []

        for dispositivo in lista_dispositivos: # Creamos objetos de conexión para NAPALM
                dispositivos_red.append(
                driver_ios(
                hostname = dispositivo[0], # hace referencia al Hostname del dispositivo en la lista_dispositivos
                username = "admin",
                password = "admin"
                                ) # Al terminar la iteración la lista dispositivos_red guardará los objetos de conexión a NAPALM
                        )
        
        tabla_dispositivos = [["hostname","vendor","modelo","uptime","serial"]]
        tabla_dispositivos_int = [["hostname","interfaces", "is_up","is_enable","description","speed","mtu","mac_address"]]
        tabla_dispositivos_bgp = [["hostname", "neighbor", "remote-as", "status", "sent prefixes", "received prefixes"]]

        for dispositivo in dispositivos_red:
                print("Conectando a {} ... ".format(dispositivo.hostname))
                dispositivo.open()

                print("Obteniendo Información del Dispositivo")
                dispositivo_info = dispositivo.get_facts()

                tabla_dispositivos.append([dispositivo_info["hostname"],
                                           dispositivo_info["vendor"],
                                           dispositivo_info["model"],
                                           dispositivo_info["uptime"],
                                           dispositivo_info["serial_number"]
                                           ])
                
                print("Obteniendo Información de Interfaces")
                dispositivos_interfaces = dispositivo.get_interfaces()
                for interface in dispositivos_interfaces:
                        tabla_dispositivos_int.append([dispositivo_info["hostname"],
                                                       interface,
                                                       dispositivos_interfaces[interface]['is_up'],
                                                       dispositivos_interfaces[interface]['is_enabled'],
                                                       dispositivos_interfaces[interface]['description'],
                                                       dispositivos_interfaces[interface]['speed'],
                                                       dispositivos_interfaces[interface]['mtu'],
                                                       dispositivos_interfaces[interface]['mac_address']
                                                       ])
                
                if not "SW" in dispositivo_info["hostname"]:
                        print("Obteniendo vecinos BGP")
                        dispositivo_bgp_peers = dispositivo.get_bgp_neighbors()

                        for bgp_neighbor in dispositivo_bgp_peers['global']['peers']:
                                tabla_dispositivos_bgp.append([dispositivo_info["hostname"],
                                                               bgp_neighbor,
                                                               dispositivo_bgp_peers['global']['peers'][bgp_neighbor]['remote_as'],
                                                               dispositivo_bgp_peers['global']['peers'][bgp_neighbor]['is_up'],
                                                               dispositivo_bgp_peers['global']['peers'][bgp_neighbor]['address_family']['ipv4 unicast']['sent_prefixes'],
                                                               dispositivo_bgp_peers['global']['peers'][bgp_neighbor]['address_family']['ipv4 unicast']['received_prefixes']
                                                               ])
                dispositivo.close()
                print("Realizado.")

        print(tabulate(tabla_dispositivos, headers="firstrow"))
        print(tabulate(tabla_dispositivos_int, headers="firstrow"))
        print(tabulate(tabla_dispositivos_bgp, headers="firstrow"))

if __name__ == "__main__": # Condición para ejecutar el programa principal
        main()