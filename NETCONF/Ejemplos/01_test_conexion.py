from ncclient import manager

m = manager.connect(host="clab-NETCONF-PE1",
                    port=830,
                    username="admin",
                    password="admin",
                    hostkey_verify=False
                    )

m.close_session()