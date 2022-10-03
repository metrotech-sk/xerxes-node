#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
log = logging.getLogger(__name__)
import os


def get_cpu_temp_celsius():
    if os.access("/sys/class/thermal/thermal_zone0/temp", os.R_OK):
        with open ("/sys/class/thermal/thermal_zone0/temp", "r") as tf:
            cpu_temp = int(tf.read())
        return cpu_temp/1000
    else:
        return None