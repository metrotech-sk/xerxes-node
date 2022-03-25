#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List
from xerxes_node.hierarchy.branch import Branch
from xerxes_node.hierarchy.pleaf import PLeaf
from xerxes_node.network import XerxesNetwork


class NivelationBranch(Branch):
    def __init__(self, leaves: List, network: XerxesNetwork, name: str, reference_leaf: PLeaf):
        super().__init__(leaves, network, name)
        self._ref_leaf = reference_leaf
        