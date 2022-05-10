#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from xerxes_node.ids import MsgId

from xerxes_node.network import Addr, XerxesNetwork

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)


class NetworkError(Exception): ...


class Leaf:
    def __init__(self, channel: XerxesNetwork, address: Addr):
        assert(isinstance(address, Addr))
        self._address = address

        self.channel: XerxesNetwork
        self.assign_channel(channel)



    @property
    def addr(self):
        return self._address


    @addr.setter
    def addr(self, __v):
        raise NotImplementedError



    def ping(self):
        start = time.monotonic()

        self.channel.send_msg(
            destination=self._address.to_bytes(),
            payload=MsgId.PING.to_bytes()
        )
        reply = self.channel.read_msg()
        if reply.message_id == MsgId.PING_REPLY and reply.destination == self.channel.addr:
            return time.monotonic() - start
        elif reply.message_id != MsgId.PING_REPLY:
            NetworkError("Invalid reply received ({reply.message_id})")
        else:
            NetworkError("Invalid destination address received ({reply.destination})")


    def exchange(self, payload: bytes) -> None:
        # test if payload is list of uchars
        assert isinstance(payload, bytes)
        self.channel.send_msg(self._address, payload)
        return self.channel.read_msg()
        
    
    def read(self):
        return self.exchange(MsgId.FETCH_MEASUREMENT.bytes)
        

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