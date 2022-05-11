#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_node.hierarchy.branches.nivelation_branch import NivelationBranch
from xerxes_node.medium import Medium


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = "mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority"
use_database = "pri_sajbach"
sample_period = 1  # how often read sensors, [s]
port_timeout = 0.005
network_timeout = 0.05  # read until, [s]
update_period = 60  # how often to push to DB, [s]
use_device = "/dev/ttyS0"  # device used for communication
used_medium = Medium.propyleneglycol  # used medium in pressure bus


branches = {
    "measurement" : { 
        "type": NivelationBranch,
        "reference_leaf" : 0x1f,
        "leaves" : {  # do not include reference
            0x01                : "nivelation",
            0x02                : "nivelation",
            0x03                : "nivelation",
        },
        "medium" : Medium.propyleneglycol,
        "column_avg_samples": 10  # samples
    }
}