from ncclient import manager
from device_info_h import vrp_h1
from xml.dom import minidom
import logging

#filter_xml = """
#<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
#</filter>
#"""

filter_xml2 = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <interfaces xmlns="http://openconfig.net/yang/interfaces"/>
</filter>
"""

logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    with manager.connect(host=vrp_h1["address"], port=vrp_h1["port"],
                         username=vrp_h1["username"],
                         password=vrp_h1["password"],
                         hostkey_verify=False,
                         allow_agent=False,
                         look_for_keys=False
                         ) as m:
        
        #reply = m.get(filter=filter_xml)
        reply = m.get(filter=filter_xml2)
        xml_pretty = minidom.parseString(reply.xml).toprettyxml(indent="    ")
        print(xml_pretty)