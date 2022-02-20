#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dis import disco
import cppyy, os, time, sys, struct

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

cppyy.add_include_path(os.path.join(script_dir, "lib/include"))
[cppyy.include(i) for i in os.listdir(os.path.join(script_dir, "lib/include"))]
cppyy.add_library_path(os.path.join(script_dir, "build"))
cppyy.load_library("libxerxes")
from cppyy.gbl import Xerxes as X
from cppyy.gbl import std

from xerxes_node.leaves.pleaf import PLeaf


def discover(comm, leaves, addr_range=127, repeat=1):
    found_addresses = []

    for i in range(repeat):
        for addr in range(1, addr_range):
            if addr in found_addresses:
                continue

            try:
                comm.ping(addr)
                comm.receive(.02)
                found_addresses.append(addr)
            except cppyy.gbl.TimeoutExpired:
                pass
    return found_addresses

if __name__ == "__main__":
    rs485 = X.RS485(sys.argv[1])
    comm = X.Protocol(rs485, 0x00)
    leaves = []
    pleaf = X.PLeaf(0x01, comm, 0.02)
    
    print(discover(comm, leaves))
    
    comm.ping(0x01)
    reply = comm.receive(.02)
    reply = bytes([ord(i) for i in reply.payload])
    struct.unpack("!IIII", reply)

        
    # adresses_discovered = discover(comm, leaves)
    