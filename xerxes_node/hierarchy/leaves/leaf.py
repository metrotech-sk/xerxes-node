#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import os
import struct
import time
from typing import List
from xerxes_node.ids import DevId, MsgId

from xerxes_node.network import Addr, FutureXerxesNetwork, XerxesMessage, XerxesNetwork, NetworkError

import logging
log = logging.getLogger(__name__)



class EmptyBufferError(Exception): ...


@dataclass
class LeafData(object): ...
    # addr: int


class Leaf:
    def __init__(self, addr: Addr, channel: XerxesNetwork=FutureXerxesNetwork):
        assert(isinstance(addr, Addr))
        self._address = addr

        self.channel: XerxesNetwork
        self.assign_channel(channel)

        self._readings = []


    def ping(self):
        return self.channel.ping(self._address.to_bytes())


    def exchange(self, payload: bytes) -> XerxesMessage:
        # test if payload is list of uchars
        assert isinstance(payload, bytes)
        self.channel.send_msg(self._address, payload)
        return self.channel.read_msg()
        
    
    def read(self) -> XerxesMessage:
        return self.exchange(MsgId.FETCH_MEASUREMENT.bytes)
    
    
    def read_reg(self, reg_addr: int, length: int) -> bytes:
        length = int(length)
        reg_addr = int(reg_addr)
        payload = MsgId.READ_REQ.to_bytes() + reg_addr.to_bytes(1, "big") + length.to_bytes(1, "big")
        return self.exchange(payload)
    
    
    def write_reg(self, reg_addr: int, value: bytes) -> bytes:
        reg_addr = int(reg_addr)
        payload = MsgId.SET.to_bytes() + reg_addr.to_bytes(1, "big") + value
        return self.exchange(payload)


    def fetch(self):
        self._readings.append(self.read())


    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, val):
        raise NotImplementedError("Address should not be changed")

    def assign_channel(self, channel):
        assert("send_msg" in dir(channel))
        assert("read_msg" in dir(channel))
        self.channel = channel

    def __repr__(self) -> str:
        return f"Leaf(channel={self.channel}, address={self._address})"

    def pop(self) -> LeafData:
        return self._readings.pop()

    def pop_all(self) -> List[LeafData]:
        readings = list(self._readings)
        self._readings = list()
        return readings
