from inventario import INVENTORY, napalm_session, wait_for_ssh
from tabulate import tabulate

def extract_environment(device) -> dict:
    """
    get_environment() en IOS virtual (ContainerLab) lanza UnboundLocalError
    porque 'show processes memory' no contiene la línea I/O que NAPALM busca.
    Se captura explícitamente para retornar datos parciales sin crashear.
    """
    try:
        env = device.get_environment()
    except UnboundLocalError:
        # Bug interno de NAPALM con IOS virtual — memoria no disponible
        return {
            "cpu_%":        "N/A (virtual)",
            "mem_%":        "N/A (virtual)",
            "temp_alert":   "N/A",
            "temp_critical":"N/A",
        }
    except Exception as e:
        return {
            "cpu_%":        "ERR",
            "mem_%":        "ERR",
            "temp_alert":   str(e)[:30],
            "temp_critical":"-",
        }

    # ── CPU ──────────────────────────────────────────────────────────────
    cpu_data = env.get("cpu", {})
    if cpu_data:
        vals = []
        for v in cpu_data.values():
            # IOS virtual a veces devuelve float directo, otras un dict
            vals.append(float(v.get("%usage", v) if isinstance(v, dict) else v))
        cpu_avg = sum(vals) / len(vals)
    else:
        cpu_avg = 0.0

    # ── MEMORIA ──────────────────────────────────────────────────────────
    mem  = env.get("memory", {})
    used = mem.get("used_ram",      0) or 0
    avail= mem.get("available_ram", 0) or 0
    mem_pct = (used / (used + avail)) * 100 if (used + avail) > 0 else 0.0

    # ── TEMPERATURA ──────────────────────────────────────────────────────
    temps = env.get("temperature", {})
    safe_temps = [v for v in temps.values() if isinstance(v, dict)]

    return {
        "cpu_%":        round(cpu_avg, 1),
        "mem_%":        round(mem_pct, 1),
        "temp_alert":   " YES" if any(v.get("is_alert")    for v in safe_temps) else "✅ NO",
        "temp_critical":" YES" if any(v.get("is_critical") for v in safe_temps) else "✅ NO",
    }

def run_audit():
    results = []
    for name, info in INVENTORY.items():
        print(f"  [ENV] {name}...")
        if not wait_for_ssh(info['ip']):
            results.append({"device": name, "cpu_%": "ERR", "mem_%": "ERR", "temp_alert": "ERR", "temp_critical": "ERR"})
            continue
        try:
            with napalm_session(name, info) as device:
                data = extract_environment(device)
                data["device"] = name
                results.append(data)
            print(f" OK")
        except Exception as e:
            err = str(e)[:40]
            print(f"  {name}: {err}")
            results.append({"device": name, "cpu_%": "ERR", "mem_%": "ERR", "temp_alert": err, "temp_critical": "-"})
    return results

if __name__ == "__main__":
    print("\n INICIANDO ENVIRONMENT \n")
    data = run_audit()
    headers_map = {"device": "Dispositivo", "cpu_%": "CPU %", "mem_%": "RAM %", "temp_alert": "Alerta Temp", "temp_critical": "Temp Crítica"}
    print(tabulate(data, headers=headers_map, tablefmt="fancy_grid", showindex=False))