#!/usr/bin/env python3
# -*- coding: utf-8 -*-


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = None  # insert URI here
use_database = "test" # "pri_sajbach"
sample_period = 1  # how often read sensors, [s]
port_timeout = 0.1
network_timeout = 0.5  # read until, [s]
update_period = 60  # how often to push to DB, [s]
use_device = "/dev/ttyUSB0"  # device used for communication
