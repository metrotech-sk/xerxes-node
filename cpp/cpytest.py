#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os, time, sys

includes = ["Packet.h", "Serialization.h", "PacketSerializer.h", "MsgReader.h", "AsyncMsgReader.h", "rs485.h", "RequestResponseClient.h"]
for i in includes:
    cppyy.include(i)

cppyy.add_library_path("/usr/local/lib")
cppyy.load_library("XeusProtocol")
cppyy.load_library("SerialBus")
from cppyy.gbl import Xerxes as X
from cppyy.gbl import std
from cppyy.gbl import AsyncMsgReader, MsgReader, RequestResponseClient


bus = X.RS485(sys.argv[1])
amr = AsyncMsgReader[MsgReader](MsgReader(bus, std.chrono.milliseconds(10)))
    
    
exit(0)

rs485 = X.RS485("/dev/ttyUSB0")
comm = X.Protocol(rs485, 0x00)
leaf1 = X.PLeaf(0x01, comm, 0.020)

leaves = []
found_addresses = []

print("scanning...")

for i in range(1):
    for addr in range(1, 32):
        if addr in found_addresses:
            continue

        try:
            tmp_leaf = X.PLeaf(addr, comm, 0.020)
            tmp_leaf.read()
            if addr not in found_addresses:
                found_addresses.append(addr)
                leaves.append(tmp_leaf)
                print(f"leaf: {addr} found!")
        except cppyy.gbl.std.runtime_error:
            pass

print("Leaves found:")

for leaf in found_addresses:
    print(leaf)

while True:
    for leaf in leaves:
        val = leaf.read()
        print(f"Leaf[{leaf.getAddr()}]: p={val.pressure.getmmH2O():.3f}[mmH2O], t={val.temp_sens.getCelsius():.1f}°C")
    print("\n")
    time.sleep(1)