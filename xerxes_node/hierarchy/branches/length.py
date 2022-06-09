#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from typing import Dict, List
from xerxes_node.hierarchy.branches.branch import Branch
from xerxes_node.hierarchy.leaves.leaf import EmptyBufferError
from xerxes_node.hierarchy.leaves.length import LengthLeaf


class LengthBranch(Branch):         
    def __repr__(self):
        return f"LengthBranch(leaves={self._leaves}, name={self._name})"
    
    def read(self) -> Dict:
        readings = dict()
        
        for leaf in self._leaves:
            # try to read all values from leaf and append a average of such values into dictionary
            try:
                avg_of_readings = LengthLeaf.average(
                    readings=leaf.pop_all()
                )    
                readings[leaf.address] = avg_of_readings
            except EmptyBufferError:
                log.error(f"No data from ILeaf {leaf.address}")
        
        return readings
    
    def to_dict(self) -> Dict:
        to_return = dict()
        averages = self.read()
        for key in averages:
            to_return[hex(key)] = LengthLeaf.to_dict(averages[key])

        return to_return