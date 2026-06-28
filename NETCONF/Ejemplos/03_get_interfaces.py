from device_info import ios_xe_pe1
from ncclient import manager
import xmltodict

# Aplicamos un filtro a NETCONF para usar
#netconf_filter = open ("filter-ietf-interfaces-all.xml").read()

filter_xml = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
</filter>
"""

if __name__ == '__main__':
    with manager.connect(host=ios_xe_pe1["address"], port=ios_xe_pe1["port"],
                         username=ios_xe_pe1["username"],
                         password=ios_xe_pe1["password"],
                         hostkey_verify=False,
                         allow_agent=False,
                         look_for_keys=False
                         ) as m:
        
        # Obtenemos configuración y estado / información de interface
        netconf_reply = m.get(filter=filter_xml)

        # Procesamos el XML y almacenamos en diccionarios para usar
        intf_details = xmltodict.parse(netconf_reply.xml)["rpc-reply"]["data"]

        # Obtenemos las estructuras (o diccionarios vacíos si no existen)
        interfaces = intf_details.get("interfaces", {}).get("interface", [])
        interfaces_state = intf_details.get("interfaces-state", {}).get("interface", [])

        # Si el router devuelve solo una interfaz, xmltodict la hace diccionario. 
        # La convertimos a lista para que el bucle for funcione siempre.
        # Pregunta: "¿La variable interfaces es un Diccionario?"
        if isinstance(interfaces, dict):
            # Si es True (es una sola interfaz), la metemos dentro de corchetes 
            # para transformarla artificialmente en una lista de un solo elemento.
            interfaces = [interfaces]
        if isinstance(interfaces_state, dict):
            interfaces_state = [interfaces_state]

        # Creamos un mapa de estado usando el nombre de la interfaz como llave para emparejar
        estado_map = {item["name"]: item for item in interfaces_state}

        print("\n=== Detalle de Interfaces ===")
        for intf in interfaces:
            nombre = intf.get("name")
            # Buscamos la información operativa correspondiente a esta interfaz
            info_op = estado_map.get(nombre, {})

            print("\n Nombre: {}".format(nombre))
            print(" Descripción: {}".format(intf.get("description", "Sin descripción")))
            print(" Tipo: {}".format(intf.get("type", {}).get("#text", "Desconocido")))
            print(" Dirección MAC: {}".format(info_op.get("phys-address", "N/A")))
            
            # Estadísticas (verificamos si el nodo existe antes de imprimir)
            stats = info_op.get("statistics", {})
            print(" Paquetes Entrantes: {}".format(stats.get("in-unicast-pkts", "0")))
            print(" Paquetes Salientes: {}".format(stats.get("out-unicast-pkts", "0")))
            print("-" * 30)