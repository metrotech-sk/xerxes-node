#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, is_dataclass
from typing import List
from xerxes_node.ids import MsgId
from xerxes_node.network import Addr
from xerxes_node.units.angle import Angle
from xerxes_node.hierarchy.leaves.leaf import EmptyBufferError, Leaf, LeafData
from xerxes_node.units.temp import Celsius, Temperature
import struct


@dataclass
class ILeafData(LeafData):
    angle_x: Angle
    angle_y: Angle
    temperature_external_1: Celsius
    temperature_external_2: Celsius

@dataclass
class AverageILeafData:
    angle_x: Angle
    angle_y: Angle
    temperature_external_1: Celsius
    temperature_external_2: Celsius
    invalid: int


class ILeaf(Leaf):
    def read(self) -> ILeafData:
        reply = self.exchange(MsgId.FETCH_MEASUREMENT.to_bytes())

        # unpack 4 uint32_t's
        values = struct.unpack("!ffff", reply.payload)  # unpack 4 floats: ang_x, ang_y, temp_e1, temp_e2

        # convert to sensible units
        return ILeafData(
            angle_x=Angle.from_degrees(values[0]),
            angle_y=Angle.from_degrees(values[1]),
            temperature_external_1=Celsius(values[2]),
            temperature_external_2=Celsius(values[3])
        )
        
    
    def fetch(self) -> None:
        self._readings.append(self.read())
            
            
    def __repr__(self):
        return f"ILeaf(channel={self.channel}, addr={self.address})"
    
    @staticmethod
    def average(readings: List[ILeafData]) -> AverageILeafData:
        arrlen = len(readings)
        invalid = 0
        valid = 0

        if arrlen<1:
            raise EmptyBufferError("Unable to calculate average from empty list")
        
        x, y, t1, t2 = [], [], [], []
        for r in readings:
            if is_dataclass(r):
                x.append(r.angle_x)
                y.append(r.angle_y)
                t1.append(r.temperature_external_1)
                t2.append(r.temperature_external_2)
                valid += 1
            else:
                invalid += 1

        if valid == 0:
            raise ValueError("No valid data received")

        return AverageILeafData(
            angle_x=Angle(sum(x)/valid),
            angle_y=Angle(sum(y)/valid),
            temperature_external_1=Temperature(sum(t1)/valid),
            temperature_external_2=Temperature(sum(t2)/valid),
            invalid=invalid
        )
        

    @staticmethod
    def to_dict(readings: AverageILeafData):
        if isinstance(readings, type(None)):
            return None

        to_return = {
            "angle_x": readings.angle_x.degrees,
            "angle_y": readings.angle_y.degrees,
            "temp_ext1": readings.temperature_external_1.celsius,
            "temp_ext2": readings.temperature_external_2.celsius,
            "errors": readings.invalid
        }

        return to_return
        
        
def ileaves_from_list(channel, addresses: List[int]) -> List[ILeaf]:
    ileaves = []
    for addr_n in addresses:
        ileaves.append(
            ILeaf(
                channel=channel,
                addr=Addr(addr_n)
            )
        )
    return ileaves