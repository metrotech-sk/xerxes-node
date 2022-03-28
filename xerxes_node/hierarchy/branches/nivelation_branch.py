#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Dict, List
from xerxes_node.hierarchy.branches.branch import Branch
from xerxes_node.hierarchy.leaves.leaf import LengthError
from xerxes_node.hierarchy.leaves.pleaf import PLeaf, PLeafData


class NivelationBranch(Branch):
    def __init__(self, leaves: List[PLeaf], name: str, reference_leaf: PLeaf):
        self._ref_leaf = reference_leaf
        leaves.append(reference_leaf)
        super().__init__(leaves, name)
        
    @property
    def ref_addr(self):
        return self._ref_leaf.address
        
    def __repr__(self):
        return f"Branch(leaves={self._leaves}, name={self._name}, reference_leaf={self._ref_leaf})"
    
    def read(self) -> Dict:
        readings = dict()
        
        for leaf in self._leaves:
            try:
                readings[leaf.address] = PLeaf.average(
                    readings=leaf.pop_all()
                )    
            except LengthError:
                pass
        
        return readings
        