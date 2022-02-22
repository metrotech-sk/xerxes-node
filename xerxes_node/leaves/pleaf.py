#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncore import read
from multiprocessing.sharedctypes import Value
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
    def __init__(self, channel, my_addr: int, std_timeout: float, *, medium: Medium = Medium.WATER):
        super().__init__(channel, my_addr, std_timeout)

        if medium == Medium.ETHYLENEGLYCOL:
            self.conv_func = conv_ethyleneglycol
        elif medium == Medium.SILOXANE:
            self.conv_func = conv_siloxane
        else:
            self.conv_func = conv_water
        
    def read(self) -> list:
        reply = self.exchange([0])
        reply = bytes([ord(i) for i in reply.payload])

        # unpack 4 uint32_t's
        values = struct.unpack("!IIII", reply)

        # convert to sensible units
        result = [
            Nivelation(values[0]/10, self.conv_func),
            Temperature.from_milli_kelvin(values[1]),
            Temperature.from_milli_kelvin(values[2]),
            Temperature.from_milli_kelvin(values[3]),
        ]
        
        return result

    
    @staticmethod
    def average(readings):
        arrlen = len(readings)
        invalid = 0
        valid = 0

        if arrlen<1:
            raise ValueError("Unable to calculate average from empty list")
        
        n, ts, t1, t2 = [], [], [], []
        for r in readings:
            if isinstance(r, list):
                n.append(r[0])
                ts.append(r[1])
                t1.append(r[2])
                t2.append(r[3])
                valid += 1
            else:
                invalid += 1

        if valid == 0:
            raise ValueError("No valid data received")

        return Nivelation(sum(n)/valid), Temperature(sum(ts)/valid), Temperature(sum(t1)/valid), Temperature(sum(t2)/valid), invalid

    @staticmethod
    def to_dict(readings):
        if isinstance(readings[0], type(None)):
            return None

        to_return = {
            "nivelation": readings[0].preffered,
            "temp_sens": readings[1].preffered,
            "temp_ext1": readings[2].preffered,
            "temp_ext2": readings[3].preffered,
            "errors": readings[4]
        }

        return to_return
        