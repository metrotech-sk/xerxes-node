#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_node.hierarchy.branches.inclination import InclinationBranch
from xerxes_node.hierarchy.branches.nivelation import NivelationBranch
from xerxes_node.hierarchy.leaves.ileaf import ILeaf
from xerxes_node.hierarchy.leaves.pleaf import PLeaf, pleaves_from_list
from xerxes_node.medium import Medium
from xerxes_node.network import Addr


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = "mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority"
use_database = "test" # "pri_sajbach"
sample_period = 1  # how often read sensors, [s]
port_timeout = 0.005
network_timeout = 0.05  # read until, [s]
update_period = 60  # how often to push to DB, [s]
use_device = "/dev/ttyUSB0"  # device used for communication


branches = [
    NivelationBranch(
        name="nivelation_1",
        leaves=pleaves_from_list(
            addresses=[  # do not include reference
                0x01,
                0x02,
                0x03,
            ],
            medium=Medium.propyleneglycol
        ),
        reference_leaf=PLeaf(addr=Addr(0x1F)), 
        column_avg_samples=10
    ),
    
    InclinationBranch(
        name="inclination_1",
        leaves=[
            ILeaf(addr=Addr(0x04)),
            ILeaf(addr=Addr(0x05)),
        ]
    )
]