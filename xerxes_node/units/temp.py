#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .unit import Unit

class Temperature(Unit):
    @property
    def Celsius(self):
        return self.value - 273.15

    @property
    def Kelvin(self):
        return self.value

    @property
    def Fahrenheit(self):
        return (self.Celsius * 9 / 5) + 32
    
    @staticmethod
    def from_milli_kelvin(mK):
        return Temperature(mK/1000)

    def __repr__(self):
        return f"Temperature({self._value})"
    
    @property
    def preffered(self):
        return self.Celsius