#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .pressure import Pressure

class Nivelation(Pressure):
    def __init__(self, value=0, conv_func=1):
        self._conversion = conv_func
        super().__init__(value)

    @property
    def mm(self):
        return self._conversion(self.value)