# UNIVERSIDAD NACIONAL DE INGENIERÍA
# CURSO TLN03 - AUTOMATIZACIÓN Y PROGRAMABILIDAD DE REDES

Repositorio base para el curso electivo TLN03 de la Universidad Nacional de Ingeniería.

---

## Topología

![Topologia](docs/Topologia%20Base-2.png)

---

## Tecnologías

- Linux
- Docker
- Containerlab
- Cisco
- Python
- Ansible

---

## ⚙ Configuraciones Base

## Funciones
**Funciones en el archivo sshHostKeyConn.py**
1. **ssh_exec_multiple(comandos):**
    - Uso: EJECUTAR COMANDOS DE CONFIGURACIÓN
    - Input: comandos (diccionario con elementos de la forma "hostname":"nombre_lista_comandos")
    - Descripción: Ejecuta en el dispositivo con hostname "hostname" los comandos que están como una lista dentro del diccionario **COMANDOS** en el archivo **comandos.py**, buscándolos según el nombre "nombre_lista_comandos".

2. **ssh_exec_multiple_validar(comandos):**
    - Uso: EJECUTAR COMANDOS DE DIAGNÓSTICO Y VALIDACIÓN
    - Input: comandos (diccionario con elementos de la forma "hostname":"nombre_lista_comandos")
    - Descripción: Ejecuta en el dispositivo con hostname "hostname" los comandos que están como una lista dentro del diccionario **COMANDOS_SUP** en el archivo **comandos_validacion.py**, buscándolos según el nombre "nombre_lista_comandos".


## Clases
1. **device(hostname, username, password):**
    - Descripción: Objeto al cual se le asignan propiedades hostname (nombre de host), username (nombre de usuario de inicio de sesión), password (contraseña de usuario de inicio de sesión).
    - Métodos: 
        set_password: Setea la contraseña a utilizar para el inicio de sesión por ssh.

---

## Ejecución

Todos los comandos deben ejecutarse desde el archivo:

```bash
TLN-03-M/Topologias/scripts/main.py
```

Y en el caso de validación y diagnóstico:

```bash
TLN-03-M/Topologias/scripts/validacion_diagnostico.py
```

Bajo ningún motivo borrar las librerías importadas al inicio.

Que los comandos de configuración y validación+diagnóstico se ejecuten desde archivos distintos es meramente por un tema de orden.

---

# Opciones

## Opción 1: Ejecución de comandos preestablecidos (configuración)

Cuando se quiera ejecutar una lista de comandos preestablecidos, de la forma:
```bash
        "conf terminal",
        "hostname CPE-HQ"
```

Se deben guardar los comandos en el archivo
```bash
comandos.py
```
dentro del diccionario **COMANDOS**, de la forma:

```bash
COMANDOS = {
    "comando1": [
        "conf terminal",
        "hostname CPE-HQ"
    ],
    "comando2": [
        "show running-config",
        "show ip route"
    ]
}
```

Una vez hecho ello, tenemos guardadas las series de comandos. Luego, en el archivo main.py, se debe colocar un mapeo entre el hostname del dispositivo y el nombre del comando a ejecutar, de la forma:

```bash
hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "comando1",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "comando2"
}
```

Y, de igual forma, en main.py se debe escribir el comando para ejecutar:

```bash
sshHostKeyConn.ssh_exec_multiple(hostname_comando)
```

Ahora, se debe ejecutar el archivo main.py de la forma:

```bash
python3 main.py
```

Entonces, ahora, en el dispositivo con **hostname clab-ISP-TDP-CLARO-IOL-CPE-HQ** se ejecutará la serie de **comandos 'comando1'**, y en el dispositivo con **clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK** se ejecutará la serie de **comandos 'comando2'**. Eso se mostrará en la consola terminal.

## Opción 2: Ejecución de comandos preestablecidos (validación y diagnóstico)

Cuando se quiera ejecutar una lista de comandos preestablecidos para diagnóstico, de la forma:
```bash
        "show running-config",
        "show ip route"
```

Se deben guardar los comandos en el archivo
```bash
comandos_validacion.py
```
dentro del diccionario **COMANDOS_SUP**, de la forma:

```bash
COMANDOS = {
    "comando1": [
        "show running-config",
        "show ip route"
    ],
    "comando2": [
        "show bgp",
        "show running-config",
        "show ip route"
    ]
}
```

Una vez hecho ello, tenemos guardadas las series de comandos. Luego, en el archivo validacion_diagnostico.py, se debe colocar un mapeo entre el hostname del dispositivo y el nombre del comando a ejecutar, de la forma:

```bash
hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "comando1",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "comando2"
}
```

Y, de igual forma, en validacion_diagnostico.py se debe escribir el comando para ejecutar:

```bash
sshHostKeyConn.ssh_exec_multiple_validar(hostname_comando)
```

El archivo validacion_diagnostico.py quedará de la forma:

```bash
from network_scripting import sshHostKeyConn
from getpass import getpass
from configs import funcion_comandos
import paramiko
import time
from configs.comandos import COMANDOS

hostname_comando = {
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ": "CPE-HQ",
    "clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK": "CPE-HQ-BK"
}

sshHostKeyConn.ssh_exec_multiple_validar(hostname_comando)
```

Ahora, se debe ejecutar el archivo validacion_diagnostico.py de la forma:

```bash
python3 validacion_diagnostico.py
```

Entonces, ahora, en el dispositivo con **hostname clab-ISP-TDP-CLARO-IOL-CPE-HQ** se ejecutará la serie de **comandos 'comando1'**, y en el dispositivo con **clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK** se ejecutará la serie de **comandos 'comando2'**. Eso se mostrará en la consola terminal.