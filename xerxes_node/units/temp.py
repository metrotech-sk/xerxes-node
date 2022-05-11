#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .unit import Unit

class Temperature(Unit):
    def __init__(self, kelvin=0):
        super().__init__(kelvin)

    @property
    def kelvin(self):
        return self.value


    @property
    def celsius(self):
        return self.value - 273.15


    @property
    def fahrenheit(self):
        return (self.celsius * 9 / 5) + 32

    
    @staticmethod
    def from_milli_kelvin(mK):
        return Temperature(mK/1000)


    def __repr__(self):
        return f"Temperature({self._value})"


class Celsius(Temperature):
    def __init__(self, celsius=0):
        super().__init__(celsius + 273.15)
    

    @property
    def preffered(self):
        return self.celsius


class Kelvin(Temperature):
    def __init__(self, kelvin=0):
        super().__init__(kelvin)
    

    @property
    def preffered(self):
        return self.kelvin