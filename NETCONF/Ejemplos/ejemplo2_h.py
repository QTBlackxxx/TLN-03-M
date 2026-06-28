from ncclient import manager
from ncclient.transport.errors import SessionCloseError
from device_info_h import vrp_h1
from xml.dom import minidom


if __name__ == '__main__':
    try:
        with manager.connect(host=vrp_h1["address"], port=vrp_h1["port"],
                                username=vrp_h1["username"],
                                password=vrp_h1["password"],
                                hostkey_verify=False,
                                allow_agent=False,
                                look_for_keys=False
                                ) as m:
            
            print("Aca esta las capacidades de NETCONF")
            for capacidades in m.server_capabilities:
                print(capacidades)

    except SessionCloseError:
        print("La sesión fue cerrada por el servidor al finalizar.")