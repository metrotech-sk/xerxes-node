#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.command.config import config
from statistics import mean, median, stdev
import time
import serial, struct

from xerxes_node.ids import MsgId
from xerxes_node.hierarchy.leaves.leaf import  NetworkError
from xerxes_node.hierarchy.leaves.pleaf import PLeaf, PLeafData
from xerxes_node.network import Addr, XerxesNetwork
from xerxes_node import config


my_addr = b"\x00"

def b2i(data: bytes) -> int:
    return int(data.hex(), 16)


def s2b(data: int) -> bytes:
    return data.to_bytes(1, "big")



class XerxesLeaf:
    def __init__(self, address: int, serial_port: XerxesNetwork) -> None:
        self.com = serial_port
        self.addr = address

    
    def read(self) -> bytes:
        self.com.send_msg(self.addr.to_bytes(1, "big"), MsgId.FETCH_MEASUREMENT.bytes)
        rpl = self.com.read_msg()
        return rpl.payload, rpl.message_id
    

class PressureLeaf(XerxesLeaf):
    def read(self) -> list:
        pl, msgid = super().read()
        p, ts, te1, te2 = struct.unpack("!ffff", pl)
        return [p, ts, te1, te2], msgid


class StrainLeaf(XerxesLeaf):
    def read(self) -> list:
        pl, msgid = super().read()
        s, te1, te2 = struct.unpack("!III", pl)
        return [s, te1, te2], msgid


class DistanceLeaf(XerxesLeaf):
    def read(self) -> list:
        pl, msgid = super().read()
        d, te1, te2 = struct.unpack("!III", pl)
        return [d, te1, te2], msgid


class AngleLeaf(XerxesLeaf):
    def read(self) -> list:
        pl, msgid = super().read()
        x, y, te1, te2 = struct.unpack("!ffff", pl)
        return [x, y, te1, te2], msgid


def leaf_generator(devId: int, address: int, serial_port: serial.Serial) -> XerxesLeaf:
    #define DEVID_PRESSURE_600MBAR_2TEMP    0x03
    #define DEVID_PRESSURE_60MBAR_2TEMP     0x04    
    #define DEVID_STRAIN_24BIT_2TEMP        0x05

    if isinstance(devId, bytes):
        devId = b2i(devId)

    if devId == 0x03 or devId == 0x04:
        return PressureLeaf(
            address=address,
            serial_port=serial_port
        )

    elif devId == 0x11:
        return StrainLeaf(
            address=address,
            serial_port=serial_port
            )

    elif devId == 0x40:
        return DistanceLeaf(
            address=address,
            serial_port=serial_port
            )

    elif devId == 0x30:
        return AngleLeaf(
            address=address,
            serial_port=serial_port
            )

    else:
        return XerxesLeaf(
            address=address,
            serial_port=serial_port
            )
          

if __name__ == "__main__":
    XN = XerxesNetwork(
        port = config.use_device,
        baudrate=115_200,
        timeout=config.sensor_timeout,
        my_addr=0x00
    )


    leaves = []
    addresses = [Addr(i) for i in range(1, 32)]

    
    while addresses:
        addr = addresses.pop()

        try:
            l = PLeaf(
                channel=XN,
                addr=addr,
                medium=config.used_medium
            )
            ping = l.ping()
            leaves.append(l)
            print(f"Device {l.addr} found on network, ping: {ping*1000}ms")
            
        except TimeoutError:
            print(addr, "timeouted")
        
        except NetworkError:
            print(addr, "sent wrong reply")
        

    while 1:
        start = time.time()
        for leaf in leaves:
            try:
                reading: PLeafData = leaf.read()
                print(f"{leaf.addr} replied with: {reading.nivelation.mm}mm, {reading.temperature_sensor.preffered}°C.")
            except TimeoutError:
                print(f"{leaf.addr} timeouted...")
            except IOError:
                pass
            except ValueError:
                pass
        print(time.time() - start)
        time.sleep(1)
        