from netmiko import ConnectHandler
from getpass import getpass

# Prompt para las credenciales SSH del usuario
# El username es mostrado en texto plano
user = input('Ingrese el Usuario SSH: ')

# El password es escondido al momento de tipear
passwd = getpass('Ingrese la contraseña: ')

device = {
    'device_type': 'cisco_ios',
    'host': 'clab-Branch-CISCO',
    'username': user, # usaremos input() para recolectar el usuario
    'password': passwd, # usaremos getpass() para recolectar de manera segura el password
    'session_log': 'R-CISCO-log.txt',
}

net_connect = ConnectHandler(**device)

# Creamos una lista python con los comandos a ejecutar
config_int_LAN = ['interface e0/1', 
            'description LAN - Realizado via Python - Netmiko', 
            'ip address 192.168.1.2 255.255.255.0',
            'no shutdown',
            'vrrp 10 ip 192.168.1.1',
            'vrrp 10 priority 95',
            'vrrp 10 preempt']

config_int_WAN = ['interface e0/2', 
            'description WAN - Realizado via Python - Netmiko', 
            'ip address 10.0.0.2 255.255.255.252',
            'no shutdown']

config_int_Lo0 = ['interface lo0', 
            'description Lo0 - Realizado via Python - Netmiko', 
            'ip address 190.0.0.1 255.255.255.0']

configuraciones = [config_int_LAN, config_int_WAN, config_int_Lo0]

for config in configuraciones:
    # Ejecutamos la Configuración de la Interface LAN
    print(f'Configurando {config[0]}')
    net_connect.send_config_set(config)

# Configuramos la ruta default
#print('\n Configurando default gateway')
#net_connect.send_config_set('ip route 0.0.0.0 0.0.0.0 10.0.0.1')
print('\n Configurando Enrutamiento BGP')
bgp = ['router bgp 100', 'neighbor 10.0.0.1 remote-as 200', 'network 190.0.0.0 mask 255.255.255.0']
net_connect.send_config_set(bgp)
#print('\n Mostrando las rutas estáticas')
#print(net_connect.send_command('show ip route static'))
# Cerramos la conexión SSH
net_connect.disconnect()