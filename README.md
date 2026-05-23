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

Por desarrollar.

---

## Ejecución

Todos los comandos deben ejecutarse desde el archivo:

```bash
TLN-03-M/Topologias/scripts/main.py
```

Bajo ningún motivo borrar las librerías importadas al inicio.

---

# Opciones

## Opción 1: Ejecución de comandos preestablecidos

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

Ahora, se debe ejecutar el archivo main.py de la forma:

```bash
python3 main.py
```

Entonces, ahora, en el dispositivo con **hostname clab-ISP-TDP-CLARO-IOL-CPE-HQ** se ejecutará la serie de **comandos 'comando1'**, y en el dispositivo con **clab-ISP-TDP-CLARO-IOL-CPE-HQ-BK** se ejecutará la serie de **comandos 'comando2'**. Eso se mostrará en la consola terminal.