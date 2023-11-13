#!/usr/bin/env python3


from xerxes_protocol.network import XerxesNetwork, Addr
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.utils import leaf_generator
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
import xerxes_node.config as config
from xerxes_node.system import Duplex, XerxesSystem
from xerxes_node.utils import get_cpu_temp_celsius
from xerxes_node.debug_serial import DebugSerial
import logging
import os
import time
from typing import List

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

def find_leaves(xr: XerxesRoot) -> List[Leaf]:
    leaves = []
    for i in range(127):
        try:
            ping_reply = xr.ping(Addr(i))
            log.info(f"ping reply: {ping_reply}")
            leaf = Leaf(ping_reply.address, xr)
            leaves.append(leaf)
        except TimeoutError:
            log.warning(f"Timeout on address {i}")
        except Exception as e:
            log.error(e)

if __name__ == "__main__":
    print("creating logger")
    log_filename = "/tmp/xerxes.log"
    
    log = logging.getLogger()
    logging.basicConfig(
        format="%(levelname)s: %(message)s",  # '%(asctime)s: %(name)s: %(levelname)s - %(message)s', 
        # datefmt='%m/%d/%Y %I:%M:%S %p',
        # filename=log_filename, 
        level=logging._nameToLevel[config.logging_level]
    )
    

    log.info(f"Logger started, log file: {log_filename}")
    log.warning("Starting network.")
    dSerial1 = DebugSerial(port=config.use_device)
    dSerial2 = DebugSerial(port=config.use_device2)
    
    XN = XerxesNetwork(dSerial1).init(
        baudrate=115200,
        timeout=config.port_timeout
    )
    XN2 = False
    try:
        XN2 = XerxesNetwork(dSerial2).init(
            baudrate=115200,
            timeout=config.port_timeout
        )
    except:
        pass

    log.info(XN)
    if XN2: log.info(XN2)
    log.info("Creating root (master)")

    XR = XerxesRoot(Addr(0xfe), XN)
    if XN2: 
        XR2 = XerxesRoot(Addr(0xfe), XN2)
    else:
        XR2 = False
    log.warning("Master created")
    log.info(str(XR))

    log.warning("Creating node system")
    XS = XerxesSystem(
        mode=Duplex.HALF,
        root=XR,
        std_timeout_s=config.network_timeout,
    )
    if XN2:
        XS2 = XerxesSystem(
            mode=Duplex.HALF,
            root=XR2,
            std_timeout_s=config.network_timeout,
        )    
    else:
        XS2 = False
    log.info("System created.")
    log.warning(f"Discovering leaves on network {XN}")
    log.info(XS.discover())
    if XN2: 
        log.warning(f"Discovering leaves on network {XN2}")
        log.info(XS2.discover())
    log.warning([i.address for i in XS._leaves])

    if XN2: log.warning([i.address for i in XS2._leaves])
    
    find_leaves(XR)
    find_leaves(XR2)
    
    