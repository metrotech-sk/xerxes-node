#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_node.hierarchy.branches.nivelation_branch import NivelationBranch
from xerxes_node.medium import Medium


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = "mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority"
use_database = "test"
sample_period = 1
update_period = 60
network_timeout = 0.5
use_device = "/dev/ttyUSB0"


branches = {
    "nivel1" : { 
        "type": NivelationBranch,
        "reference_leaf" : 0x1f,
        "leaves" : {  # do not include reference
            0x01                : "nivelation",
            0x02                : "nivelation",
            0x03                : "nivelation",
        },
        "medium" : Medium.propyleneglycol,
        "sensor_timeout" : 0.005
    }
}       


# toto pojde prec
reference_leaf_addr = 0x1f
leaves = {
        0x01                : "nivelation",
        0x02                : "nivelation",
        0x03                : "nivelation",
        0x1f                : "nivelation"  # also reference
    }