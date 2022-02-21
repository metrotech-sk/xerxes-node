#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .unit import Unit

class Pressure(Unit):
    @property
    def mmH2O(self):
        return self.value * 0.10197162129779283

    @property
    def bar(self):
        return self.value * 0.00001

    @property
    def pascal(self):
        return self._value
    
    @staticmethod
    def from_micro_bar(ubar):
        return Pressure(ubar/10)
