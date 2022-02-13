#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os
cppyy.add_include_path("cpp/include")
[cppyy.include(i) for i in os.listdir("cpp/include")]
cppyy.add_library_path("./build")
cppyy.load_library("libxerxes")
from cppyy.gbl import Xerxes

