from device_info import ios_xe_pe1
from ncclient import manager
from device_info import ios_xe_pe1

if __name__ == '__main__':
    with manager.connect(host=ios_xe_pe1["address"], port=ios_xe_pe1["port"],
                         username=ios_xe_pe1["username"],
                         password=ios_xe_pe1["password"],
                         hostkey_verify=False,
                         allow_agent=False,
                         look_for_keys=False
                         ) as m:
        for cap in m.server_capabilities:
            if "ietf-interfaces" in cap:
                print(cap)