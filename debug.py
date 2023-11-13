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
import traceback

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

def find_leaves(xr: XerxesRoot, end_addr: int = 127) -> List[Leaf]:
    log.info(f"Finding leaves on {xr}")
    leaves = []
    for i in range(end_addr):
        try:
            leaf = Leaf(Addr(i), xr)
            ping_reply = leaf.ping()
            log.info(f"ping reply: {ping_reply}")
            leaves.append(leaf)
            time.sleep(0.2)
        except TimeoutError:
            log.warning(f"Timeout on address {i}")
        except Exception as e:
            # log error and traceback:
            log.error(f"Error on address {i}: {e}")
            log.error(traceback.format_exc())
            

if __name__ == "__main__":
    print("creating logger")
    log_filename = "/tmp/xerxes.log"
    
    log = logging.getLogger()
    # setup config to print function:lineno
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s',
        datefmt='%H:%M:%S'
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
    log.warning("Masters created")
    log.info(str(XR))
    log.info(str(XR2))

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
    
    # find_leaves(XR)
    find_leaves(XR2)
    
    