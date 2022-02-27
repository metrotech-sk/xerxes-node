#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from xerxes_node.leaves.pleaf import PLeaf


class Parser:
    @staticmethod
    def to_dict(averages, reference_addr):
        to_return = dict()
        # PLeaf.to_dict()
        for key in averages:
            # TODO: toto dole nie je pekné, prepísať @themladypan
            to_return[hex(key)] = PLeaf.to_dict(averages[key], averages[reference_addr][0].preffered)

        return to_return