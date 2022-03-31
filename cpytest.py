#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os, sys
from xerxes_node import config
from xerxes_node.hierarchy.branches.nivelation_branch import NivelationBranch
from xerxes_node.network import Duplex, XerxesNetwork
from xerxes_node.parser import NivelationParser
from xerxes_node.hierarchy.leaves.pleaf import PLeaf, PLeafData
from pprint import pprint as print


file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

cppyy.add_include_path(os.path.join(script_dir, "lib/include"))
[cppyy.include(i) for i in os.listdir(os.path.join(script_dir, "lib/include"))]
cppyy.add_library_path(os.path.join(script_dir, "build"))
cppyy.load_library("libxerxes")
from cppyy.gbl import Xerxes as X


if __name__ == "__main__":
    rs485 = X.RS485(config.use_device)
    comm = X.Protocol(rs485, 0x00)
    
    # load sensor list from config
    branches = []
    
    for branch_name in config.branches:
        # parse branches from config according to their type
        branch = config.branches[branch_name]
        if branch["type"] == NivelationBranch:
            ref_leaf = PLeaf(
                channel=comm,
                medium=branch["medium"],
                my_addr=branch["reference_leaf"],
                std_timeout=branch["sensor_timeout"]
            
            )
            pleaves = PLeaf.from_list(
                channel=comm, 
                addresses=branch["leaves"],
                std_timeout=branch["sensor_timeout"],
                medium=branch["medium"]
                )
            
            branches.append(
                NivelationBranch(
                    leaves=pleaves,
                    name=branch_name,
                    reference_leaf=ref_leaf
                )
            )
        
    xn = XerxesNetwork(
        branches=branches, 
        mode=Duplex.HALF, 
        std_timeout_s=config.network_timeout
        )
    
    b=branches[0]
    xn.poll()