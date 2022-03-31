#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pprint import pprint
from typing import Dict, List
from xerxes_node.hierarchy.leaves.pleaf import AveragePLeafData, PLeaf


class NivelationParser:
    @staticmethod
    def to_dict(averages: Dict, reference_value: float):
        to_return = dict()
        for key in averages:
            to_return[hex(key)] = PLeaf.to_dict(averages[key], offset=reference_value)

        to_return["fluid_column_height"] = reference_value
        return to_return