# UNIVERSIDAD NACIONAL DE INGENIERIA 
# CURSO - TLN03 - AUTOMATIZACIÓN Y PROGRAMABILIDAD DE REDES

 Descripción
Repositorio base para el curso Electivo TLN03 de la Universidad Nacional de Ingenieria.

## Topología
![Topologia]
## Tecnologías
- Linux
- Docker
- Containerlab
- Cisco
- Python
- Ansible

| Router | IP |
|--------|----|
| R1     | 192.168.1.1 |
| R2     | 192.168.1.2 |

#```bash
#docker ps
#containerlab deploy

#---

## ✔ Badges (very common)
```markdown
![GitHub repo size](https://img.shields.io/github/repo-size/user/repo)

- [x] Configurar OSPF
- [ ] Validar conectividad


<details>
<summary>Solución</summary>

Configuración OSPF:

```bash
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0