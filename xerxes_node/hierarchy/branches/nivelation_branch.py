#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import statistics
from typing import Dict, List
from xerxes_node.hierarchy.branches.branch import Branch
from xerxes_node.hierarchy.leaves.leaf import LengthError
from xerxes_node.hierarchy.leaves.pleaf import PLeaf


class NivelationBranch(Branch):
    def __init__(self, leaves: List[PLeaf], name: str, reference_leaf: PLeaf, column_avg_samples: int):
        self._ref_leaf = reference_leaf
        leaves.append(reference_leaf)
        self.fluid_column_buffer = []
        self._n_of_samples = column_avg_samples
        super().__init__(leaves, name)
        
    @property
    def ref_addr(self) -> int:
        return self._ref_leaf.address
        
    def __repr__(self):
        return f"Branch(leaves={self._leaves}, name={self._name}, reference_leaf={self._ref_leaf}, column_avg_samples={self._n_of_samples})"
    
    def read(self) -> Dict:
        readings = dict()
        
        for leaf in self._leaves:
            try:
                # try to read all values from leaf and append a average of such values into dictionary
                avg_of_readings = PLeaf.average(
                    readings=leaf.pop_all()
                )    
                readings[leaf.address] = avg_of_readings

                # append average to the column height buffer
                if leaf is self._ref_leaf:
                    self.fluid_column_buffer.insert(0, avg_of_readings.nivelation.preferred)

                    # if buffer is full, remove last value:
                    if len(self.fluid_column_buffer) > self._n_of_samples:
                        self.fluid_column_buffer.pop()

            except LengthError:
                pass
        
        return readings
        
    @property
    def column_height(self) -> float:
        if len(self.fluid_column_buffer) == 0:
            return 0
        else:
            return statistics.mean(self.fluid_column_buffer)
    
    @column_height.setter
    def column_height(self, val:None):
        raise NotImplementedError("Column height should never be set directly")