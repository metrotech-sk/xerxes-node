#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, is_dataclass
from typing import List
from xerxes_node.ids import MsgId
from xerxes_node.network import Addr
from xerxes_node.hierarchy.leaves.leaf import EmptyBufferError, Leaf, LeafData
from xerxes_node.units.length import Length
from xerxes_node.units.temp import Celsius, Temperature
import struct


@dataclass
class LengthLeafData(LeafData):
    length: Length
    temperature_external_1: Celsius
    temperature_external_2: Celsius

@dataclass
class AverageLengthLeafData:
    length: Length
    temperature_external_1: Celsius
    temperature_external_2: Celsius
    invalid: int


class LengthLeaf(Leaf):
    def read(self) -> LengthLeafData:
        reply = self.exchange(MsgId.FETCH_MEASUREMENT.to_bytes())

        # unpack 4 uint32_t's
        values = struct.unpack("!fff", reply.payload)  # unpack 4 floats: ang_x, ang_y, temp_e1, temp_e2

        # convert to sensible units
        return LengthLeafData(
            length=Length(values[0]),
            temperature_external_1=Celsius(values[1]),
            temperature_external_2=Celsius(values[2])
        )
        
    
    def fetch(self) -> None:
        self._readings.append(self.read())
            
            
    def __repr__(self):
        return f"LengthLeaf(channel={self.channel}, addr={self.address})"
    
    @staticmethod
    def average(readings: List[LengthLeafData]) -> AverageLengthLeafData:
        arrlen = len(readings)
        invalid = 0
        valid = 0

        if arrlen<1:
            raise EmptyBufferError("Unable to calculate average from empty list")
        
        l, t1, t2 = [], [], [], []
        for r in readings:
            if is_dataclass(r):
                l.append(r.length)
                t1.append(r.temperature_external_1)
                t2.append(r.temperature_external_2)
                valid += 1
            else:
                invalid += 1

        if valid == 0:
            raise ValueError("No valid data received")

        return AverageLengthLeafData(
            length=Length(sum(l)/valid),
            temperature_external_1=Temperature(sum(t1)/valid),
            temperature_external_2=Temperature(sum(t2)/valid),
            invalid=invalid
        )
        

    @staticmethod
    def to_dict(readings: AverageLengthLeafData):
        if isinstance(readings, type(None)):
            return None

        to_return = {
            "length": readings.length.m,
            "temp_ext1": readings.temperature_external_1.celsius,
            "temp_ext2": readings.temperature_external_2.celsius,
            "errors": readings.invalid
        }

        return to_return
        
        
def length_leaves_from_list(channel, addresses: List[int]) -> List[LengthLeaf]:
    lleaves = []
    for addr_n in addresses:
        lleaves.append(
            LengthLeaf(
                channel=channel,
                addr=Addr(addr_n)
            )
        )
    return lleaves