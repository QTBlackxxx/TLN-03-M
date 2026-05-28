import napalm
from pprint import pprint

#Cargamos el driver de IOS
# En este caso requiere habilitar el ip scp server enable en los routers
driver = napalm.get_network_driver('ios')

# Definimos el device
device_1 = driver (
    hostname = "clab-Branch-CISCO",
    username = 'admin',
    password = 'admin'
)

device_2 = driver (
    hostname = "clab-Branch-SW1",
    username = 'admin',
    password = 'admin'
)

#Abrimos conexion
device_1.open()

# Vemos la configuracion de las interfaces antes de los cambios
print('\nAntes de los cambios:')
pprint(device_1.get_interfaces_ip())

# Definimos la configuracion que queremos aplicar en formato IOS CLI
ios_config_1 = '''
interface e0/1
description Realizado via NAPALM
ip address 192.168.100.1 255.255.255.0
no shutdown
'''

# Cargamos la configuracion como candidata
device_1.load_merge_candidate(config=ios_config_1)

# Mostramos las diferencias entre la configuracion actual (staged) y la candidata
print('\nConfiguracion Actual')
print(device_1.compare_config())

# Preguntamos al usuario si desea aplicar (commit) los cambios
user_input = input("\n¿Desea aplicar los cambios? (si/no)")

if user_input.lower() == 'si':
    device_1.commit_config()
    print('\n Cambios aplicados (commited)')
else:
    device_1.discard_config()
    print('\n Cambios descartados')

# Verificamos la configuracion de la interface luego de los cambios
print('\nLuego de los cambios:')
pprint(device_1.get_interfaces_ip())

# Cerramos conexion
device_1.close()