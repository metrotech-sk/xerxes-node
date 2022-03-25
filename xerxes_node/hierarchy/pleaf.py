#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, is_dataclass
from typing import Callable, List
from xerxes_node.units.nivelation import Nivelation
from xerxes_node.hierarchy.leaf import Leaf
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
    def __init__(self, channel, my_addr: int, std_timeout: float, *, medium: Callable):
        super().__init__(channel, my_addr, std_timeout)

        self.conv_func = medium
        
    @staticmethod
    def from_list(channel, addresses: List, std_timeout: float, medium: Callable) -> List:
        pleaves = []
        for addr in addresses:
            pleaves.append(
                PLeaf(
                    channel=channel,
                    my_addr=addr,
                    std_timeout=std_timeout,
                    medium=medium
                    )
            )
        return pleaves
        
    def read(self) -> list:
        reply = self.exchange([0])
        reply = bytes([ord(i) for i in reply.payload])

        # unpack 4 uint32_t's
        values = struct.unpack("!IIII", reply)

        # convert to sensible units
        result = PLeafData(
            addr=self.address,
            nivelation=Nivelation(values[0]/1000, self.conv_func),  # pressure in 
            temperature_sensor=Temperature.from_milli_kelvin(values[1]),
            temperature_external_1=Temperature.from_milli_kelvin(values[2]),
            temperature_external_2=Temperature.from_milli_kelvin(values[3])
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
        