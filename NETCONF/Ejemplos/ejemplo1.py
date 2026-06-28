from ncclient import manager
from device_info import ios_xe_pe1
from xml.dom import minidom

filter_xml = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
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
        
        reply = m.get(filter=filter_xml)
        xml_pretty = minidom.parseString(reply.xml).toprettyxml(indent="    ")
        print(xml_pretty)