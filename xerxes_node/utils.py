#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
log = logging.getLogger(__name__)
import os
from xerxes_node.hierarchy.leaves.leaf import Leaf


def discover(comm, leaves, addr_range=32):
    found_addresses = []

    for i in range(3):
        for addr in range(1, addr_range):
            if addr in found_addresses:
                continue

            try:
                if addr not in found_addresses:
                    tmp_leaf = Leaf(comm, addr, 0.020)
                    tmp_leaf.ping()
                    found_addresses.append(addr)
                    leaves.append(tmp_leaf)
                    log.info(f"leaf: {addr} found!")
            except TimeoutError:
                log.debug(f"Addr {addr} unavailable.")
    return found_addresses


def get_cpu_temp_celsius():
    if os.access("/sys/class/thermal/thermal_zone0/temp", os.R_OK):
        with open ("/sys/class/thermal/thermal_zone0/temp", "r") as tf:
            cpu_temp = int(tf.read())
        return cpu_temp/1000
    else:
        return None