# Proyecto de Redes

## Descripción
Este laboratorio implementa una topología con Containerlab y Ansible.

## Topología
![Topologia](docs/topologia.png)

## Tecnologías
- Containerlab
- Ansible
- Docker

| Router | IP |
|--------|----|
| R1     | 192.168.1.1 |
| R2     | 192.168.1.2 |

```bash
docker ps
containerlab deploy

---

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