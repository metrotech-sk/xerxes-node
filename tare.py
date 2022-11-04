#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich import print
import time
import serial
from typing import List, Union, Optional
from xerxes_protocol.network import XerxesNetwork, Addr
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
from xerxes_protocol.hierarchy.leaves.pressure import PLeaf, PLeafData
from xerxes_protocol.hierarchy.leaves.inclination import ILeaf, ILeafData
from xerxes_protocol.hierarchy.leaves.strain import SLeaf, SLeafData
from xerxes_node import config
from xerxes_node.system import Duplex, XerxesSystem


def tare_pleaf(leaf: PLeaf) -> int:
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
    
    avg_p = sum(pressures[2:-2]) / (len(pressures)-4)
    print(f"PLeaf Ambient pressure {leaf.address} (no connection): {avg_p}")
    
    if avg_p != 0:
        print("Writing to register: offset ...")
        leaf.write_param("offset", -avg_p)
        leaf.reset_soft()
        time.sleep(.1)
        return 1
    
    return 0


def tare_ileaf(leaf: ILeaf) -> int:
    leaf.write_param("offset_x", 0)
    leaf.write_param("offset_y", 0)
    leaf.reset_soft()
    time.sleep(.2)
    x = []
    y = []

    for i in range(100):
        XR.sync()
        time.sleep(0.01)
        fd: ILeafData = leaf.fetch()

        x.append(fd.angle_x.preferred())
        y.append(fd.angle_y.preferred())

    x.sort()
    y.sort()
    avg_x = sum(x[2:-2]) / (len(x)-4)
    avg_y = sum(y[2:-2]) / (len(y)-4)
    print(f"ILeaf: Default offset: X: {avg_x}°, Y: {avg_y}°")
    
    if avg_x != 0 and avg_y != 0:
        print("Writing to register: offset_x, offset_y ...")
        leaf.write_param("offset_x", -avg_x)
        leaf.write_param("offset_y", -avg_y)
        leaf.reset_soft()
        time.sleep(.2)
        return 1

    return 0


def tare_sleaf(leaf: SLeaf) -> int:
    # clear current offset register
    leaf.write_param("offset", 0)
    # reset the sensor
    leaf.reset_soft()
    time.sleep(.1)
    
    # measure default value 100times
    strains = []
    for i in range(100):
        XR.sync()
        time.sleep(0.05)
        fd: SLeafData = leaf.fetch()
        strains.append(fd.strain.preferred())

    # sort the values
    strains.sort()
    
    # remove 4% of outliers (keep the middle 2 sigma) and calculate mean value from the rest
    avg_s = sum(strains[2:-2]) / (len(strains)-4)
    print(f"SLeaf: Default strain (no load): {avg_s}")
    
    if avg_s != 0:
        print("Writing to register: offset...")
        leaf.write_param("offset", -avg_s)
        leaf.reset_soft()
        time.sleep(.01)
        return 1
    
    return 0


def tare_leaves(leaves: List[Leaf], addr_range: Optional[List] = None) -> int:
    affected = 0
    
    if not isinstance(addr_range, list):
        addr_range = [addr for addr in range(0, 0xFF)]
    
    # for eaxh address on the bus
    for leaf in leaves:
        # seek only selected adresses, maybe can be rewritten better
        if leaf.address in addr_range:
            print(f"Taring: {leaf.address}")
            
            if isinstance(leaf, PLeaf):
                affected += tare_pleaf(leaf)
                
            elif isinstance(leaf, ILeaf):
                affected += tare_ileaf(leaf)
                
            elif isinstance(leaf, SLeaf):
                affected += tare_sleaf
            
    # return the number of affected adresses
    return affected


if __name__ == "__main__":
    XN = XerxesNetwork(serial.Serial(
        port=config.use_device
    ))
    XN.init(
        baudrate=115200,
        timeout=config.port_timeout
    )
    
    XR = XerxesRoot(Addr(0xfe), XN)
    
    XS = XerxesSystem(
        mode=Duplex.HALF,
        root=XR,
        std_timeout_s=config.network_timeout,
    )
    
    print("Discovering leaves on the network 🕵️")
    print(XS.discover())
    
    to_change = [i for i in range(15, 26)]
    print(f"Taring leaves 🔨🔨 \n{to_change}")
    affected = 0
    
    affected = tare_leaves(
        leaves=XS._leaves,
        addr_range=to_change
    )
    
    print(f"TARING FINISHED 💪💪💪\n{affected} leaves affected.")