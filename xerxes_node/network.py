#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum
import logging
from subprocess import TimeoutExpired
from threading import Lock
from threading import Thread
from typing import List
from xerxes_node.hierarchy.leaf import ChecksumError, LengthError

from xerxes_node.hierarchy.pleaf import PLeaf


class NetworkBusy(Exception):
    pass


class Duplex(Enum):
    HALF = 1
    FULL = 0


class XerxesNetwork:
    def __init__(self, leaves: list, mode: Duplex, std_timeout_s=-1):
        self._leaves = leaves
        self._mode = mode
        self._access_lock = Lock()
        self._std_timeout_s = std_timeout_s
        self._readings = []
        self.log = logging.getLogger(__name__)
        
    def append_leaves(self, leaves: List) -> None:
        assert(isinstance(leaves, list))
        
        self._leaves.append(leaves)

    def _poll(self):
        # if network is read/write exclusive:
        if self._mode == Duplex.HALF:
            lock_acq = self._access_lock.acquire(blocking=True, timeout=self._std_timeout_s)
            if not lock_acq:
                self.log.warning("trying to access busy network")
                raise TimeoutExpired("unable to access network within timeout")

        network_snap = {}
        for i in range(len(self._leaves)):
            leaf = self._leaves[i]
            try:
                leaf_reading = leaf.read()
                network_snap[leaf.address] = leaf_reading
            except LengthError:
                self.log.warning(f"message from leaf {leaf.address} has invalid length")
            except ChecksumError:
                self.log.warning(f"message from leaf {leaf.address} has invalid checksum")
            except TimeoutError:
                self.log.warning(f"Leaf {leaf.address} is not responding.")
        
        self._readings.append(network_snap)

        # release access lock
        if self._mode == Duplex.HALF:
            self._access_lock.release()

    def poll(self) -> None:
        if self._access_lock.locked() and self._mode == Duplex.HALF:
           raise NetworkBusy("Previous command is still in progress")
        poller = Thread(target = self._poll)
        poller.start()

    def busy(self) -> bool:
        return self._access_lock.locked()
        
    def wait(self, timeout=-1):
        locked = self._access_lock.acquire(timeout=timeout)
        self._access_lock.release()
        return locked

    def get(self) -> List:
        # reset counter
        readings = list(self._readings)
        self._readings = []
        return readings
    
    def average(self, flush=True):
        "return the average of aggregated results"
        averages = dict()
        for leaf in self._leaves:
            addr = leaf.address
            leaf_vals = []
            for reading in self._readings:
                leaf_vals.append(reading.get(addr))

            try:    
                averages[addr] = PLeaf.average(leaf_vals)
            except ValueError:
                averages[addr] = None
        
        if flush:
            self._readings=[]

        return averages

