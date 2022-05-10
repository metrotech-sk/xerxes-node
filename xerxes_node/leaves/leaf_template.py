#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from xerxes_node.ids import MsgId

from xerxes_node.network import Addr, XerxesNetwork

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)


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
        try:
            self.channel.send_msg(
                destination=self._address.to_bytes(),
                payload=MsgId.PING.to_bytes()
            )
            reply = self.channel.read_msg()
            return reply.message_id == MsgId.PING_REPLY and reply.destination == self.channel.addr
        except TimeoutError:
            return False
        except IOError:
            return False


    def exchange(self, payload: list) -> None:
        # test if payload is list of uchars
        if isinstance(payload, bytes):
            payload = [b for b in payload]
        else:
            assert(all([isinstance(i, int) for i in payload]))
            assert(all([i<=255 for i in payload]))
            assert(all([i>=0 for i in payload]))

        self.channel.send(self._address, payload)
        try:
            return self.channel.receive(self.std_timeout)
        except X.TimeoutExpired:
            raise TimeoutError("Timeout expired")
        except X.InvalidMessageLength:
            raise IOError("Invalid message received (length)")
        except X.InvalidMessageChecksum:
            raise IOError("Invalid message received (checksum)")
    
    def read(self):
        raise NotImplementedError

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