#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy
cppyy.add_include_path("wiringpi-cpp/")
cppyy.include("test.cpp")
cppyy.add_library_path("build/")
cppyy.load_library("libxerxes")
from cppyy.gbl import v_std_dev