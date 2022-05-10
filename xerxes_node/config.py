#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_node.medium import Medium


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = "mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority"
use_database = "pri_sajbach_v1.2"
sample_period = 1
update_period = 60
use_device = "/dev/ttyS0"
used_medium = Medium.propyleneglycol

sensor_timeout=0.005

reference_leaf_addr = 0x1f
leaves = {
    0x01                : "nivelation",
    0x02                : "nivelation",
    0x03                : "nivelation",
    reference_leaf_addr : "nivelation"  # also reference
}