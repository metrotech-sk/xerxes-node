#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from rich import print
import os
import time
import socket
import logging
import sys
import serial
from pymongo import MongoClient
from pymongo.collection import Collection
from xerxes_protocol.network import XerxesNetwork, Addr
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.utils import leaf_generator
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
from xerxes_protocol.hierarchy.leaves.pressure import PLeaf, PLeafData

import xerxes_node.config as config
from xerxes_node.system import Duplex, XerxesSystem
from xerxes_node.utils import get_cpu_temp_celsius


def tare_pleaf(leaf: PLeaf):
    leaf.write_param("offset", 0)
    leaf.reset_soft()
    time.sleep(.2)
    pressures = []
    for i in range(100):
        leaf.root.sync()
        time.sleep(0.01)
        fd: PLeafData = leaf.fetch()
        pressures.append(fd.pressure.preferred())
        
    pressures.sort()
    
    avg_p = sum(pressures[10:-10]) / (len(pressures)-20)
    log.info(f">>> Ambient pressure {leaf.address} (no connection): {avg_p}")
    
    if avg_p != 0:
        log.info("Writing to register: offset...")
        leaf.write_param("offset", -avg_p)
        leaf.reset_soft()
        time.sleep(.01)


def tare_leaf(leaf: Leaf):
    if isinstance(leaf, PLeaf):
        tare_pleaf(leaf)
    else:
        pass


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
    
    XN = XerxesNetwork(serial.Serial(
        port=config.use_device
    )).init(
        baudrate=115200,
        timeout=config.port_timeout
    )
    log.info(XN)
    log.info("Creating root (master)")
    XR = XerxesRoot(Addr(0xfe), XN)
    log.warning("Master created")
    log.info(str(XR))

    log.warning("Creating node system")
    XS = XerxesSystem(
        mode=Duplex.HALF,
        root=XR,
        std_timeout_s=config.network_timeout,
    )
    
    
    log.warning("Discovering leaves on network...")
    log.info(XS.discover())
    
    for leaf in XS._leaves:
        tare_leaf(leaf)