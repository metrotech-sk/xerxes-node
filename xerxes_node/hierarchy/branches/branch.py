#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List

from xerxes_node.hierarchy.leaves.leaf import Leaf


class Branch:
    def __init__(self, leaves: List[Leaf], name: str):
        self._leaves = leaves
        self._name = name
        self.readings = {}
        
    @property
    def name(self):
        return str(self._name)
    
    @name.setter
    def name(self, val):
        raise NotImplementedError
        
    def __iter__(self):
        self._lv_it = 0
        return self
  
    def __next__(self):
        if self._lv_it == len(self._leaves):
            raise StopIteration
        next_leaf = self._leaves[self._lv_it]
        self._lv_it += 1
        return next_leaf
    
    def __repr__(self):
        return f"Branch(leaves={self._leaves}, name={self._name})"
    
    def read(self) -> None:
        raise NotImplementedError