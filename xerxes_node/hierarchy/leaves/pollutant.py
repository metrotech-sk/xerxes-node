#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncore import read
from dataclasses import dataclass, is_dataclass
from pdb import pm
from typing import List, Union
from xerxes_node.ids import MsgId
from xerxes_node.network import Addr
from xerxes_node.units.density import Fraction, Density
from xerxes_node.hierarchy.leaves.leaf import EmptyBufferError, Leaf, LeafData
from xerxes_node.units.temp import Celsius, Temperature
import struct

from xerxes_node.units.unit import Index


@dataclass
class PollutantLeafData(LeafData):
    pm1: Density
    pm2_5: Density
    pm4: Density
    pm10: Density
    humidity: Fraction
    temperature_internal: Celsius
    VOC_index: Index
    NOX_index: Index

@dataclass
class AveragePollutantLeafData:
    pm1: Density
    pm2_5: Density
    pm4: Density
    pm10: Density
    humidity: Fraction
    temperature_internal: Celsius
    VOC_index: Index
    NOX_index: Index
    invalid: int


class PollutantLeaf(Leaf):
    def read(self) -> PollutantLeafData:
        reply = self.exchange(MsgId.FETCH_MEASUREMENT.to_bytes())

        # unpack 4 uint32_t's
        values = struct.unpack("!ffffffff", reply.payload)  # unpack 8 floats: pm1? pm2.5, pm4, pm10, rh, temp, voc, nox

        # convert to sensible units
        return PollutantLeafData(
            pm1=Density.from_ug_per_m3(values[0]),
            pm2_5=Density.from_ug_per_m3(values[1]),
            pm4=Density.from_ug_per_m3(values[2]),
            pm10=Density.from_ug_per_m3(values[3]),
            humidity=Fraction.from_percent(values[4]),
            temperature_internal=Celsius(values[5]),
            VOC_index=Index(values[6]),
            NOX_index=Index(values[7])
        )
        
    
    def fetch(self) -> None:
        self._readings.append(self.read())
            
            
    def __repr__(self):
        return f"PollutantLeaf(channel={self.channel}, addr={self.address})"
    
    @staticmethod
    def average(readings: List[PollutantLeafData]) -> AveragePollutantLeafData:
        arrlen = len(readings)
        invalid = 0
        valid = 0

        if arrlen<1:
            raise EmptyBufferError("Unable to calculate average from empty list")
        
        pm1, pm2_5, pm4, pm10, rh, t, voc, nox = ([] for i in range(8))
        for r in readings:
            if is_dataclass(r):
                pm1.append(r.pm1)
                pm2_5.append(r.pm2_5)
                pm4.append(r.pm4)
                pm10.append(r.pm10)
                rh.append(r.humidity)
                t.append(r.temperature_internal)
                voc.append(r.VOC_index)
                nox.append(r.NOX_index)
                valid += 1
            else:
                invalid += 1

        if valid == 0:
            raise ValueError("No valid data received")

        return AveragePollutantLeafData(
            pm1=Density(sum(pm1)/valid),
            pm2_5=Density(sum(pm2_5)/valid),
            pm4=Density(sum(pm4)/valid),
            pm10=Density(sum(pm10)/valid),
            humidity=Fraction(sum(rh)/valid),
            temperature_internal=Temperature(sum(t)/valid),
            VOC_index=Index(sum(voc)/valid),
            NOX_index=Index(sum(nox)/valid),
            invalid=invalid
        )
        

    @staticmethod
    def to_dict(readings: Union[AveragePollutantLeafData, None]):
        if isinstance(readings, type(None)):
            return None

        to_return = {
            "PM1":          readings.pm1.ug_per_m3,
            "PM2_5":        readings.pm2_5.ug_per_m3,
            "PM4":          readings.pm4.ug_per_m3,
            "PM10":         readings.pm10.ug_per_m3,
            "humidity":     readings.humidity.percent,
            "temperature":  readings.temperature_internal.celsius,
            "VOC":          readings.VOC_index.value,
            "NOx":          readings.NOX_index.value,
            "units": "PMx[ug/m3], humidity[%], temperature[°C], VOC/NOx[index]",
            "errors": readings.invalid
        }

        return to_return
        
        
def pollutant_leaves_from_list(channel, addresses: List[int]) -> List[PollutantLeaf]:
    pol_leaves = []
    for addr_n in addresses:
        pol_leaves.append(
            PollutantLeaf(
                channel=channel,
                addr=Addr(addr_n)
            )
        )
    return pol_leaves