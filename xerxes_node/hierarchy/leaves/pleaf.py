#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, is_dataclass
from typing import Callable, List
from xerxes_node.ids import MsgId
from xerxes_node.medium import Medium
from xerxes_node.network import Addr, FutureXerxesNetwork, XerxesNetwork
from xerxes_node.units.nivelation import Nivelation
from xerxes_node.hierarchy.leaves.leaf import Leaf, LeafData, LengthError
from xerxes_node.units.temp import Celsius, Temperature
import struct


@dataclass
class PLeafData(LeafData):
    nivelation: Nivelation
    temperature_sensor: Celsius
    temperature_external_1: Celsius
    temperature_external_2: Celsius

@dataclass
class AveragePLeafData:
    nivelation: Nivelation
    temperature_sensor: Celsius
    temperature_external_1: Celsius
    temperature_external_2: Celsius
    invalid: int


class PLeaf(Leaf):
    def __init__(self, addr: Addr, *, channel: XerxesNetwork=FutureXerxesNetwork,  medium: Callable = Medium.water):
        super().__init__(
            addr=addr, 
            channel=channel
        )

        self.conv_func = medium
        
    def __repr__(self):
        return f"PLeaf(channel={self.channel}, addr={self.address}, medium={self.conv_func})"
    
        
    def read(self):
        reply = self.exchange(MsgId.FETCH_MEASUREMENT.to_bytes())

        # unpack 4 uint32_t's
        values = struct.unpack("!ffff", reply.payload)  # unpack 4 floats: presure + 3x temp.

        # convert to sensible units
        return PLeafData(
            addr=self.address,
            nivelation=Nivelation(values[0], self.conv_func),  # pressure in 
            temperature_sensor=Celsius(values[1]),
            temperature_external_1=Celsius(values[2]),
            temperature_external_2=Celsius(values[3])
        )
        
        
    def fetch(self):
        self._readings.append(self.read())
            
    
    @staticmethod
    def average(readings: List[PLeafData]) -> AveragePLeafData:
        arrlen = len(readings)
        invalid = 0
        valid = 0

        if arrlen<1:
            raise LengthError("Unable to calculate average from empty list")
        
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
            nivelation=Nivelation(sum(n)/valid, conv_func=n[0]._conversion),
            temperature_sensor=Temperature(sum(ts)/valid),
            temperature_external_1=Temperature(sum(t1)/valid),
            temperature_external_2=Temperature(sum(t2)/valid),
            invalid=invalid
        )
        

    @staticmethod
    def to_dict(readings: AveragePLeafData, offset: float):
        if isinstance(readings, type(None)):
            return None

        to_return = {
            "nivelation_raw": readings.nivelation.preffered,
            "nivelation": readings.nivelation.preffered - offset,
            "temp_sens": readings.temperature_sensor.celsius,
            "temp_ext1": readings.temperature_external_1.celsius,
            "temp_ext2": readings.temperature_external_2.celsius,
            "errors": readings.invalid
        }

        return to_return
        
        
def pleaves_from_list(addresses: List[int], medium: Callable, channel: XerxesNetwork = FutureXerxesNetwork) -> List[PLeaf]:
    pleaves = []
    for addr_n in addresses:
        pleaves.append(
            PLeaf(
                channel=channel,
                addr=Addr(addr_n),
                medium=medium
            )
        )
    return pleaves