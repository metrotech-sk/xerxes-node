#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, is_dataclass
from pprint import pprint
from typing import List
from xerxes_node.ids import MsgId
from xerxes_node.medium import Medium
from xerxes_node.units.nivelation import Nivelation
from xerxes_node.leaves.leaf_template import Leaf
from xerxes_node.units.temp import Temperature
import struct


@dataclass
class PLeafData:
    addr: int
    nivelation: Nivelation
    temperature_sensor: Temperature
    temperature_external_1: Temperature
    temperature_external_2: Temperature

@dataclass
class AveragePLeafData:
    nivelation: Nivelation
    temperature_sensor: Temperature
    temperature_external_1: Temperature
    temperature_external_2: Temperature
    invalid: int


class PLeaf(Leaf):
    def __init__(self, channel, my_addr: int, std_timeout: float, *, medium: Medium = Medium.water):
        super().__init__(channel, my_addr, std_timeout)

        self.conv_func = medium
        
    def read(self) -> list:
        reply = self.exchange(MsgId.FETCH_MEASUREMENT.to_bytes(2, "big"))
        reply = bytes([ord(i) for i in reply.payload])
        print(reply, len(reply))

        # unpack 4 uint32_t's
        values = struct.unpack("!ffff", reply)  # unpack 4 floats: presure + 3x temp.

        # convert to sensible units
        result = PLeafData(
            addr=self.address,
            nivelation=Nivelation(values[0], self.conv_func),  # pressure in 
            temperature_sensor=Temperature(values[1]),
            temperature_external_1=Temperature(values[2]),
            temperature_external_2=Temperature(values[3])
        )
        
        return result

    
    @staticmethod
    def average(readings: List[PLeafData]):
        arrlen = len(readings)
        invalid = 0
        valid = 0

        if arrlen<1:
            raise ValueError("Unable to calculate average from empty list")
        
        n, ts, t1, t2 = [], [], [], []
        for r in readings:
            # type(r) == PLeafData
            if is_dataclass(r):
                n.append(r.nivelation)
                ts.append(r.temperature_sensor)
                t1.append(r.temperature_external_1)
                t2.append(r.temperature_external_2)
                valid += 1
            else:
                invalid += 1

        if valid == 0:
            raise ValueError("No valid data received")

        return AveragePLeafData(
            Nivelation(sum(n)/valid, conv_func=n[0]._conversion),
            Temperature(sum(ts)/valid),
            Temperature(sum(t1)/valid),
            Temperature(sum(t2)/valid),
            invalid
        )
        

    @staticmethod
    def to_dict(readings: AveragePLeafData, offset: float):
        if isinstance(readings, type(None)):
            return None

        to_return = {
            "nivelation_raw": readings.nivelation.preffered,
            "nivelation": readings.nivelation.preffered - offset,
            "temp_sens": readings.temperature_sensor.preffered,
            "temp_ext1": readings.temperature_external_1.preffered,
            "temp_ext2": readings.temperature_external_2.preffered,
            "errors": readings.invalid
        }

        return to_return
        