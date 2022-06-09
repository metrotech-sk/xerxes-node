#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List
from xerxes_node.hierarchy.branches.branch import Branch
from xerxes_node.hierarchy.leaves.ileaf import ILeaf

import logging
from xerxes_node.hierarchy.leaves.leaf import EmptyBufferError

from xerxes_node.network import LengthError
log = logging.getLogger(__name__)


class InclinationBranch(Branch):         
    def __repr__(self):
        return f"InclinationBranch(leaves={self._leaves}, name={self._name})"
    
    def read(self) -> Dict:
        readings = dict()
        
        for leaf in self._leaves:
            # try to read all values from leaf and append a average of such values into dictionary
            try:
                avg_of_readings = ILeaf.average(
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
            to_return[hex(key)] = ILeaf.to_dict(averages[key])

        return to_return