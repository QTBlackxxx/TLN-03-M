import napalm

def main(): # Crea la función main, sin argumentos para poder invocarla

        driver_ios = napalm.get_network_driver("ios")

        ios_router = driver_ios(
                hostname = 'clab-Branch-CISCO',
                username = 'admin',
                password = 'admin',
        )

        print("Conectando a IOS Router")
        ios_router.open()
        print("Verificando estatus de Conexión con Router IOS:")
        print(ios_router.is_alive())

        ios_router.close()
        print("Prueba Completada")

if __name__ == "__main__": # Condición para ejecutar el programa principal
        main()