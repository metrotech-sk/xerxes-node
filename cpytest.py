#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os, sys
from xerxes_node import config
from xerxes_node.network import XerxesNetwork

from xerxes_node.utils import discover

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

cppyy.add_include_path(os.path.join(script_dir, "lib/include"))
[cppyy.include(i) for i in os.listdir(os.path.join(script_dir, "lib/include"))]
cppyy.add_library_path(os.path.join(script_dir, "build"))
cppyy.load_library("libxerxes")
from cppyy.gbl import Xerxes as X

from xerxes_node.leaves.pleaf import PLeaf


if __name__ == "__main__":
    rs485 = X.RS485(sys.argv[1])
    comm = X.Protocol(rs485, 0x00)
    leaves = []
    for key in config.leaves.keys():
        if config.leaves.get(key) == "nivelation":
            leaves.append(PLeaf(comm, key, std_timeout=0.02, medium=config.used_medium))

    network = XerxesNetwork(leaves, std_timeout_s=0.2)