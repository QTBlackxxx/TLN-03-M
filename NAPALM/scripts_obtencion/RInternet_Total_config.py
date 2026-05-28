from netmiko import ConnectHandler
from getpass import getpass

# Prompt para las credenciales SSH del usuario
# El username es mostrado en texto plano
user = input('Ingrese el Usuario SSH: ')

# El password es escondido al momento de tipear
passwd = getpass('Ingrese la contraseña: ')

device = {
    'device_type': 'cisco_ios',
    'host': 'clab-Branch-INTERNET',
    'username': user, # usaremos input() para recolectar el usuario
    'password': passwd, # usaremos getpass() para recolectar de manera segura el password
    'session_log': 'R-INTERNET-log.txt',
}

net_connect = ConnectHandler(**device)

# Creamos una lista python con los comandos a ejecutar
config_int_lo0 = ['interface l0', 
            'description Loopback1 - Internet - Realizado via Python - Netmiko', 
            'ip address 8.8.8.8 255.255.255.255',
            'no shutdown']

config_int_e1 = ['interface e0/1', 
            'description Hacia CISCO - Realizado via Python - Netmiko', 
            'ip address 10.0.0.1 255.255.255.252',
            'no shutdown']

config_int_e2 = ['interface e0/2', 
            'description Hacia HUAWEI - Realizado via Python - Netmiko', 
            'ip address 10.0.0.5 255.255.255.252',
            'no shutdown']

#  Mostramos la configuración antes del script
print(f'\nConfigurando Loopback0')

# Ejecutamos la Configuración de la Interface Loopback0
interface_LAN = net_connect.send_config_set(config_int_lo0)

print(f'\nConfigurando Ethernet0/1')

# Ejecutamos la Configuración de la Interface Ethernet0/1
interface_LAN = net_connect.send_config_set(config_int_e1)

print(f'\nConfigurando Ethernet0/2')

# Ejecutamos la Configuración de la Interface Ethernet0/2
interface_LAN = net_connect.send_config_set(config_int_e2)

# Configuramos la ruta estáticas de las Publicas de cada router
#print('\n Configurando Ruta hacia 190.0.0.0/24')
#net_connect.send_config_set('ip route 190.0.0.0 255.255.255.0 10.0.0.2')
print('\n Configurando Enrutamiento BGP con Router CISCO')
bgp = ['router bgp 200', 'neighbor 10.0.0.2 remote-as 100', 'redistribute static']
net_connect.send_config_set(bgp)

print('\n Configurando Ruta hacia 200.0.0.0/24')
net_connect.send_config_set('ip route 200.0.0.0 255.255.255.0 10.0.0.6')

#print('\n Mostrando las rutas estáticas')
#print(net_connect.send_command('show ip route static'))

# Cerramos la conexión SSH
net_connect.disconnect()