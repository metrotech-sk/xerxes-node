#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_node.units.nivelation import Nivelation
from xerxes_node.leaves.leaf_template import Leaf
from xerxes_node.units.temp import Temperature
import struct

g=9.80665

def conv_ethyleneglycol(Pa):
    return Pa/(g*1.1132)

def conv_water(Pa):
    return Pa/g

def conv_siloxane(Pa):
    return Pa/(g*0.965)

class Medium:
    WATER=0
    ETHYLENEGLYCOL=1
    SILOXANE=2


class PLeaf(Leaf):
    def __init__(self, channel, my_addr: int, std_timeout: float, *, t_ext1=False, t_ext2=False, medium: Medium = Medium.WATER):
        super().__init__(channel, my_addr, std_timeout)

        if medium == Medium.ETHYLENEGLYCOL:
            self.conv_func = conv_ethyleneglycol
        elif medium == Medium.SILOXANE:
            self.conv_func = conv_siloxane
        else:
            self.conv_func = conv_water
        
        self.t_ext1 = t_ext1
        self.t_ext2 = t_ext2


    def read(self) -> list:
        reply = self.exchange([0])
        reply = bytes([ord(i) for i in reply.payload])

        # unpack 4 uint32_t's
        values = struct.unpack("!IIII", reply)

        # convert to sensible units
        result = [
            Nivelation(values[0]/10, self.conv_func),
            Temperature.from_milli_kelvin(values[1]),
        ]
        if self.t_ext1:
            result.append(
                Temperature.from_milli_kelvin(values[2]),
            )
        if self.t_ext2:
            result.append(
                Temperature.from_milli_kelvin(values[3]),
            )
        
        return result
    
    def read_dict(self):
        vals = self.read()
        dict_repr = {
            "nivelation": vals[0].mm,
            "temp_sens": vals[1].Celsius,
        }
        if self.t_ext1:
            dict_repr["temp_ext1"] = vals[2].Celsius, 
            
        if self.t_ext1:
            dict_repr["temp_ext2"] = vals[3].Celsius, 
            
        return dict_repr

