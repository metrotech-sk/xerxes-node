#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from xerxes_node.network import XerxesNetwork


class Branch:
    def __init__(self, leaves: List, network: XerxesNetwork, name: str):
        self._leaves = leaves
        self._network = network
        self._name = name