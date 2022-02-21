#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Unit:
    _value = 0

    def __init__(self, value=0):
        self._value = value
    
    @property
    def value(self):
        return self._value