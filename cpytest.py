#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os, time, sys 

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

cppyy.add_include_path(os.path.join(script_dir, "lib/include"))
[cppyy.include(i) for i in os.listdir(os.path.join(script_dir, "lib/include"))]
cppyy.add_library_path(os.path.join(script_dir, "build"))
cppyy.load_library("libxerxes")
from cppyy.gbl import Xerxes as X
from cppyy.gbl import std

from xerxes_node.leaves.pleaf import PLeaf


def discover(comm, leaves, addr_range=32):
    found_addresses = []

    for i in range(3):
        for addr in range(1, 32):
            if addr in found_addresses:
                continue

            try:
                tmp_leaf = X.PLeaf(addr, comm, 0.020)
                tmp_leaf.read()
                if addr not in found_addresses:
                    found_addresses.append(addr)
                    leaves.append(tmp_leaf)
                    log.info(f"leaf: {addr} found!")
            except cppyy.gbl.std.runtime_error:
                pass
    return found_addresses

if __name__ == "__main__":
    rs485 = X.RS485(sys.argv[1])
    comm = X.Protocol(rs485, 0x00)
    leaves = []
    pleaf = X.PLeaf(0x01, comm, 0.02)
    
    while 1:
        comm.ping(0x01)
        reply = comm.receive(.02)
        print(bytes([ord(i) for i in reply.payload]))
        
    # adresses_discovered = discover(comm, leaves)
    