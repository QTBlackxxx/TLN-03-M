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
                dispositivo.close()
        
        print("Realizado.")
        print(tabulate(tabla_dispositivos, headers="firstrow"))

if __name__ == "__main__": # Condición para ejecutar el programa principal
        main()