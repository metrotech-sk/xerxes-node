#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cppyy, os

file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)
cppyy.add_include_path(os.path.join(script_dir, "../../lib/include"))
cppyy.include("exceptions.h")
from cppyy.gbl import Xerxes as X


class Leaf:
    def __init__(self, channel, address: int, std_timeout: float):
        assert(address < 256)
        assert(address > 0)
        assert(isinstance(address, int))
        self._address = address

        self.channel = channel

        assert(std_timeout >= 0)
        self.std_timeout = std_timeout

    def ping(self):
        self.channel.ping(self._address)
        try:
            return self.channel.receive(self.std_timeout)
        except X.TimeoutExpired:
            raise TimeoutError("Timeout expired")
        except X.InvalidMessageLength:
            raise IOError("Invalid message received (length)")
        except X.InvalidMessageChecksum:
            raise IOError("Invalid message received (checksum)")

    def exchange(self, payload: list) -> None:
        # test if payload is list of uchars
        assert(all([i<=255 for i in payload]))
        assert(all([i>=0 for i in payload]))
        assert(all([isinstance(i, int) for i in payload]))

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
        assert("send" in dir(channel))
        assert("ping" in dir(channel))
        assert("receive" in dir(channel))
        self.channel = channel

    def __repr__(self) -> str:
        return f"Leaf(channel={self.channel}, address={self._address}, std_timeout={self.std_timeout})"