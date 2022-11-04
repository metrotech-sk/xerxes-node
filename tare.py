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

from xerxes_node import config
from xerxes_node.system import Duplex, XerxesSystem
from xerxes_node.utils import get_cpu_temp_celsius


def tare_pleaf(leaf: PLeaf) -> bool:
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
    print(f">>> Ambient pressure {leaf.address} (no connection): {avg_p}")
    
    if avg_p != 0:
        print("Writing to register: offset ...")
        leaf.write_param("offset", -avg_p)
        leaf.reset_soft()
        time.sleep(.01)
        return True
    
    return False


def tare_leaf(leaf: Leaf) -> bool:
    if isinstance(leaf, PLeaf):
        return tare_pleaf(leaf)
    else:
        return False


if __name__ == "__main__":
    XN = XerxesNetwork(serial.Serial(
        port=config.use_device
    )).init(
        baudrate=115200,
        timeout=config.port_timeout
    )
    
    XR = XerxesRoot(Addr(0xfe), XN)
    
    XS = XerxesSystem(
        mode=Duplex.HALF,
        root=XR,
        std_timeout_s=config.network_timeout,
    )
    
    print("Discovering leaves on network...")
    print(XS.discover())
    
    affected = 0
    for leaf in XS._leaves:
        if tare_leaf(leaf): affected += 1
    
    print(f" ############### TARING FINISHED! {affected} leaves affected. ############### ")