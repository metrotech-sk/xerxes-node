#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os, sys
from xerxes_node import config
from xerxes_node.network import XerxesNetwork
from xerxes_node.parser import Parser
from xerxes_node.leaves.pleaf import PLeaf, PLeafData


if __name__ == "__main__":
    leaves = []
    for key in config.leaves.keys():
        if config.leaves.get(key) == "nivelation":
            leaves.append(PLeaf(comm, key, std_timeout=0.02, medium=config.used_medium))

    network = XerxesNetwork(leaves, std_timeout_s=0.2)
    network.poll()
    
