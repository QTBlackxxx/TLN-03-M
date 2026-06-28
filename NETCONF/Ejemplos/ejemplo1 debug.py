from ncclient import manager
import logging

logging.basicConfig(level=logging.DEBUG)

with manager.connect(
    host="clab-NETCONF-PE1",
    port=830,
    username="admin",
    password="admin",
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False,
    timeout=30
) as m:
    print(m.connected)